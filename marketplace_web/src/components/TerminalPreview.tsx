import { useEffect, useRef, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';

interface TerminalPreviewProps {
  slug: string;
  code?: string;
}

export default function TerminalPreview({ slug, code }: TerminalPreviewProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'error' | 'disconnected'>('connecting');
  const workerRef = useRef<Worker | null>(null);

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

    // Start WebWorker
    const worker = new Worker('/pyodideWorker.js?v=3');
    workerRef.current = worker;

    worker.onmessage = (event) => {
      const { type, data } = event.data;
      if (type === 'ready') {
        setStatus('connected');
        term.clear();
        worker.postMessage({ type: 'play', slug, code, width: term.cols, height: term.rows });
      } else if (type === 'stdout') {
        term.write(data);
      }
    };

    worker.onerror = (err) => {
      console.error('Worker error:', err);
      setStatus('error');
    };

    // Initialize worker
    worker.postMessage({ type: 'init' });

    const handleResize = () => {
      fitAddon.fit();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (workerRef.current) {
        workerRef.current.terminate();
      }
      term.dispose();
    };
  }, [slug, code]);

  return (
    <div className="terminal-container">
      {status === 'connecting' && <div className="terminal-overlay">Loading engine...</div>}
      {status === 'error' && <div className="terminal-overlay error">Engine error</div>}
      <div ref={terminalRef} className="terminal-element" />
    </div>
  );
}
