"""Rename patios to ubicaciones and add orientacion to cameras

Revision ID: c5d9e2f3g4h5
Revises: b4c8d9e1f2a3
Create Date: 2025-12-09 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c5d9e2f3g4h5'
down_revision: Union[str, Sequence[str], None] = 'b4c8d9e1f2a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Renombrar tabla patios a ubicaciones
    op.rename_table('patios', 'ubicaciones')
    
    # Renombrar índices de patios
    op.execute('ALTER INDEX ix_patios_id RENAME TO ix_ubicaciones_id')
    op.execute('ALTER INDEX ix_patios_patio_id RENAME TO ix_ubicaciones_ubicacion_id')
    
    # Renombrar columna patio_id a ubicacion_id en tabla ubicaciones
    op.alter_column('ubicaciones', 'patio_id', new_column_name='ubicacion_id')
    
    # Agregar columna orientacion a cameras
    op.add_column('cameras', sa.Column('orientacion', sa.String(length=100), nullable=True))
    
    # Renombrar columna patio_id a ubicacion_id en cameras
    op.alter_column('cameras', 'patio_id', new_column_name='ubicacion_id')
    
    # Renombrar columna patio_id a ubicacion_id en detections
    op.alter_column('detections', 'patio_id', new_column_name='ubicacion_id')


def downgrade() -> None:
    """Downgrade schema."""
    # Renombrar columna ubicacion_id a patio_id en detections
    op.alter_column('detections', 'ubicacion_id', new_column_name='patio_id')
    
    # Renombrar columna ubicacion_id a patio_id en cameras
    op.alter_column('cameras', 'ubicacion_id', new_column_name='patio_id')
    
    # Eliminar columna orientacion de cameras
    op.drop_column('cameras', 'orientacion')
    
    # Renombrar columna ubicacion_id a patio_id en tabla ubicaciones
    op.alter_column('ubicaciones', 'ubicacion_id', new_column_name='patio_id')
    
    # Renombrar índices de ubicaciones
    op.execute('ALTER INDEX ix_ubicaciones_ubicacion_id RENAME TO ix_patios_patio_id')
    op.execute('ALTER INDEX ix_ubicaciones_id RENAME TO ix_patios_id')
    
    # Renombrar tabla ubicaciones a patios
    op.rename_table('ubicaciones', 'patios')
