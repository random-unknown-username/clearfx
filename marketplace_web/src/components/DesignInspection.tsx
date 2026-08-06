import { useState, useEffect } from 'react';
import TerminalPreview from './TerminalPreview';
import { TerminalSquare, X } from 'lucide-react';

interface DesignInspectionProps {
  slug: string;
  onClose: () => void;
  mockData?: any;
}

interface Design {
  slug: string;
  name: string;
  description: string;
  author_uid: string;
  author_handle: string;
  upvotes_count: number;
}

export default function DesignInspection({ slug, onClose, mockData }: DesignInspectionProps) {
  const [design, setDesign] = useState<Design | null>(mockData || null);
  const [loading, setLoading] = useState(!mockData);
  const [error, setError] = useState('');

  useEffect(() => {
    if (mockData) {
      setDesign(mockData as Design);
      setLoading(false);
      return;
    }
    // Fallback if not provided (shouldn't happen with our rewrite)
    setTimeout(() => setError('Design not found'), 100);
  }, [slug, mockData]);

  // Upvotes removed.
  if (loading) return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '800px' }}>
        <div className="empty-state">Loading details...</div>
      </div>
    </div>
  );
  if (error) return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '800px' }}>
        <div className="empty-state">{error}</div>
      </div>
    </div>
  );
  if (!design) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '900px', padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', height: '80vh' }}>
        <div className="card-header">
          <div className="card-title"><TerminalSquare size={14}/> {design.name}</div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn btn-tertiary" onClick={onClose} style={{ padding: '0 4px' }}>
              <X size={16} />
            </button>
          </div>
        </div>
        <div style={{ padding: 'var(--space-4)', borderBottom: '1px solid var(--border-hairline)', flexShrink: 0 }}>
          <div style={{ display: 'flex', gap: 'var(--space-4)', marginBottom: 'var(--space-3)' }}>
            <div style={{ flex: 1 }}>
              <p className="body-text" style={{ marginBottom: 'var(--space-3)' }}>{design.description}</p>
              <div className="inspection-grid" style={{ padding: 0, gap: 'var(--space-4)' }}>
                <div className="inspection-item">
                  <span className="label">Author</span>
                  <span className="value">@{design.author_handle}</span>
                </div>
                <div className="inspection-item">
                  <span className="label">Package Slug</span>
                  <span className="value mono" style={{ fontFamily: 'var(--font-mono)' }}>{design.slug}</span>
                </div>
              </div>
            </div>
            
            <div style={{ flex: 1, background: 'var(--bg-canvas)', border: '1px solid var(--border-strong)', padding: 'var(--space-3)', borderRadius: 'var(--radius-card)' }}>
              <div className="mono-label" style={{ marginBottom: '8px' }}>Install Command</div>
              <pre style={{ background: 'var(--bg-surface)', padding: '12px', borderRadius: '4px', border: '1px solid var(--border-hairline)', fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-high)' }}>clearfx install {design.slug}</pre>
            </div>
          </div>
        </div>
        
        <div className="product-frame" style={{ margin: 'var(--space-4)', flex: 1, minHeight: '300px' }}>
          <div className="product-frame-header" style={{ justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', gap: '6px' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--border-strong)' }}></div>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--border-strong)' }}></div>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--border-strong)' }}></div>
            </div>
            <span className="mono-label">LIVE PREVIEW</span>
            <div style={{ width: 40 }}></div>
          </div>
          <div className="terminal-wrapper">
            <TerminalPreview slug={design.slug} code={(design as any).code || ((design as any).source === 'community' || !design.hasOwnProperty('source') ? `"""Community Design."""
from clearfx.compiler.creator_sdk import CreatorAnimation

class MyAnimation(CreatorAnimation):
    def design(self) -> None:
        self.add_text(text="Community Design Loading...", x="w/2 - 14", y="h/2", fg=(0, 255, 128), bold=True)
` : undefined)} />
          </div>
        </div>
      </div>
    </div>
  );
}
