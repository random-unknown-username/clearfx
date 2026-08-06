importScripts("https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js");

let pyodideReadyPromise = null;

self.postMessageObject = function(msgStr) {
  self.postMessage(JSON.parse(msgStr));
};

async function initPyodide() {
  const pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/",
  });
  
  await pyodide.loadPackage("micropip");
  const micropip = pyodide.pyimport("micropip");
  await micropip.install("platformdirs");
  await micropip.install("wcwidth");
  // Install the wheel we copied to public
  await micropip.install(location.origin + "/clearfx-0.2.9-py3-none-any.whl");

  pyodide.runPython(`
import sys
import time
import js
import json

class WebWorkerStdout:
    def write(self, data):
        js.postMessageObject(json.dumps({"type": "stdout", "data": data}))
    def flush(self):
        pass
    def fileno(self):
        return 1

sys.stdout = WebWorkerStdout()

# Mock terminal session capabilities to bypass termios
from clearfx.engine.terminal import TerminalSession, TerminalCapabilities

class MockTerminalSession(TerminalSession):
    def __init__(self, width=80, height=24):
        self._w = width
        self._h = height
        self._capabilities = TerminalCapabilities(
            width=width, 
            height=height, 
            colors="256color",
            unicode_support=True,
            alternate_screen_support=True,
            title_support=True,
            os_name="web"
        )
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def get_size(self):
        return self._w, self._h
        
    def write(self, data):
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='replace')
        sys.stdout.write(data)
        
    def flush(self):
        pass
        
    def clear(self):
        self.write("\\033[H\\033[2J\\033[3J")
        
    def hide_cursor(self):
        self.write("\\033[?25l")
        
    def show_cursor(self):
        self.write("\\033[?25h")

# Monkey-patch TerminalSession in player
import clearfx.engine.player
clearfx.engine.player.TerminalSession = MockTerminalSession

from clearfx.core.registry import AnimationRegistry
from clearfx.engine.player import AnimationPlayer
import importlib.util

registry = AnimationRegistry()

def play_builtin(slug, width, height):
    anim = registry.get_animation(slug)
    if not anim:
        sys.stdout.write(f"\\r\\nError: Animation '{slug}' not found.\\r\\n")
        return
        
    player = AnimationPlayer(anim, loop=True, config={"clear_after": False})
    # Override the session in the player to use our mock
    session = MockTerminalSession(width, height)
    player._external_session = session
    
    try:
        player.play()
    except Exception as e:
        sys.stdout.write(str(e))

def play_custom(code, width, height):
    import tempfile
    import os
    import inspect
    from clearfx.engine.animation import Animation
    
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write(code)
        temp_path = f.name
        
    try:
        spec = importlib.util.spec_from_file_location("dynamic_anim", temp_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        anim_class = None
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, Animation) and obj is not Animation and obj.__name__ != 'CreatorAnimation':
                anim_class = obj
                break
                
        if anim_class:
            anim = anim_class()
            player = AnimationPlayer(anim, loop=True, config={"clear_after": False})
            session = MockTerminalSession(width, height)
            player._external_session = session
            player.play()
        else:
            sys.stdout.write("Error: Could not find Animation class in code.\\r\\n")
    except Exception as e:
        sys.stdout.write(f"Error compiling: {e}\\r\\n")
    finally:
        os.unlink(temp_path)
`);
  return pyodide;
}

pyodideReadyPromise = initPyodide();

self.onmessage = async (event) => {
  const { type, slug, code, width, height } = event.data;
  
  if (type === "init") {
    await pyodideReadyPromise;
    self.postMessage({ type: "ready" });
  } else if (type === "play") {
    const pyodide = await pyodideReadyPromise;
    if (code) {
      pyodide.globals.set("custom_code", code);
      pyodide.runPython(`play_custom(custom_code, ${width}, ${height})`);
    } else {
      pyodide.runPython(`play_builtin("${slug}", ${width}, ${height})`);
    }
    self.postMessage({ type: "done" });
  }
};
