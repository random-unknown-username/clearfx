import os
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
