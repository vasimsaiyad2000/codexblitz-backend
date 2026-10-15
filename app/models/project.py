
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"schema": "ai-analyzer"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    idea: Mapped[str] = mapped_column(Text, nullable=False)

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
    )

    blueprint: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
