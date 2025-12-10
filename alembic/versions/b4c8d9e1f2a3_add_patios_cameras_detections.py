"""Create initial schema: locations, cameras, detections

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
    
    # 1. Crear tabla de LOCATIONS (Ya con el campo address, sin pasos intermedios)
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.String(length=50), nullable=False), # El código identificador
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('address', sa.String(length=200), nullable=True), # <-- AQUÍ CAMBIAMOS location POR address
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locations_id'), 'locations', ['id'], unique=False)
    op.create_index(op.f('ix_locations_location_id'), 'locations', ['location_id'], unique=True)

    # 2. Crear tabla de CAMERAS (Ya con el campo orientacion)
    op.create_table(
        'cameras',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mac', sa.String(length=17), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=15), nullable=True),
        sa.Column('orientacion', sa.String(length=100), nullable=True), # <-- AQUÍ AGREGAMOS LO QUE FALTABA
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_detection', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cameras_id'), 'cameras', ['id'], unique=False)
    op.create_index(op.f('ix_cameras_mac'), 'cameras', ['mac'], unique=True)

    # 3. Crear tabla de DETECTIONS
    op.create_table(
        'detections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('camera_id', sa.Integer(), nullable=False),
        sa.Column('image_path', sa.String(length=500), nullable=False),
        sa.Column('detection_type', sa.String(length=50), nullable=True),
        sa.Column('objects_detected', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_detections_id'), 'detections', ['id'], unique=False)
    op.create_index(op.f('ix_detections_created_at'), 'detections', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # El orden inverso para borrar
    op.drop_index(op.f('ix_detections_created_at'), table_name='detections')
    op.drop_index(op.f('ix_detections_id'), table_name='detections')
    op.drop_table('detections')

    op.drop_index(op.f('ix_cameras_mac'), table_name='cameras')
    op.drop_index(op.f('ix_cameras_id'), table_name='cameras')
    op.drop_table('cameras')

    op.drop_index(op.f('ix_locations_location_id'), table_name='locations')
    op.drop_index(op.f('ix_locations_id'), table_name='locations')
    op.drop_table('locations')