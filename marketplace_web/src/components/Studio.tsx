import { useEffect, useRef, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { Play } from 'lucide-react';

const DEFAULT_CODE = `"""Custom ClearFX animation."""
from clearfx.compiler.creator_sdk import CreatorAnimation

class MyAnimation(CreatorAnimation):
    def design(self) -> None:
        """Define your animation here."""
        # Add a text element
        self.add_text(
            text="Hello from the Web Studio!",
            x="w/2 - 12",
            y="h/2",
            fg=(255, 255, 255),
            bold=True
        )

        # Add a simple transition
        self.set_keyframe(
            target="text_0",
            property="opacity",
            time=0.0,
            value=0.0,
        )
        self.set_keyframe(
            target="text_0",
            property="opacity",
            time=0.5,
            value=1.0,
        )
        self.set_keyframe(
            target="text_0",
            property="opacity",
            time=1.0,
            value=0.0,
        )
`;

export function Studio() {
  const terminalRef = useRef<HTMLDivElement>(null);
  const [code, setCode] = useState(DEFAULT_CODE);
  const wsRef = useRef<WebSocket | null>(null);
  const termRef = useRef<Terminal | null>(null);

  useEffect(() => {
    if (!terminalRef.current) return;

    const term = new Terminal({
      theme: {
        background: '#09090b',
        foreground: '#fafafa',
        cursor: 'transparent',
      },
      fontFamily: 'JetBrains Mono, Menlo, monospace',
      fontSize: 14,
      allowProposedApi: true,
      disableStdin: true,
    });
    
    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    
    term.open(terminalRef.current);
    fitAddon.fit();
    termRef.current = term;

    const wsUrl = `ws://localhost:8000/ws/studio`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      term.writeln('\\x1b[32mStudio connection established. Click "Run Animation" to preview.\\x1b[0m');
    };

    ws.onmessage = (event) => {
      term.write(event.data);
    };

    const handleResize = () => {
      fitAddon.fit();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      ws.close();
      term.dispose();
    };
  }, []);

  const handleRun = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      if (termRef.current) {
        termRef.current.clear();
      }
      wsRef.current.send(JSON.stringify({ type: 'run', code }));
    }
  };

  return (
    <div className="studio-layout">
      <div className="editor-pane">
        <div className="editor-header">
          <h3>design.py</h3>
          <button className="run-button" onClick={handleRun}>
            <Play size={16} fill="currentColor" /> Run Animation
          </button>
        </div>
        <textarea 
          className="code-editor"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          spellCheck={false}
        />
      </div>

      <div className="preview-pane">
        <div className="terminal-display-area" style={{ height: '100%' }}>
          <div className="terminal-window-decor">
            <div className="mac-buttons">
              <span className="close"></span>
              <span className="minimize"></span>
              <span className="maximize"></span>
            </div>
            <div className="terminal-title">~ clearfx preview</div>
          </div>
          <div className="terminal-wrapper">
            <div ref={terminalRef} className="terminal-element" style={{ width: '100%', height: '100%' }} />
          </div>
        </div>
      </div>
    </div>
  );
}
