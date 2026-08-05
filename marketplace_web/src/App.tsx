import { useState, useEffect } from 'react';
import { TerminalPreview } from './components/TerminalPreview';
import { Studio } from './components/Studio';
import { Play, Terminal, Zap, Compass, Star, Settings, User, LogIn } from 'lucide-react';
import './index.css';

interface Creator {
  handle: string;
}

interface DesignInfo {
  slug: string;
  name: string;
  description: string;
  creator: Creator;
}

function App() {
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'explore' | 'install' | 'studio'>('explore');
  const [catalog, setCatalog] = useState<DesignInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [isGuest, setIsGuest] = useState(true);
  const [showLoginModal, setShowLoginModal] = useState(false);
  
  useEffect(() => {
    fetch('http://localhost:8000/api/v1/designs')
      .then(res => res.json())
      .then(data => {
        setCatalog(data.items || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching catalog:', err);
        setLoading(false);
      });
  }, []);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsGuest(false);
    setShowLoginModal(false);
  };

  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="nav-brand">
          <Terminal className="brand-icon" />
          <span>ClearFX</span>
        </div>
        <div className="nav-links">
          <a href="#" className={activeTab === 'explore' ? 'active' : ''} onClick={() => setActiveTab('explore')}><Compass size={18}/> Explore</a>
          <a href="#" className={activeTab === 'install' ? 'active' : ''} onClick={() => setActiveTab('install')}><Zap size={18}/> CLI / Install</a>
          <a href="#" className={activeTab === 'studio' ? 'active' : ''} onClick={() => setActiveTab('studio')}><Settings size={18}/> Studio</a>
        </div>
        <div className="nav-auth">
          {isGuest ? (
            <button className="auth-btn" onClick={() => setShowLoginModal(true)}><LogIn size={16}/> Sign In / Join</button>
          ) : (
            <button className="auth-btn outline" onClick={() => setIsGuest(true)}><User size={16}/> @creator</button>
          )}
        </div>
      </nav>

      <main className="main-content">
        <header className="hero">
          <div className="hero-badge">v2.0 Beta</div>
          <h1>Terminal Magic, <span>Reimagined</span>.</h1>
          <p>
            Experience breathtaking terminal animations. Bring your command line to life with 
            procedurally generated art that leaves you with a clean slate.
          </p>
        </header>

        {activeTab === 'explore' && (
          <section className="preview-section">
            <div className="preview-layout">
              <div className="animation-list">
                <div className="list-header">
                  <h3>Community Animations</h3>
                  <Star className="trending-icon" size={18}/>
                </div>
                <div className="list-items">
                  {loading ? (
                    <div className="empty-state"><p>Loading catalog...</p></div>
                  ) : catalog.length === 0 ? (
                    <div className="empty-state"><p>No animations found.</p></div>
                  ) : (
                    catalog.map((anim) => (
                      <button 
                        key={anim.slug}
                        className={`anim-card ${selectedSlug === anim.slug ? 'selected' : ''}`}
                        onClick={() => setSelectedSlug(anim.slug)}
                        title={anim.description}
                      >
                        <div className="anim-info">
                          <h4>{anim.name}</h4>
                          <span className="anim-author">by {anim.creator?.handle || 'Unknown'}</span>
                        </div>
                        <div className="play-btn">
                          <Play size={16} fill={selectedSlug === anim.slug ? "currentColor" : "none"}/>
                        </div>
                      </button>
                    ))
                  )}
                </div>
              </div>

              <div className="terminal-display-area">
                <div className="terminal-window-decor">
                  <div className="mac-buttons">
                    <span className="close"></span>
                    <span className="minimize"></span>
                    <span className="maximize"></span>
                  </div>
                  <div className="terminal-title">
                    {selectedSlug ? `~ clearfx play ${selectedSlug}` : '~ bash'}
                  </div>
                </div>
                <div className="terminal-wrapper">
                  {selectedSlug ? (
                    <TerminalPreview key={selectedSlug} slug={selectedSlug} />
                  ) : (
                    <div className="empty-state">
                      <Terminal size={48} className="empty-icon" />
                      <p>Select an animation to preview</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}

        {activeTab === 'install' && (
          <section className="install-section" style={{ background: 'var(--card-border)', padding: '2rem', border: '1px solid #333' }}>
            <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>Terminal Integration API</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
              ClearFX provides a native shell integration API that automatically hijacks your terminal's default <code>clear</code> command.
              Every time you clear your screen, you'll be greeted by a randomized animation from your catalog.
            </p>
            
            <div style={{ background: 'var(--bg-color)', padding: '1.5rem', border: '1px solid #333', marginBottom: '2rem' }}>
              <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>1. Install via Pip</h3>
              <pre style={{ color: 'var(--text-primary)', fontFamily: 'monospace' }}><code>pip install clearfx</code></pre>
            </div>

            <div style={{ background: 'var(--bg-color)', padding: '1.5rem', border: '1px solid #333', marginBottom: '2rem' }}>
              <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>2. Setup Shell Hooks</h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem', fontSize: '0.9rem' }}>
                Run this command to automatically inject the API hooks into your ~/.bashrc or ~/.zshrc.
              </p>
              <pre style={{ color: 'var(--text-primary)', fontFamily: 'monospace' }}><code>clearfx setup-shell</code></pre>
            </div>

            <div style={{ background: 'var(--bg-color)', padding: '1.5rem', border: '1px solid #333' }}>
              <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>3. API Customization</h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem', fontSize: '0.9rem' }}>
                You can configure the API via the CLI to whitelist or blacklist specific tags.
              </p>
              <pre style={{ color: 'var(--text-primary)', fontFamily: 'monospace' }}><code>clearfx config set tags "cyberpunk,retro"
clearfx config set fps 60
clearfx config set duration_ms 1000</code></pre>
            </div>
          </section>
        )}

        {activeTab === 'studio' && (
          <Studio />
        )}
      </main>

      {/* Login Modal */}
      {showLoginModal && (
        <div className="modal-overlay" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="modal-content" style={{ background: 'var(--bg-color)', border: '1px solid var(--text-primary)', padding: '2rem', width: '400px' }}>
            <h2 style={{ marginBottom: '1.5rem', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', fontSize: '1.2rem' }}>Authenticate</h2>
            <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem', fontFamily: 'JetBrains Mono' }}>Handle</label>
                <input type="text" required placeholder="@creator" style={{ width: '100%', padding: '0.75rem', background: 'var(--card-border)', border: '1px solid #333', color: 'white', fontFamily: 'monospace' }} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem', fontFamily: 'JetBrains Mono' }}>API Key</label>
                <input type="password" required placeholder="cfx_..." style={{ width: '100%', padding: '0.75rem', background: 'var(--card-border)', border: '1px solid #333', color: 'white', fontFamily: 'monospace' }} />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button type="button" onClick={() => setShowLoginModal(false)} style={{ flex: 1, padding: '0.75rem', background: 'transparent', color: 'white', border: '1px solid #333', cursor: 'pointer', fontFamily: 'JetBrains Mono' }}>CANCEL</button>
                <button type="submit" style={{ flex: 1, padding: '0.75rem', background: 'white', color: 'black', border: 'none', cursor: 'pointer', fontFamily: 'JetBrains Mono', fontWeight: 'bold' }}>SIGN IN</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
