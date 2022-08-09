"""create todo table

Revision ID: ad8492b766f6
Revises: 
Create Date: 2021-08-07 09:49:44.567926

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ad8492b766f6"
down_revision = None
branch_labels = None
depends_on = None


# noinspection SqlResolve
after_insert = """
CREATE TRIGGER vimania_todos_ai AFTER INSERT ON vimania_todos
    BEGIN
        INSERT INTO vimania_todos_fts (rowid, parent_id, todo, metadata, "desc", path)
        VALUES (new.id, new.parent_id, new.todo, new.metadata, new.desc, new.path);
    END;
"""

# noinspection SqlResolve
after_delete = """
CREATE TRIGGER vimania_todos_ad AFTER DELETE ON vimania_todos
    BEGIN
        INSERT INTO vimania_todos_fts (vimania_todos_fts, rowid, parent_id, todo, metadata, "desc", path)
        VALUES ('delete', old.id, old.parent_id, old.todo, old.metadata, old.desc, old.path);
    END;
"""

# noinspection SqlResolve
after_update = """
CREATE TRIGGER vimania_todos_au AFTER UPDATE ON vimania_todos
    BEGIN
        INSERT INTO vimania_todos_fts (vimania_todos_fts, rowid, parent_id, todo, metadata, "desc", path)
        VALUES ('delete', old.id, old.parent_id, old.todo, old.metadata, old.desc, old.path);
        INSERT INTO vimania_todos_fts (rowid, parent_id, todo, metadata, "desc", path)
        VALUES (new.id, new.parent_id, new.todo, new.metadata, new.desc, new.path);
    END;
"""

create_fts = """
CREATE VIRTUAL TABLE vimania_todos_fts USING fts5(
    id,
    parent_id UNINDEXED,
    todo,
    metadata,
    tags UNINDEXED,
    "desc",
    "path",
    flags UNINDEXED,
    content='vimania_todos',
    content_rowid='id',
    tokenize="porter unicode61",
);
"""

update_time_trigger = """
CREATE TRIGGER [UpdateLastTime] AFTER UPDATE ON vimania_todos
    FOR EACH ROW WHEN NEW.last_update_ts <= OLD.last_update_ts
    BEGIN
        update vimania_todos set last_update_ts=CURRENT_TIMESTAMP where id=OLD.id;
    END;
"""


def upgrade():
    op.create_table(
        "vimania_todos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("todo", sa.String(), nullable=False, unique=False),
        sa.Column("metadata", sa.String(), default=""),
        sa.Column("tags", sa.String(), default=""),
        sa.Column("desc", sa.String(), default=""),
        sa.Column("path", sa.String(), default=""),
        sa.Column("flags", sa.Integer(), default=0),
        sa.Column(
            "last_update_ts", sa.DateTime(), server_default=sa.func.current_timestamp()
        ),
        sa.Column("created_at", sa.DateTime()),
        sa.ForeignKeyConstraint(
            ("parent_id",),
            ["vimania_todos.id"],
        ),
    )
    op.execute(create_fts)
    op.execute(after_insert)
    op.execute(after_delete)
    op.execute(after_update)
    op.execute(update_time_trigger)


def downgrade():
    op.drop_table("vimania_todos")
