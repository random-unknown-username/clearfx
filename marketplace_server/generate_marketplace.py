import os

base_dir = "/home/satvik/Projects/ragebaitGPT/marketplace_server"
app_dir = os.path.join(base_dir, "app")
templates_dir = os.path.join(base_dir, "templates")
static_dir = os.path.join(base_dir, "static")

os.makedirs(app_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(base_dir, "data"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "packages"), exist_ok=True)

files = {}

files["requirements.txt"] = """fastapi>=0.100.0
uvicorn>=0.23.0
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
pydantic>=2.0.0
jinja2>=3.1.2
python-multipart>=0.0.6
aiofiles>=23.1.0
passlib>=1.7.4
bcrypt>=4.0.1
"""

files["run.py"] = """import uvicorn
import os

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("packages", exist_ok=True)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
"""

files["app/__init__.py"] = ""

files["app/database.py"] = """import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

DB_PATH = os.getenv("DB_PATH", "sqlite+aiosqlite:///data/marketplace.db")
engine = create_async_engine(DB_PATH, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
"""

files["app/models.py"] = """import datetime
import enum
from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from .database import Base

class DesignStatus(str, enum.Enum):
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"
    quarantined = "quarantined"

class Creator(Base):
    __tablename__ = "creators"
    id = Column(Integer, primary_key=True, index=True)
    handle = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String)
    email = Column(String, unique=True, index=True)
    bio = Column(Text)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    api_key_hash = Column(String, nullable=False)

    designs = relationship("Design", back_populates="creator")

class Design(Base):
    __tablename__ = "designs"
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creators.id"))
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    current_version = Column(String, nullable=False)
    license = Column(String)
    tags = Column(JSON)
    min_width = Column(Integer)
    min_height = Column(Integer)
    supports_ascii = Column(Boolean, default=False)
    supports_monochrome = Column(Boolean, default=False)
    recommended_duration_ms = Column(Integer)
    download_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    report_count = Column(Integer, default=0)
    status = Column(String, default=DesignStatus.submitted.value)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    package_hash = Column(String, nullable=False)
    package_size = Column(Integer, nullable=False)

    creator = relationship("Creator", back_populates="designs")
    versions = relationship("DesignVersion", back_populates="design")

class DesignVersion(Base):
    __tablename__ = "design_versions"
    id = Column(Integer, primary_key=True, index=True)
    design_id = Column(Integer, ForeignKey("designs.id"))
    version = Column(String, nullable=False)
    package_hash = Column(String, nullable=False)
    package_size = Column(Integer, nullable=False)
    changelog = Column(Text)
    status = Column(String, default=DesignStatus.submitted.value)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    design = relationship("Design", back_populates="versions")

class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, index=True)
    design_id = Column(Integer, ForeignKey("designs.id"))
    user_ip = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    design_id = Column(Integer, ForeignKey("designs.id"))
    reason = Column(String, nullable=False)
    reporter_ip = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
"""

files["app/schemas.py"] = """from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import datetime

class CreatorResponse(BaseModel):
    handle: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool
    model_config = ConfigDict(from_attributes=True)

class DesignBase(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    license: Optional[str] = None
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    supports_ascii: bool = False
    supports_monochrome: bool = False
    recommended_duration_ms: Optional[int] = None

class DesignResponse(DesignBase):
    slug: str
    current_version: str
    download_count: int
    favorite_count: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    creator: Optional[CreatorResponse] = None
    model_config = ConfigDict(from_attributes=True)

class DesignListResponse(BaseModel):
    items: List[DesignResponse]
    total: int

class VersionResponse(BaseModel):
    version: str
    changelog: Optional[str] = None
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class ValidationResultResponse(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]
"""

files["app/storage.py"] = """import os
import hashlib
import aiofiles
from typing import Optional

class ContentAddressedStorage:
    def __init__(self, base_dir: str = "packages"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        
    def _get_path(self, hash_hex: str) -> str:
        return os.path.join(self.base_dir, hash_hex)

    async def store(self, package_bytes: bytes) -> str:
        hash_hex = hashlib.sha256(package_bytes).hexdigest()
        path = self._get_path(hash_hex)
        if not os.path.exists(path):
            async with aiofiles.open(path, 'wb') as f:
                await f.write(package_bytes)
        return hash_hex

    async def retrieve(self, hash_hex: str) -> Optional[bytes]:
        path = self._get_path(hash_hex)
        if os.path.exists(path):
            async with aiofiles.open(path, 'rb') as f:
                return await f.read()
        return None

    def exists(self, hash_hex: str) -> bool:
        return os.path.exists(self._get_path(hash_hex))
        
storage = ContentAddressedStorage()
"""

