import { useState, useEffect } from 'react';
import Studio from './components/Studio';
import DesignInspection from './components/DesignInspection';
import TerminalPreview from './components/TerminalPreview';
import UserProfile from './components/UserProfile';
import { defaultCatalog } from './lib/catalog';
import { TerminalSquare, User as UserIcon, LogIn } from 'lucide-react';
import './index.css';
import { auth, db, googleProvider, signInWithPopup, signOut, collection, getDocs, query } from './lib/firebase';
import { onAuthStateChanged } from 'firebase/auth';

const FALLBACK_CODE = `"""Community Design."""
from clearfx.compiler.creator_sdk import CreatorAnimation

class MyAnimation(CreatorAnimation):
    def design(self) -> None:
        self.add_text(
            text="Community Design Loading...",
            x="w/2 - 14",
            y="h/2",
            fg=(0, 255, 128),
            bold=True
        )
`;

export default function App() {
  const [designs, setDesigns] = useState<any[]>(defaultCatalog);
  const [sortBy, setSortBy] = useState<'newest' | 'name' | 'author'>('newest');
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'explore' | 'install' | 'studio' | 'profile'>('explore');
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [user, setUser] = useState<any | null>(null);
  const [userHandle, setUserHandle] = useState<string>('');

  useEffect(() => {
    // Listen for Firebase auth state changes
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      if (firebaseUser) {
        const handle = (firebaseUser.email || '').split('@')[0] || 'user';
        setUser({ uid: firebaseUser.uid, email: firebaseUser.email, handle });
        setUserHandle(handle);
      } else {
        setUser(null);
        setUserHandle('');
      }
    });

    // Fetch catalog from Firestore
    const fetchCatalog = async () => {
      try {
        const q = query(collection(db, "designs"));
        const querySnapshot = await getDocs(q);
        const fbDesigns = querySnapshot.docs
          .map((doc: any) => doc.data())
          .filter((d: any) => d.author_uid !== 'dummy-uid-12345');
        
        // Merge Firestore designs with builtins
        setDesigns([...fbDesigns, ...defaultCatalog]);
      } catch (err) {
        console.error("Failed to fetch from Firestore:", err);
        setDesigns(defaultCatalog);
      }
    };
    
    fetchCatalog();

    return () => unsubscribe();
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
    try {
      await signInWithPopup(auth, googleProvider);
      setShowLoginModal(false);
    } catch (error) {
      console.error(error);
    }
  };

  const handleSignOut = () => {
    signOut(auth);
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
                    <option value="newest" style={{ background: '#111', color: '#fff' }}>Newest First</option>
                    <option value="name" style={{ background: '#111', color: '#fff' }}>Sort by Name</option>
                    <option value="author" style={{ background: '#111', color: '#fff' }}>Sort by Author</option>
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
                      <TerminalPreview 
                        slug={anim.slug} 
                        code={anim.code || (!defaultCatalog.some(d => d.slug === anim.slug) ? FALLBACK_CODE : undefined)} 
                      />
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
            
            <div style={{ marginBottom: 'var(--space-6)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <span className="status-dot green"></span>
                <h3 style={{ fontSize: '15px' }}>2. Shell Hooks</h3>
              </div>
              <p className="supporting-text" style={{ marginBottom: '12px' }}>Initialize shell integrations to wrap the clear command automatically.</p>
              <pre style={{ background: 'var(--bg-canvas)', padding: '16px', borderRadius: 'var(--radius-input)', border: '1px solid var(--border-strong)', fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-high)' }}>clearfx setup-shell</pre>
            </div>

            <div style={{ marginBottom: 'var(--space-6)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <span className="status-dot purple"></span>
                <h3 style={{ fontSize: '15px' }}>3. Reload Shell</h3>
              </div>
              <p className="supporting-text" style={{ marginBottom: '12px' }}>Source your configuration file to apply the newly added shell hooks.</p>
              <pre style={{ background: 'var(--bg-canvas)', padding: '16px', borderRadius: 'var(--radius-input)', border: '1px solid var(--border-strong)', fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-high)' }}>source ~/.bashrc  # or ~/.zshrc</pre>
            </div>

            <div style={{ marginBottom: 'var(--space-6)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <span className="status-dot blue"></span>
                <h3 style={{ fontSize: '15px' }}>4. Quick Wrap</h3>
              </div>
              <p className="supporting-text" style={{ marginBottom: '12px' }}>Want to animate a specific command? Wrap it directly (e.g., wrap <code>ls</code> with the Aurora Fold animation).</p>
              <pre style={{ background: 'var(--bg-canvas)', padding: '16px', borderRadius: 'var(--radius-input)', border: '1px solid var(--border-strong)', fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-high)' }}>clearfx wrap ls --anim aurora-fold</pre>
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <span className="status-dot red"></span>
                <h3 style={{ fontSize: '15px' }}>Emergency Reset</h3>
              </div>
              <p className="supporting-text" style={{ marginBottom: '12px' }}>If you ever want to completely wipe ClearFX from your terminal and reset everything to normal.</p>
              <pre style={{ background: 'var(--bg-canvas)', padding: '16px', borderRadius: 'var(--radius-input)', border: '1px solid var(--border-strong)', fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-high)' }}>clearfx reset</pre>
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
