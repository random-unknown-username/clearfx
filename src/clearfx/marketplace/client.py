from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
import httpx

@dataclass
class DesignInfo:
    slug: str
    name: str
    version: str

class MarketplaceClient:
    def __init__(self, base_url: str = "https://marketplace.clearfx.test"):
        self.base_url = base_url
        
    def search(self, query: str, tags: List[str] = None, creator: str = None) -> List[DesignInfo]:
        return []
        
    def download(self, slug: str, version: Optional[str] = None) -> Path:
        return Path(f"/tmp/{slug}.clearfx")
        
    def get_info(self, slug: str) -> DesignInfo:
        return DesignInfo(slug=slug, name=slug, version="1.0.0")
        
    def sync_index(self):
        pass