files["app/validation.py"] = """import json
import zipfile
import io
from typing import Tuple

def validate_package(package_bytes: bytes) -> Tuple[bool, list, list]:
    errors = []
    warnings = []
    
    if len(package_bytes) > 10 * 1024 * 1024:
        errors.append("Package size exceeds 10MB limit.")
        return False, errors, warnings
        
    try:
        with zipfile.ZipFile(io.BytesIO(package_bytes)) as zf:
            files = zf.namelist()
            if "manifest.json" not in files:
                errors.append("Missing manifest.json in package.")
                return False, errors, warnings
                
            manifest_bytes = zf.read("manifest.json")
            try:
                manifest = json.loads(manifest_bytes.decode('utf-8'))
            except json.JSONDecodeError:
                errors.append("Invalid JSON in manifest.json.")
                return False, errors, warnings
                
            required_keys = ["id", "name", "version", "author"]
            for key in required_keys:
                if key not in manifest:
                    errors.append(f"Missing required key in manifest: {key}")
                    
    except zipfile.BadZipFile:
        errors.append("Invalid zip file format.")
        
    return len(errors) == 0, errors, warnings
"""

files["app/auth.py"] = """import secrets
from passlib.context import CryptContext
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Header, HTTPException, Depends
from .models import Creator
from .database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_api_key(api_key: str) -> str:
    return pwd_context.hash(api_key)

def verify_api_key_hash(plain_api_key: str, hashed_api_key: str) -> bool:
    return pwd_context.verify(plain_api_key, hashed_api_key)

def generate_api_key() -> str:
    return "cfx_" + secrets.token_urlsafe(32)

async def get_current_creator(x_api_key: str = Header(None), db: AsyncSession = Depends(get_db)) -> Creator:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key missing")
        
    result = await db.execute(select(Creator))
    creators = result.scalars().all()
    for creator in creators:
        if verify_api_key_hash(x_api_key, creator.api_key_hash):
            return creator
            
    raise HTTPException(status_code=401, detail="Invalid API Key")
"""

files["app/api.py"] = """from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query, Request
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
"""

files["app/web.py"] = """from fastapi import APIRouter, Depends, Request, Form
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
"""

files["app/main.py"] = """from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from .api import api_router
from .web import web_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="ClearFX Marketplace", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix="/api/v1")
app.include_router(web_router)
"""

files["templates/base.html"] = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClearFX Marketplace</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="/" class="logo">ClearFX Marketplace</a>
            <div class="nav-links">
                <a href="/browse">Browse</a>
                <a href="/upload">Upload</a>
                <form action="/search" method="get" class="search-form">
                    <input type="text" name="q" placeholder="Search designs..." value="{{ q | default('') }}">
                </form>
            </div>
        </div>
    </nav>
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    <footer>
        <div class="container">
            <p>&copy; 2024 ClearFX</p>
        </div>
    </footer>
    <script src="/static/main.js"></script>
</body>
</html>
"""

files["templates/index.html"] = """{% extends "base.html" %}
{% block content %}
<div class="hero">
    <h1>Discover ClearFX Designs</h1>
    <p>Find the best visual effects for your terminal and stream.</p>
</div>
<h2>Featured Designs</h2>
<div class="grid">
    {% for design in featured %}
    <div class="card">
        <h3><a href="/design/{{ design.slug }}">{{ design.name }}</a></h3>
        <p class="author">by <a href="/creator/{{ design.creator.handle }}">{{ design.creator.handle }}</a></p>
        <p class="desc">{{ design.description }}</p>
        <div class="stats">
            <span>↓ {{ design.download_count }}</span>
            <span>★ {{ design.favorite_count }}</span>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

files["templates/browse.html"] = """{% extends "base.html" %}
{% block content %}
<h2>All Designs</h2>
<div class="grid">
    {% for design in designs %}
    <div class="card">
        <h3><a href="/design/{{ design.slug }}">{{ design.name }}</a></h3>
        <p class="author">by <a href="/creator/{{ design.creator.handle }}">{{ design.creator.handle }}</a></p>
        <p class="desc">{{ design.description }}</p>
        <div class="stats">
            <span>↓ {{ design.download_count }}</span>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

files["templates/design_detail.html"] = """{% extends "base.html" %}
{% block content %}
<div class="design-detail">
    <div class="header">
        <h1>{{ design.name }} <span class="version">v{{ design.current_version }}</span></h1>
        <p class="author">by <a href="/creator/{{ design.creator.handle }}">{{ design.creator.handle }}</a></p>
    </div>
    <div class="content">
        <p class="desc">{{ design.description }}</p>
        
        <div class="install-box">
            <h3>Install Command</h3>
            <code>clearfx install {{ design.slug }}</code>
        </div>
        
        <div class="meta">
            <p><strong>License:</strong> {{ design.license }}</p>
            <p><strong>Downloads:</strong> {{ design.download_count }}</p>
            <p><strong>Tags:</strong> 
                {% if design.tags %}
                    {{ design.tags | join(', ') }}
                {% else %}
                    None
                {% endif %}
            </p>
            <a href="/api/v1/designs/{{ design.slug }}/download" class="btn">Download Package</a>
        </div>
    </div>
