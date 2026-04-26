"""add cascade to emprestimos

Revision ID: c149c6b6ed6f
Revises: 14c4a906af5a
Create Date: 2026-04-24

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c149c6b6ed6f'
down_revision: Union[str, Sequence[str], None] = '14c4a906af5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('emprestimo', recreate='always') as batch_op:

        batch_op.create_foreign_key(
            'fk_emprestimo_usuario',
            'usuario',
            ['id_usuario'],
            ['id'],
            ondelete='CASCADE'
        )

        batch_op.create_foreign_key(
            'fk_emprestimo_livro',
            'livros',
            ['id_livro'],
            ['id'],
            ondelete='CASCADE'
        )

def downgrade() -> None:
    with op.batch_alter_table('emprestimo', recreate='always') as batch_op:

        batch_op.create_foreign_key(
            'fk_emprestimo_usuario',
            'usuario',
            ['id_usuario'],
            ['id']
        )

        batch_op.create_foreign_key(
            'fk_emprestimo_livro',
            'livros',
            ['id_livro'],
            ['id']
        )