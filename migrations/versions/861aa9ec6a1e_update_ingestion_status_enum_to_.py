"""Update ingestion_status enum to uppercase

Revision ID: 861aa9ec6a1e
Revises: aca6393d9897
Create Date: 2025-03-27 15:37:19.640589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '861aa9ec6a1e'
down_revision: Union[str, None] = 'aca6393d9897'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enum names should be exactly as stored in the database
old_enum = sa.Enum("pending", "processing", "completed", "failed", name="ingestionstatus")
new_enum = sa.Enum("PENDING", "PROCESSING", "COMPLETED", "FAILED", name="ingestionstatus")

def upgrade():
    # Convert status column to TEXT temporarily
    op.alter_column("documents", "status", type_=sa.String(), existing_type=old_enum)

    # Update all lowercase status values to uppercase
    op.execute("""
        UPDATE documents
        SET status = UPPER(status)
    """)

    # Drop the old enum type
    op.execute("DROP TYPE ingestionstatus")

    # Create new enum with uppercase values
    new_enum.create(op.get_bind())

    # Convert status column back to ENUM, ensuring explicit casting
    op.alter_column("documents", "status", type_=new_enum, existing_type=sa.String(), postgresql_using="status::ingestionstatus")

def downgrade():
    # Convert status column to TEXT temporarily
    op.alter_column("documents", "status", type_=sa.String(), existing_type=new_enum)

    # Revert status values back to lowercase before switching enum
    op.execute("""
        UPDATE documents
        SET status = LOWER(status)
    """)

    # Drop the new enum type
    op.execute("DROP TYPE ingestionstatus")

    # Recreate the old enum type
    old_enum.create(op.get_bind())

    # Convert back to the original enum type using explicit casting
    op.alter_column("documents", "status", type_=old_enum, existing_type=sa.String(), postgresql_using="status::ingestionstatus")
