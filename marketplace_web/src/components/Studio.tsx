import { useEffect, useRef, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { Play, Code2, Terminal as TerminalIcon, UploadCloud } from 'lucide-react';
import Editor from '@monaco-editor/react';

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

interface StudioProps {
  user: any;
  onPublish: (design: any) => void;
}

export default function Studio({ user, onPublish }: StudioProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const [code, setCode] = useState(DEFAULT_CODE);
  const wsRef = useRef<WebSocket | null>(null);
  const termRef = useRef<Terminal | null>(null);

  useEffect(() => {
    if (!terminalRef.current) return;

    const term = new Terminal({
      theme: {
        background: '#000000',
        foreground: '#ffffff',
        cursor: '#ffffff',
      },
      fontFamily: "'JetBrains Mono', monospace",
      fontSize: 13,
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
      term.writeln('\x1b[32mCompiler ready. Click "Execute" to preview.\x1b[0m');
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
      wsRef.current.send(JSON.stringify({ 
        type: 'run', 
        code, 
        width: termRef.current.cols, 
        height: termRef.current.rows 
      }));
    }
  };

  const handlePublish = async () => {
    if (!user) {
      alert("Please sign in from the Explore tab to publish designs.");
      return;
    }
    
    const name = prompt("Enter a name for your animation:");
    if (!name) return;
    
    const desc = prompt("Enter a short description:");
    if (!desc) return;
    
    const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    
    try {
      const newDesign = {
        slug: slug,
        name: name,
        description: desc,
        author_uid: user.uid,
        creator: { handle: user.handle },
        author_handle: user.handle,
        source: 'community',
        code: code,
        timestamp: new Date().toISOString()
      };
      
      try {
        await fetch('http://localhost:8000/api/publish', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            slug: slug,
            name: name,
            description: desc,
            author_handle: user.handle,
            code: code
          })
        });
      } catch (err) {
        console.error("Failed to publish to local backend", err);
      }

      onPublish(newDesign);
      alert(`Successfully published ${name} to the catalog!`);
    } catch (err: any) {
      console.error(err);
      alert("Failed to publish: " + err.message);
    }
  };

  return (
    <div className="split-layout">
      <div className="card card-raised">
        <div className="card-header">
          <div className="card-title"><Code2 size={14}/> design.py</div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn btn-secondary" onClick={handlePublish} style={{ height: '24px', fontSize: '12px', padding: '0 8px' }}>
              <UploadCloud size={12} /> Publish
            </button>
            <button className="btn btn-primary" onClick={handleRun} style={{ height: '24px', fontSize: '12px', padding: '0 8px' }}>
              <Play size={12} /> Execute
            </button>
          </div>
        </div>
        <div className="card-content" style={{ padding: 0 }}>
          <Editor
            height="100%"
            defaultLanguage="python"
            theme="vs-dark"
            value={code}
            onChange={(value) => setCode(value || '')}
            options={{
              minimap: { enabled: false },
              fontSize: 13,
              fontFamily: "'Geist Mono', monospace",
              padding: { top: 16 },
              scrollBeyondLastLine: false,
              renderLineHighlight: 'all',
              hideCursorInOverviewRuler: true,
              overviewRulerBorder: false,
              scrollbar: {
                vertical: 'hidden',
                horizontal: 'hidden'
              }
            }}
          />
        </div>
      </div>

      <div className="card product-frame">
        <div className="product-frame-header" style={{ justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: '6px' }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--border-strong)' }}></div>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--border-strong)' }}></div>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--border-strong)' }}></div>
          </div>
          <span className="mono-label">LIVE PREVIEW</span>
          <div style={{ width: 40 }}></div>
        </div>
        <div className="card-content terminal-wrapper">
          <div ref={terminalRef} className="terminal-container" />
        </div>
      </div>
    </div>
  );
}
