
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    google_account_email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    timezone: Mapped[str] = mapped_column(
        String(100),
        default="UTC",
        nullable=False,
    )

    auto_archive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    threshold: Mapped[int] = mapped_column(
        Integer,
        default=80,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    emails: Mapped[list["Email"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Email(Base):
    __tablename__ = "emails"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "gmail_id",
            name="uq_emails_user_gmail_id",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    gmail_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    thread_id: Mapped[str | None] = mapped_column(String(255))
    sender: Mapped[str | None] = mapped_column(String(500))
    subject: Mapped[str | None] = mapped_column(String(1000))

    received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    category: Mapped[str | None] = mapped_column(String(50))
    importance_score: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float | None] = mapped_column(Float)
    reason: Mapped[str | None] = mapped_column(Text)
    deadline: Mapped[str | None] = mapped_column(String(255))
    requires_reply: Mapped[bool | None] = mapped_column(Boolean)
    suspicious: Mapped[bool | None] = mapped_column(Boolean)

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="emails")


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    encrypted_refresh_token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    scopes: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    gmail_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)

    rule_ids: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    before_state: Mapped[dict | None] = mapped_column(JSON)
    after_state: Mapped[dict | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    undone_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    email_id: Mapped[int] = mapped_column(
        ForeignKey("emails.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    verdict: Mapped[str] = mapped_column(String(50), nullable=False)
    corrected_category: Mapped[str | None] = mapped_column(String(50))
    note: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Preference(Base):
    __tablename__ = "preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    kind: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    weight: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )


class SenderStat(Base):
    __tablename__ = "sender_stats"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    sender: Mapped[str] = mapped_column(
        String(500),
        primary_key=True,
    )

    message_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    correction_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    last_category: Mapped[str | None] = mapped_column(String(50))
    avg_importance: Mapped[float | None] = mapped_column(Float)


class WatchState(Base):
    __tablename__ = "watch_state"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    history_id: Mapped[str | None] = mapped_column(String(255))

    watch_expiration: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
