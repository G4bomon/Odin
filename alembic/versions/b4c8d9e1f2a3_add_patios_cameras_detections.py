"""Add patios, cameras and detections tables

Revision ID: b4c8d9e1f2a3
Revises: a3bd7bb970a0
Create Date: 2025-12-09 09:59:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b4c8d9e1f2a3'
down_revision: Union[str, Sequence[str], None] = 'a3bd7bb970a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Crear tabla de patios
    op.create_table(
        'patios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patio_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patios_id'), 'patios', ['id'], unique=False)
    op.create_index(op.f('ix_patios_patio_id'), 'patios', ['patio_id'], unique=True)

    # Crear tabla de cámaras
    op.create_table(
        'cameras',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mac', sa.String(length=17), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=15), nullable=True),
        sa.Column('patio_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_detection', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['patio_id'], ['patios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cameras_id'), 'cameras', ['id'], unique=False)
    op.create_index(op.f('ix_cameras_mac'), 'cameras', ['mac'], unique=True)

    # Crear tabla de detecciones
    op.create_table(
        'detections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patio_id', sa.Integer(), nullable=False),
        sa.Column('camera_id', sa.Integer(), nullable=False),
        sa.Column('image_path', sa.String(length=500), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('detection_type', sa.String(length=50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('objects_detected', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patio_id'], ['patios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_detections_id'), 'detections', ['id'], unique=False)
    op.create_index(op.f('ix_detections_created_at'), 'detections', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar tabla de detecciones
    op.drop_index(op.f('ix_detections_created_at'), table_name='detections')
    op.drop_index(op.f('ix_detections_id'), table_name='detections')
    op.drop_table('detections')

    # Eliminar tabla de cámaras
    op.drop_index(op.f('ix_cameras_mac'), table_name='cameras')
    op.drop_index(op.f('ix_cameras_id'), table_name='cameras')
    op.drop_table('cameras')

    # Eliminar tabla de patios
    op.drop_index(op.f('ix_patios_patio_id'), table_name='patios')
    op.drop_index(op.f('ix_patios_id'), table_name='patios')
    op.drop_table('patios')
