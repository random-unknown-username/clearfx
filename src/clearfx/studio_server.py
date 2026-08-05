import asyncio
import os
import pty
import fcntl
import struct
import termios
import sys
import tempfile
import json
import shutil
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from clearfx.core.config import get_data_dir
import importlib.util
import inspect
from clearfx.engine.animation import Animation

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/publish")
async def api_publish(request: Request):
    data = await request.json()
    slug = data.get("slug")
    if not slug:
        return {"success": False, "error": "Missing slug"}
    
    designs_dir = get_data_dir() / "designs" / slug
    designs_dir.mkdir(parents=True, exist_ok=True)
    
    src_dir = designs_dir / "src"
    src_dir.mkdir(exist_ok=True)
    
    code = data.get("code", "")
    (src_dir / "design.py").write_text(code)
    
    manifest = f'''format_version = 1
id = "io.clearfx.community.{slug}"
slug = "{slug}"
name = "{data.get("name", slug)}"
version = "1.0.0"
author_name = "Studio User"
author_handle = "{data.get("author_handle", "@user")}"
description = "{data.get("description", "")}"
entry_scene = "main"
recommended_duration_ms = 3000
'''
    (designs_dir / "manifest.toml").write_text(manifest)
    
    # Compile design.py to design.json
    try:
        spec = importlib.util.spec_from_file_location("dynamic_publish", str(src_dir / "design.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        anim_class = None
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, Animation) and obj is not Animation and obj.__name__ != 'CreatorAnimation':
                anim_class = obj
                break
        if anim_class:
            anim_instance = anim_class()
            design_data = {
                "elements": getattr(anim_instance, "elements", []),
                "keyframes": getattr(anim_instance, "keyframes", [])
            }
            with open(designs_dir / "design.json", "w") as f:
                json.dump(design_data, f)
    except Exception as e:
        print(f"Failed to compile design: {e}")
        return {"success": False, "error": str(e)}
    
    return {"success": True}

@app.get("/api/catalog")
async def api_catalog():
    from clearfx.core.registry import AnimationRegistry
    registry = AnimationRegistry()
    return {"designs": registry.list_animations()}

@app.websocket("/ws/preview/{slug}")
async def websocket_preview(websocket: WebSocket, slug: str, width: int = 80, height: int = 24):
    await websocket.accept()
    
    pid, fd = pty.fork()
    
    if pid == 0:
        winsize = struct.pack("HHHH", height, width, 0, 0)
        fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSWINSZ, winsize)
        
        env = os.environ.copy()
        env["PYTHONPATH"] = "src"
        
        os.execvpe("python", ["python", "-m", "clearfx.cli.main", "play", slug, "--keep-screen", "--loop"], env)
    else:
        try:
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            loop = asyncio.get_event_loop()
            
            while True:
                try:
                    data = await loop.run_in_executor(None, os.read, fd, 4096)
                    if not data:
                        break
                    await websocket.send_text(data.decode("utf-8", errors="replace"))
                except BlockingIOError:
                    await asyncio.sleep(0.01)
                except OSError:
                    break
        except WebSocketDisconnect:
            pass
        finally:
            try:
                os.kill(pid, 9)
                os.waitpid(pid, 0)
            except Exception:
                pass
            os.close(fd)

@app.websocket("/ws/studio")
async def websocket_studio(websocket: WebSocket, width: int = 80, height: int = 24):
    await websocket.accept()
    
    current_pid = None
    current_fd = None
    read_task = None
    
    loop = asyncio.get_event_loop()
    
    temp_dir = tempfile.mkdtemp(prefix="clearfx_studio_")
    
    async def pty_reader(fd):
        try:
            while True:
                try:
                    data = await loop.run_in_executor(None, os.read, fd, 4096)
                    if not data:
                        break
                    await websocket.send_text(data.decode("utf-8", errors="replace"))
                except BlockingIOError:
                    await asyncio.sleep(0.01)
                except OSError:
                    break
        except Exception:
            pass

    try:
        while True:
            # Wait for code from the frontend
            message_text = await websocket.receive_text()
            try:
                message = json.loads(message_text)
            except Exception:
                continue
                
            if message.get("type") == "run":
                code = message.get("code", "")
                req_width = message.get("width", width)
                req_height = message.get("height", height)
                
                # Cleanup previous run
                if current_pid:
                    try:
                        os.kill(current_pid, 9)
                        os.waitpid(current_pid, 0)
                    except Exception:
                        pass
                if current_fd:
                    try:
                        os.close(current_fd)
                    except Exception:
                        pass
                if read_task:
                    read_task.cancel()
                
                # Write project files
                src_dir = Path(temp_dir) / "src"
                src_dir.mkdir(exist_ok=True)
                (src_dir / "design.py").write_text(code)
                
                manifest = '''format_version = 1
id = "io.clearfx.studio.preview"
slug = "studio-preview"
name = "Studio Preview"
version = "1.0.0"
author_name = "Studio User"
author_handle = "@studio"
description = "Live preview"
entry_scene = "main"
recommended_duration_ms = 3000
'''
                (Path(temp_dir) / "manifest.toml").write_text(manifest)
                
                # Fork new PTY
                pid, fd = pty.fork()
                
                if pid == 0:
                    # Child process
                    winsize = struct.pack("HHHH", req_height, req_width, 0, 0)
                    fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSWINSZ, winsize)
                    
                    env = os.environ.copy()
                    env["PYTHONPATH"] = "src"
                    
                    os.execvpe("python", ["python", "-m", "clearfx.cli.main", "preview", temp_dir], env)
                else:
                    # Parent process
                    current_pid = pid
                    current_fd = fd
                    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                    read_task = asyncio.create_task(pty_reader(fd))
                    
    except WebSocketDisconnect:
        pass
    finally:
        if read_task:
            read_task.cancel()
        if current_pid:
            try:
                os.kill(current_pid, 9)
                os.waitpid(current_pid, 0)
            except Exception:
                pass
        if current_fd:
            try:
                os.close(current_fd)
            except Exception:
                pass
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
