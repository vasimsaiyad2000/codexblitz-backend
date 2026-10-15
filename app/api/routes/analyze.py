
from fastapi import APIRouter, Depends, HTTPException, Request
from openai import APIError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.project import Project
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.llm import generate_blueprint


router = APIRouter(tags=["Analysis"])
settings = get_settings()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
@limiter.limit(f"{settings.analyze_rate_limit_per_minute}/minute")
async def analyze_idea(
    request: Request,
    payload: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    try:
        blueprint = await generate_blueprint(
            idea=payload.idea,
            currency=payload.currency,
        )
    except APIError as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI provider request failed.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI provider returned an invalid response.",
        ) from exc

    project = Project(
        idea=payload.idea,
        currency=payload.currency,
        blueprint=blueprint.model_dump(mode="json"),
    )

    try:
        db.add(project)
        await db.commit()
        await db.refresh(project)
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save the generated project.",
        ) from exc

    return AnalyzeResponse(
        project_id=str(project.id),
        status="completed",
        blueprint=blueprint,
    )
