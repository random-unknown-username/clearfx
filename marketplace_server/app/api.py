from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, desc
from sqlalchemy.orm import joinedload
from typing import List
import json
import io
import zipfile
import re

from .database import get_db
from .models import Design, DesignVersion, Creator, Favorite, Report
from .schemas import DesignResponse, DesignListResponse, VersionResponse, CreatorResponse
from .auth import get_current_creator
from .storage import storage
from .validation import validate_package

api_router = APIRouter()

@api_router.get("/designs", response_model=DesignListResponse)
async def list_designs(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Design).options(joinedload(Design.creator)).order_by(desc(Design.created_at)).offset(skip).limit(limit)
    )
    designs = result.scalars().all()
    count_res = await db.execute(select(Design))
    total = len(count_res.scalars().all())
    return {"items": designs, "total": total}

@api_router.get("/catalog")
async def get_catalog():
    from clearfx.core.registry import AnimationRegistry
    registry = AnimationRegistry()
    anims = registry.list_animations("builtin")
    items = []
    for anim in anims:
        items.append({
            "slug": anim["slug"],
            "name": anim["name"],
            "author": anim["author_handle"] or anim["author_name"] or "ClearFX Built-in",
            "description": anim["description"]
        })
    return {"items": items}

@api_router.get("/designs/{slug}", response_model=DesignResponse)
async def get_design(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Design).options(joinedload(Design.creator)).where(Design.slug == slug))
    design = result.scalars().first()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    return design

@api_router.get("/designs/{slug}/download")
async def download_design(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Design).where(Design.slug == slug))
    design = result.scalars().first()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    
    package_bytes = await storage.retrieve(design.package_hash)
    if not package_bytes:
        raise HTTPException(status_code=404, detail="Package file not found")
        
    design.download_count += 1
    await db.commit()
    
    return Response(content=package_bytes, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={slug}.clearfx"})

@api_router.post("/submissions")
async def submit_design(
    file: UploadFile = File(...),
    creator: Creator = Depends(get_current_creator),
    db: AsyncSession = Depends(get_db)
):
    package_bytes = await file.read()
    is_valid, errors, warnings = validate_package(package_bytes)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"errors": errors, "warnings": warnings})
        
    with zipfile.ZipFile(io.BytesIO(package_bytes)) as zf:
        manifest = json.loads(zf.read("manifest.json").decode('utf-8'))
        
    slug = manifest["id"]
    version = manifest["version"]
    
    if not re.match(r"^[a-zA-Z0-9_-]+$", slug):
        raise HTTPException(status_code=400, detail="Invalid slug format")
        
    result = await db.execute(select(Design).where(Design.slug == slug))
    design = result.scalars().first()
    
    if design:
        if design.creator_id != creator.id:
            raise HTTPException(status_code=403, detail="Design slug already taken by another creator")
        if design.current_version == version:
            raise HTTPException(status_code=400, detail="Version already exists")
    
    hash_hex = await storage.store(package_bytes)
    
    if not design:
        design = Design(
            creator_id=creator.id,
            slug=slug,
            name=manifest["name"],
            description=manifest.get("description", ""),
            current_version=version,
            license=manifest.get("license", "MIT"),
            package_hash=hash_hex,
            package_size=len(package_bytes),
            tags=manifest.get("tags", [])
        )
        db.add(design)
        await db.commit()
        await db.refresh(design)
        
    design_version = DesignVersion(
        design_id=design.id,
        version=version,
        package_hash=hash_hex,
        package_size=len(package_bytes)
    )
    db.add(design_version)
    
    design.current_version = version
    design.package_hash = hash_hex
    design.package_size = len(package_bytes)
    
    await db.commit()
    return {"message": "Design submitted successfully", "slug": slug, "version": version}
