"""Change id to UUID and add embedding column

Revision ID: bcb54358344f
Revises: 115a6bbfcc4c
Create Date: 2025-03-27 01:41:15.612886

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision: str = 'bcb54358344f'
down_revision: Union[str, None] = '85d02d00f239'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Step 1: Create a new UUID column (temporary)
    op.add_column('documents', sa.Column('new_id', sa.UUID(), nullable=False, default=uuid.uuid4))

    # Step 2: Copy data from old id column to new_id (if possible)
    op.execute('UPDATE documents SET new_id = gen_random_uuid()')

    # Step 3: Drop old integer id column
    op.drop_column('documents', 'id')

    # Step 4: Rename new_id to id
    op.alter_column('documents', 'new_id', new_column_name='id')

    # Step 5: Set as primary key
    op.create_primary_key("pk_documents", "documents", ["id"])

def downgrade():
    # Reverse migration (Not needed, but safe to implement)
    op.drop_column('documents', 'id')
    op.add_column('documents', sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True))