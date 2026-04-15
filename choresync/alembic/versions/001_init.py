"""Phase 1: initial tables (users, families, family_members, invitations)

Revision ID: 001_init
Revises:
Create Date: 2026-04-12
"""

from alembic import op
import sqlalchemy as sa

revision = "001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "families",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("invite_code", sa.String(20), unique=True, nullable=False),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "family_members",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("family_id", sa.Integer, sa.ForeignKey("families.id"), nullable=False),
        sa.Column(
            "role",
            sa.Enum("Admin", "Member", name="memberrole"),
            nullable=False,
            server_default="Member",
        ),
        sa.Column("family_role", sa.String(20), nullable=False, server_default="기타"),
        sa.Column("age", sa.Integer, nullable=True),
        sa.Column("joined_at", sa.DateTime, nullable=False),
        sa.UniqueConstraint("user_id", "family_id", name="uq_user_family"),
    )
    op.create_index("ix_family_members_family_id", "family_members", ["family_id"])

    op.create_table(
        "invitations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("family_id", sa.Integer, sa.ForeignKey("families.id"), nullable=False),
        sa.Column("code", sa.String(20), unique=True, nullable=False),
        sa.Column("invited_by", sa.Integer, sa.ForeignKey("family_members.id"), nullable=False),
        sa.Column("accepted_by", sa.Integer, sa.ForeignKey("family_members.id"), nullable=True),
        sa.Column(
            "status",
            sa.Enum("Pending", "Accepted", "Expired", name="invitationstatus"),
            nullable=False,
            server_default="Pending",
        ),
        sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_invitations_family_id", "invitations", ["family_id"])


def downgrade():
    op.drop_index("ix_invitations_family_id", "invitations")
    op.drop_table("invitations")
    op.drop_index("ix_family_members_family_id", "family_members")
    op.drop_table("family_members")
    op.drop_table("families")
    op.drop_index("ix_users_email", "users")
    op.drop_table("users")
