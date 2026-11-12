
import backend.app.models  # noqa: F401
from backend.app.database import Base


def test_all_eight_tables_are_registered():
    expected_tables = {
        "users",
        "emails",
        "oauth_tokens",
        "actions",
        "feedback",
        "preferences",
        "sender_stats",
        "watch_state",
    }

    assert set(Base.metadata.tables.keys()) == expected_tables


def test_email_has_unique_user_gmail_constraint():
    emails = Base.metadata.tables["emails"]

    unique_constraints = {
        tuple(constraint.columns.keys())
        for constraint in emails.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    assert ("user_id", "gmail_id") in unique_constraints


def test_email_references_users():
    emails = Base.metadata.tables["emails"]

    foreign_keys = {
        foreign_key.target_fullname
        for foreign_key in emails.foreign_keys
    }

    assert "users.id" in foreign_keys


def test_feedback_references_users_and_emails():
    feedback = Base.metadata.tables["feedback"]

    foreign_keys = {
        foreign_key.target_fullname
        for foreign_key in feedback.foreign_keys
    }

    assert "users.id" in foreign_keys
    assert "emails.id" in foreign_keys


def test_sender_stats_has_composite_primary_key():
    sender_stats = Base.metadata.tables["sender_stats"]

    primary_key_columns = tuple(
        column.name for column in sender_stats.primary_key.columns
    )

    assert primary_key_columns == ("user_id", "sender")


def test_watch_state_uses_user_id_as_primary_key():
    watch_state = Base.metadata.tables["watch_state"]

    primary_key_columns = tuple(
        column.name for column in watch_state.primary_key.columns
    )

    assert primary_key_columns == ("user_id",)


def test_email_body_is_not_stored():
    emails = Base.metadata.tables["emails"]

    assert "body" not in emails.columns
    assert "email_body" not in emails.columns
