from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, or_
from .database import get_db
from .models import Design, Creator

web_router = APIRouter()
templates = Jinja2Templates(directory="templates")

@web_router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Design).options(joinedload(Design.creator)).order_by(desc(Design.download_count)).limit(6)
    )
    featured = result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "featured": featured})

@web_router.get("/browse", response_class=HTMLResponse)
async def browse(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Design).options(joinedload(Design.creator)).order_by(desc(Design.created_at)).limit(20)
    )
    designs = result.scalars().all()
    return templates.TemplateResponse("browse.html", {"request": request, "designs": designs})

@web_router.get("/design/{slug}", response_class=HTMLResponse)
async def design_detail(request: Request, slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Design).options(joinedload(Design.creator)).where(Design.slug == slug))
    design = result.scalars().first()
    if not design:
        return HTMLResponse("Design not found", status_code=404)
    return templates.TemplateResponse("design_detail.html", {"request": request, "design": design})

@web_router.get("/creator/{handle}", response_class=HTMLResponse)
async def creator_profile(request: Request, handle: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Creator).where(Creator.handle == handle))
    creator = result.scalars().first()
    if not creator:
        return HTMLResponse("Creator not found", status_code=404)
        
    designs_res = await db.execute(select(Design).where(Design.creator_id == creator.id).order_by(desc(Design.created_at)))
    designs = designs_res.scalars().all()
    return templates.TemplateResponse("creator.html", {"request": request, "creator": creator, "designs": designs})

@web_router.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = "", db: AsyncSession = Depends(get_db)):
    designs = []
    if q:
        result = await db.execute(
            select(Design).options(joinedload(Design.creator)).where(
                or_(Design.name.ilike(f"%{q}%"), Design.description.ilike(f"%{q}%"))
            ).limit(20)
        )
        designs = result.scalars().all()
    return templates.TemplateResponse("search.html", {"request": request, "designs": designs, "q": q})

@web_router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})
