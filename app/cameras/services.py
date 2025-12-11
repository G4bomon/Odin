from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Update, Delete, And_
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from app.cameras.models import Camera
from app.cameras.schemas import CameraCreate, CameraUpdate
from app.database import get_async_session
from fastapi import Depends, HTTPException, status

async def _get_active_by_mac(session: AsyncSession, mac: str) -> Optional[Camera]:
    q = select(Camera).where(Camera.mac == mac, Camera.deleted_at.is_(None))
    res = await session.execute(q)
    return res.scalars().first()

async def _get_active_by_ip(session: AsyncSession, ip: str) -> Optional[Camera]:
    q = select(Camera).where(Camera.ip == ip, Camera.deleted_at.is_(None))
    res = await session.execute(q)
    return res.scalars().first()

async def get_camera(session: AsyncSession = Depends(get_async_session), camera_id: int = None) -> Optional[Camera]:
    q = select(Camera).where(Camera.id == camera_id)
    res = await session.execute(q)
    return res.scalars().first()

async def list_cameras(session: AsyncSession = Depends(get_async_session), include_deleted: bool = False, skip: int = 0, limit: int = 100) -> List[Camera]:
    q = select(Camera)
    if not include_deleted:
        q = q.where(Camera.deleted_at.is_(None))
    q = q.offset(skip).limit(limit)
    res = await session.execute(q)
    return res.scalars().all()

async def create_camera(data: CameraCreate, session: AsyncSession = Depends(get_async_session)) -> Camera:
    # Normalizaciones ya hechas en Schema (mac uppercase, ip validada)
    # Chequear unicidad
    existing_mac = await _get_active_by_mac(session, data.mac)
    if existing_mac:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una cámara activa con esa MAC")

    existing_ip = await _get_active_by_ip(session, data.ip)
    if existing_ip:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una cámara activa con esa IP")

    new = Camera(
        ip=data.ip,
        puerto=data.puerto,
        orientacion=data.orientacion,
        mac=data.mac,
        patio_id=data.patio_id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
        deleted_at=None
    )
    session.add(new)
    await session.commit()
    await session.refresh(new)
    return new

async def update_camera(camera_id: int, data: CameraUpdate, session: AsyncSession = Depends(get_async_session)) -> Camera:
    camera = await get_camera(session=session, camera_id=camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cámara no encontrada")

    # Si se actualiza MAC/IP validar unicidad con otras cámaras activas
    if data.mac and data.mac != camera.mac:
        existing = await _get_active_by_mac(session, data.mac)
        if existing and existing.id != camera.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Otra cámara activa usa esa MAC")

    if data.ip and data.ip != camera.ip:
        existing = await _get_active_by_ip(session, data.ip)
        if existing and existing.id != camera.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Otra cámara activa usa esa IP")

    # Aplicar cambios
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(camera, field, value)
    camera.updated_at = datetime.datetime.utcnow()
    session.add(camera)
    await session.commit()
    await session.refresh(camera)
    return camera

async def soft_delete_camera(camera_id: int, session: AsyncSession = Depends(get_async_session)) -> Camera:
    camera = await get_camera(session=session, camera_id=camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cámara no encontrada")
    if camera.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cámara ya está eliminada")
    camera.deleted_at = datetime.datetime.utcnow()
    session.add(camera)
    await session.commit()
    await session.refresh(camera)
    return camera

async def restore_camera(camera_id: int, session: AsyncSession = Depends(get_async_session)) -> Camera:
    camera = await get_camera(session=session, camera_id=camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cámara no encontrada")
    if camera.deleted_at is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cámara no está eliminada")
    # Antes de restaurar, chequear unicidad de ip/mac con otras activas
    if await _get_active_by_mac(session, camera.mac):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede restaurar: otra cámara activa tiene la misma MAC")
    if await _get_active_by_ip(session, camera.ip):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede restaurar: otra cámara activa tiene la misma IP")

    camera.deleted_at = None
    camera.updated_at = datetime.datetime.utcnow()
    session.add(camera)
    await session.commit()
    await session.refresh(camera)
    return camera
