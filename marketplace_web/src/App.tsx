import { useState, useEffect } from 'react';
import Studio from './components/Studio';
import DesignInspection from './components/DesignInspection';
import TerminalPreview from './components/TerminalPreview';
import UserProfile from './components/UserProfile';
import { defaultCatalog } from './lib/catalog';
import { TerminalSquare, Compass, Code2, User as UserIcon, LogIn, ArrowUpCircle } from 'lucide-react';
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

export default function App() {
  const [designs, setDesigns] = useState<any[]>(defaultCatalog);
  const [sortBy, setSortBy] = useState<'newest' | 'name' | 'author'>('newest');
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'explore' | 'install' | 'studio' | 'profile'>('explore');
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [user, setUser] = useState<any | null>(null);
  const [userHandle, setUserHandle] = useState<string>('');

  useEffect(() => {
    // Simulate checking local storage for a session
    const saved = localStorage.getItem('clearfx_user');
    if (saved) {
      const u = JSON.parse(saved);
      setUser(u);
      setUserHandle(u.handle);
    }

    // Fetch catalog from backend
    fetch('http://localhost:8000/api/catalog')
      .then(res => res.json())
      .then(data => {
        if (data.designs) {
          // Remove duplicates if backend returned some defaults
          const merged = [...data.designs];
          setDesigns(merged);
        }
      })
      .catch(err => console.error("Failed to fetch catalog:", err));
  }, []);

  const sortedDesigns = [...designs].sort((a, b) => {
    if (sortBy === 'name') return (a.name || '').localeCompare(b.name || '');
    if (sortBy === 'author') {
      const aAuth = a.creator?.handle || a.author_handle || '';
      const bAuth = b.creator?.handle || b.author_handle || '';
      return aAuth.localeCompare(bAuth);
    }
    if (sortBy === 'newest') {
      if (a.source === 'community' && b.source === 'builtin') return -1;
      if (a.source === 'builtin' && b.source === 'community') return 1;
      return 0;
    }
    return 0;
  });

  const handleGoogleLogin = async () => {
    const mockUser = { uid: 'mock-user-123', email: 'developer@clearfx.local', handle: 'Rand0m_unkn0wn' };
    setUser(mockUser);
    setUserHandle(mockUser.handle);
    localStorage.setItem('clearfx_user', JSON.stringify(mockUser));
    setShowLoginModal(false);
  };

  const handleSignOut = () => {
    setUser(null);
    setUserHandle('');
    localStorage.removeItem('clearfx_user');
  };

  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="nav-brand">
          <TerminalSquare size={18} />
          ClearFX
        </div>
        <div className="nav-links">
          <button className={activeTab === 'explore' ? 'active' : ''} onClick={() => setActiveTab('explore')}>Explore</button>
          <button className={activeTab === 'install' ? 'active' : ''} onClick={() => setActiveTab('install')}>Install</button>
          <button className={activeTab === 'studio' ? 'active' : ''} onClick={() => setActiveTab('studio')}>Studio</button>
          {user && <button className={activeTab === 'profile' ? 'active' : ''} onClick={() => setActiveTab('profile')}>Profile</button>}
        </div>
        <div>
          {!user ? (
            <button className="btn btn-secondary" onClick={() => setShowLoginModal(true)}>
              <LogIn size={14} /> Sign In
            </button>
          ) : (
            <button className="btn btn-ghost" onClick={handleSignOut}>
              <UserIcon size={14} /> @{userHandle}
            </button>
          )}
        </div>
      </nav>

      <main className="main-content">
        {activeTab === 'explore' && (
          <>
            <section className="hero-layout">
              <div className="hero-content">
                <span className="mono-label" style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '16px' }}>
                  <span className="status-dot green"></span> ClearFX v2.0 Beta
                </span>
                <h1>Terminal Magic.</h1>
                <p className="body-text">
                  Experience breathtaking terminal animations. Bring your command line to life with procedurally generated art that leaves you with a clean slate. Built for precision and performance.
                </p>
                <div className="hero-actions">
                  <button className="btn btn-primary" onClick={() => setActiveTab('install')}>Get Started</button>
                  <button className="btn btn-tertiary" onClick={() => setActiveTab('studio')}>Open Studio →</button>
                </div>
              </div>
              
              <div className="product-frame">
                <div className="product-frame-header">
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--border-strong)' }}></div>
                    <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--border-strong)' }}></div>
                    <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--border-strong)' }}></div>
                  </div>
                  <span className="mono-label" style={{ marginLeft: '12px' }}>~/project/demo</span>
                </div>
                <div style={{ height: '320px', padding: '16px', background: '#000' }}>
                  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMWE5N2RhOWI3ZjUzMmUxZjJjMjRjMTRiMGU5ZGE4ZDRiYzk0ZGFjMyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/3o7TKSjRrfIPjeiVyM/giphy.gif" alt="Terminal preview" style={{ width: '100%', height: '100%', objectFit: 'cover', opacity: 0.5 }} />
                </div>
              </div>
            </section>

            <section className="catalog-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
                <h3>Community Catalog</h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <select 
                    value={sortBy} 
                    onChange={(e) => setSortBy(e.target.value as any)}
                    style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)', color: 'var(--text-normal)', padding: '4px 8px', borderRadius: '4px' }}
                  >
                    <option value="newest">Newest First</option>
                    <option value="name">Sort by Name</option>
                    <option value="author">Sort by Author</option>
                  </select>
                  <span className="mono-label">{designs.length} packages available</span>
                </div>
              </div>
              
              <div className="catalog-grid">
                {sortedDesigns.map((anim) => (
                  <div 
                    key={anim.slug}
                    className="catalog-card"
                    onClick={() => setSelectedSlug(anim.slug)}
                  >
                    <div className="catalog-card-preview">
                      <TerminalPreview slug={anim.slug} />
                    </div>
                    <div className="catalog-card-body">
                      <div className="catalog-card-header">
                        <div>
                          <div className="catalog-card-title">{anim.name}</div>
                          <div className="catalog-card-author">{anim.creator?.handle || anim.author_handle || 'unknown'}</div>
                        </div>
                      </div>
                      <div className="catalog-card-desc">{anim.description || 'No description provided.'}</div>
                      <div style={{ marginTop: 'auto', paddingTop: 'var(--space-2)' }}>
                        <span className="tag">{anim.slug}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
            
            {selectedSlug && (
              <DesignInspection slug={selectedSlug} onClose={() => setSelectedSlug(null)} mockData={designs.find((d: any) => d.slug === selectedSlug)} />
            )}
          </>
        )}

        {activeTab === 'install' && (
          <section className="card card-raised" style={{ padding: 'var(--space-6)', maxWidth: '640px', margin: '0 auto', width: '100%' }}>
            <h2 style={{ marginBottom: 'var(--space-4)' }}>Installation</h2>
            
            <div style={{ marginBottom: 'var(--space-6)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <span className="status-dot orange"></span>
                <h3 style={{ fontSize: '15px' }}>1. Package Manager</h3>
              </div>
              <p className="supporting-text" style={{ marginBottom: '12px' }}>Install the core CLI globally via pip.</p>
              <pre style={{ background: 'var(--bg-canvas)', padding: '16px', borderRadius: 'var(--radius-input)', border: '1px solid var(--border-strong)', fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-high)' }}>pip install clearfx</pre>
            </div>
            
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <span className="status-dot green"></span>
                <h3 style={{ fontSize: '15px' }}>2. Shell Hooks</h3>
              </div>
              <p className="supporting-text" style={{ marginBottom: '12px' }}>Initialize shell integrations to wrap the clear command automatically.</p>
              <pre style={{ background: 'var(--bg-canvas)', padding: '16px', borderRadius: 'var(--radius-input)', border: '1px solid var(--border-strong)', fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-high)' }}>clearfx setup-shell</pre>
            </div>
          </section>
        )}

        {activeTab === 'studio' && <Studio user={user} onPublish={(newDesign: any) => setDesigns([newDesign, ...designs])} />}
        {activeTab === 'profile' && user && <UserProfile uid={user.uid} handle={userHandle} designs={designs} />}
      </main>

      {showLoginModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Authentication</h2>
            <p>Sign in to publish your own designs to the Marketplace.</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <button className="btn btn-primary" onClick={handleGoogleLogin} style={{ width: '100%', height: '44px' }}>
                Continue with Google
              </button>
              <button className="btn btn-ghost" onClick={() => setShowLoginModal(false)} style={{ width: '100%', height: '44px' }}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