</div>
{% endblock %}
"""

files["templates/creator.html"] = """{% extends "base.html" %}
{% block content %}
<div class="creator-profile">
    <h1>{{ creator.display_name or creator.handle }}</h1>
    <p class="bio">{{ creator.bio }}</p>
</div>
<h2>Designs by {{ creator.handle }}</h2>
<div class="grid">
    {% for design in designs %}
    <div class="card">
        <h3><a href="/design/{{ design.slug }}">{{ design.name }}</a></h3>
        <p class="desc">{{ design.description }}</p>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

files["templates/upload.html"] = """{% extends "base.html" %}
{% block content %}
<div class="upload-form">
    <h2>Upload Design</h2>
    <p>Upload your .clearfx package here. You must authenticate via the CLI to publish packages, but this form acts as a placeholder for Web-UI uploads if authentication is integrated in the future.</p>
    <p class="warning">For MVP, please use the <code>clearfx publish</code> command line tool.</p>
    <form action="/api/v1/submissions" method="post" enctype="multipart/form-data">
        <div class="form-group">
            <label for="file">Package (.clearfx)</label>
            <input type="file" name="file" accept=".clearfx,.zip" required>
        </div>
        <div class="form-group">
            <label for="api_key">API Key</label>
            <input type="password" name="x-api-key" placeholder="cfx_..." required>
        </div>
        <button type="submit" class="btn" disabled>Upload (Use CLI)</button>
    </form>
</div>
{% endblock %}
"""

files["templates/search.html"] = """{% extends "base.html" %}
{% block content %}
<h2>Search Results for "{{ q }}"</h2>
{% if designs %}
<div class="grid">
    {% for design in designs %}
    <div class="card">
        <h3><a href="/design/{{ design.slug }}">{{ design.name }}</a></h3>
        <p class="author">by <a href="/creator/{{ design.creator.handle }}">{{ design.creator.handle }}</a></p>
        <p class="desc">{{ design.description }}</p>
    </div>
    {% endfor %}
</div>
{% else %}
<p>No results found.</p>
{% endif %}
{% endblock %}
"""

files["static/style.css"] = """
:root {
    --bg: #121212;
    --fg: #ffffff;
    --card-bg: #1e1e1e;
    --primary: #bb86fc;
    --primary-hover: #9965d6;
    --border: #333;
}

body {
    background-color: var(--bg);
    color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    margin: 0;
    padding: 0;
    line-height: 1.6;
}

a {
    color: var(--primary);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.navbar {
    background-color: var(--card-bg);
    padding: 1rem 0;
    border-bottom: 1px solid var(--border);
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--fg);
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 20px;
}

.search-form input {
    padding: 0.5rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    background: var(--bg);
    color: var(--fg);
}

main {
    padding: 2rem 0;
    min-height: 80vh;
}

.hero {
    text-align: center;
    padding: 4rem 0;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

.card {
    background-color: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    transition: transform 0.2s;
}

.card:hover {
    transform: translateY(-5px);
}

.card h3 {
    margin-top: 0;
    margin-bottom: 5px;
}

.author {
    color: #888;
    font-size: 0.9rem;
    margin-top: 0;
}

.stats {
    display: flex;
    gap: 15px;
    color: #aaa;
    font-size: 0.9rem;
    margin-top: 15px;
}

.install-box {
    background: #000;
    padding: 15px;
    border-radius: 6px;
    border: 1px solid var(--border);
    margin: 20px 0;
}

.install-box code {
    color: #4ade80;
    font-family: monospace;
    font-size: 1.1rem;
}

.btn {
    display: inline-block;
    background: var(--primary);
    color: #000;
    padding: 10px 20px;
    border-radius: 4px;
    font-weight: bold;
}
.btn:hover {
    background: var(--primary-hover);
    text-decoration: none;
}
"""

files["static/main.js"] = """
console.log("ClearFX Marketplace loaded");
"""


for filename, content in files.items():
    filepath = os.path.join(base_dir, filename)
    with open(filepath, "w") as f:
        f.write(content)

print("Marketplace generation complete!")
