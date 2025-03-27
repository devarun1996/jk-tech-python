"""Update IngestionStatus Enum values

Revision ID: 31d59729d505
Revises: 8d7fa037fcd1
Create Date: 2025-03-27 14:57:49.812457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '31d59729d505'
down_revision: Union[str, None] = '8d7fa037fcd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define the old and new ENUM types
old_enum = ENUM("Pending", "Processing", "Completed", "Failed", name="ingestionstatus", create_type=False)
new_enum = ENUM("pending", "processing", "completed", "failed", name="ingestionstatus", create_type=False)

def upgrade():
    # Step 1: Rename the old enum type
    op.execute("ALTER TYPE ingestionstatus RENAME TO ingestionstatus_old;")

    # Step 2: Create the new enum type
    new_enum.create(op.get_bind())

    # Step 3: Temporarily cast the status column to TEXT
    op.execute("ALTER TABLE documents ALTER COLUMN status TYPE TEXT;")

    # Step 4: Convert values from old to new format
    op.execute("""
        UPDATE documents
        SET status = 
            CASE 
                WHEN status = 'Pending' THEN 'pending'
                WHEN status = 'Processing' THEN 'processing'
                WHEN status = 'Completed' THEN 'completed'
                WHEN status = 'Failed' THEN 'failed'
                ELSE status
            END;
    """)

    # Step 5: Change the column type to the new ENUM
    op.execute("ALTER TABLE documents ALTER COLUMN status TYPE ingestionstatus USING status::ingestionstatus;")

    # Step 6: Drop the old ENUM type
    op.execute("DROP TYPE ingestionstatus_old;")

def downgrade():
    # Step 1: Recreate the old enum type
    old_enum.create(op.get_bind())

    # Step 2: Temporarily cast the status column to TEXT
    op.execute("ALTER TABLE documents ALTER COLUMN status TYPE TEXT;")

    # Step 3: Convert values back to old format
    op.execute("""
        UPDATE documents
        SET status = 
            CASE 
                WHEN status = 'pending' THEN 'Pending'
                WHEN status = 'processing' THEN 'Processing'
                WHEN status = 'completed' THEN 'Completed'
                WHEN status = 'failed' THEN 'Failed'
                ELSE status
            END;
    """)

    # Step 4: Change the column type back to the old ENUM
    op.execute("ALTER TABLE documents ALTER COLUMN status TYPE ingestionstatus_old USING status::ingestionstatus_old;")

    # Step 5: Drop the new ENUM type
    op.execute("DROP TYPE ingestionstatus;")

    # Step 6: Rename old enum back to original name
    op.execute("ALTER TYPE ingestionstatus_old RENAME TO ingestionstatus;")
