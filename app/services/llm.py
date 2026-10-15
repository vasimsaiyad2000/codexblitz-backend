
import json
import logging

from openai import AsyncOpenAI
from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.analysis import ProductBlueprint

logger = logging.getLogger(__name__)
settings = get_settings()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
    timeout=90.0,
    max_retries=2,
)


SUPPORTED_TECH_STACK = {
    "frontend_web": {
        "frameworks": [
            "React", "Next.js", "Vue.js", "Angular"
        ],
        "styling": [
            "Tailwind CSS", "Bootstrap", "Material UI", "shadcn/ui"
        ],
        "state_management": [
            "Redux", "Zustand", "TanStack Query", "Pinia"
        ],
    },
    "mobile": {
        "cross_platform": ["Flutter", "React Native"],
        "android": ["Kotlin", "Jetpack Compose"],
        "ios": ["Swift", "SwiftUI"],
    },
    "backend": {
        "languages": [
            "Node.js", "TypeScript", "Python", "Java", "Go", "PHP"
        ],
        "frameworks": [
            "Express.js", "NestJS", "FastAPI", "Django",
            "Spring Boot", "Laravel"
        ],
        "apis": ["REST", "GraphQL", "gRPC", "WebSockets"],
    },
    "databases": {
        "sql": ["PostgreSQL", "MySQL", "SQLite"],
        "nosql": ["MongoDB", "DynamoDB"],
        "caching_vector": ["Redis", "pgvector"],
    },
    "devops": {
        "cloud": ["AWS", "Azure", "Vercel"],
        "containers": ["Docker", "Kubernetes"],
        "cicd_iac": ["GitHub Actions", "GitLab CI", "Terraform"],
    },
}

def build_system_prompt() -> str:
    catalog = json.dumps(
        SUPPORTED_TECH_STACK,
        separators=(",", ":"),
    )

    return f"""
You are an AI business analyst and software architect.

Generate a complete, concise product blueprint matching the supplied schema.

Supported technology catalog:
{catalog}

Include:
- Problem, users, value proposition
- MVP features and user flows
- Recommended technology stack
- Development phases and budget friendly estimates
- Dashboard prototype specification
- Key business risks and validation steps, if requested

Limits:
- 5 features maximum
- 2 user flows maximum
- 5 assumptions maximum per section
- Keep descriptions to 1-2 sentences
- Use realistic estimates and state uncertainty
- Never present unsupported claims as verified facts
- Return JSON only.

Technology selection rules:
- Recommend technologies only from the catalog above.
- Choose technologies appropriate for the business idea.
- Select one primary framework per category unless multiple are justified.
- Keep the stack practical and avoid unnecessary technologies.
- Select compatible frontend and state-management technologies.
- Match backend frameworks to supported languages.
- Recommend mobile technologies only if a mobile app is needed.
- Do not invent technologies or return unsupported alternatives.
- Explain the reason for each major selection.
- If a category is unnecessary, represent that according to the schema.
- Return valid JSON only, with exact schema field names and types.

"""

async def generate_blueprint(
    idea: str,
    currency: str,
) -> ProductBlueprint:

    catalog = json.dumps(
        SUPPORTED_TECH_STACK,
        separators=(",", ":"),
    )

    schema = ProductBlueprint.model_json_schema()
    response = await client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {
                "role": "system",
                "content": build_system_prompt(),
            },
            {
                "role": "user",
                "content": (
                    f"Business idea:\n{idea}\n\n"
                    f"Currency: {currency}\n\n"
                    "Required output schema:\n"
                    f"{json.dumps(schema, indent=2)}\n\n"
                    "Generate a complete blueprint instance. "
                    "Do not return the schema definition."
                ),
            },
        ],
        response_format={"type": "json_object"},
        max_tokens=3500,
        temperature=0.2,
    )

    choice = response.choices[0]
    content = choice.message.content

    logger.info("Model finish reason: %s", choice.finish_reason)

    if not content:
        raise ValueError("The model returned empty content")

    try:
        data = json.loads(content)
        return ProductBlueprint.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.exception("Blueprint JSON validation failed")
        raise ValueError(
            "The model returned a blueprint that does not match the schema"
        ) from exc
