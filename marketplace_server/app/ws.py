from fastapi import APIRouter, WebSocket, WebSocketDisconnect
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
import fcntl
import struct
import termios
import sys

ws_router = APIRouter()

@ws_router.websocket("/ws/preview/{slug}")
async def websocket_preview(websocket: WebSocket, slug: str, width: int = 80, height: int = 24):
    await websocket.accept()
    
    # Run the clearfx command in a PTY so we capture ANSI output
    pid, fd = pty.fork()
    
    if pid == 0:
        # Child process
        # Set terminal size
        winsize = struct.pack("HHHH", height, width, 0, 0)
        fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSWINSZ, winsize)
        
        # Add the parent src directory to PYTHONPATH
        env = os.environ.copy()
        parent_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
        env["PYTHONPATH"] = f"{parent_src}:{env.get('PYTHONPATH', '')}"
        
        os.execvpe(sys.executable, ["python", "-m", "clearfx.cli.main", "play", slug, "--keep-screen"], env)
    else:
        # Parent process
        try:
            # We want to read from fd asynchronously, but fd is blocking by default
            # Make fd non-blocking
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            loop = asyncio.get_running_loop()
            
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

@ws_router.websocket("/ws/studio")
async def websocket_studio(websocket: WebSocket, width: int = 80, height: int = 24):
    await websocket.accept()
    
    current_pid = None
    current_fd = None
    read_task = None
    
    loop = asyncio.get_running_loop()
    
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
                    winsize = struct.pack("HHHH", height, width, 0, 0)
                    fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSWINSZ, winsize)
                    
                    env = os.environ.copy()
                    parent_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
                    env["PYTHONPATH"] = f"{parent_src}:{env.get('PYTHONPATH', '')}"
                    
                    os.execvpe(sys.executable, ["python", "-m", "clearfx.cli.main", "preview", temp_dir], env)
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
