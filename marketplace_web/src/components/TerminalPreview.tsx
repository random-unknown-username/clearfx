import { useEffect, useRef, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';

interface TerminalPreviewProps {
  slug: string;
}

export default function TerminalPreview({ slug }: TerminalPreviewProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'error' | 'disconnected'>('connecting');
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!terminalRef.current) return;

    // Initialize xterm.js
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

    // Connect to WebSocket
    // Hardcoded to localhost:8000 for preview
    const wsUrl = `ws://localhost:8000/ws/preview/${slug}?width=${term.cols}&height=${term.rows}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('connected');
      term.clear();
    };

    ws.onmessage = (event) => {
      term.write(event.data);
    };

    ws.onclose = () => {
      setStatus('disconnected');
    };

    ws.onerror = () => {
      setStatus('error');
    };

    const handleResize = () => {
      fitAddon.fit();
      // Optionally could send resize event to backend, but we fix it for now
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      ws.close();
      term.dispose();
    };
  }, [slug]);

  return (
    <div className="terminal-container">
      {status === 'connecting' && <div className="terminal-overlay">Connecting to terminal...</div>}
      {status === 'error' && <div className="terminal-overlay error">Connection error</div>}
      <div ref={terminalRef} className="terminal-element" />
    </div>
  );
}
