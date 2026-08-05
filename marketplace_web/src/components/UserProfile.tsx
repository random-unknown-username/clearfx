import { useState, useEffect } from 'react';
import { User as UserIcon, ArrowUpCircle } from 'lucide-react';

interface UserProfileProps {
  uid: string;
  handle: string;
}

interface Design {
  slug: string;
  name: string;
  upvotes_count: number;
}

export default function UserProfile({ uid, handle, designs = [] }: UserProfileProps) {
  const [userDesigns, setUserDesigns] = useState<Design[]>([]);

  useEffect(() => {
    // Filter the designs from the prop to just those matching this user's handle/uid
    const filtered = designs.filter((d: any) => d.author_uid === uid || d.creator?.handle === handle);
    setUserDesigns(filtered.sort((a: any, b: any) => (b.upvotes_count || 0) - (a.upvotes_count || 0)));
  }, [uid, handle, designs]);

  const totalUpvotes = userDesigns.reduce((acc, curr) => acc + (curr.upvotes_count || 0), 0);

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
      <div className="card card-raised" style={{ marginBottom: 'var(--space-6)' }}>
        <div className="card-header" style={{ padding: 'var(--space-4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: 'var(--bg-canvas)', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border-strong)' }}>
              <UserIcon size={32} color="var(--text-muted)" />
            </div>
            <div>
              <h2 style={{ fontSize: '24px', marginBottom: '4px' }}>@{handle}</h2>
              <div className="mono-label">
                UID: {uid}
              </div>
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', borderTop: '1px solid var(--border-hairline)', background: 'var(--bg-canvas)' }}>
          <div style={{ flex: 1, padding: 'var(--space-3)', borderRight: '1px solid var(--border-hairline)' }}>
            <div className="mono-label" style={{ marginBottom: '8px' }}>Total Designs</div>
            <div style={{ fontSize: '24px', fontWeight: 500 }}>{designs.length}</div>
          </div>
          <div style={{ flex: 1, padding: 'var(--space-3)' }}>
            <div className="mono-label" style={{ marginBottom: '8px' }}>Total Upvotes</div>
            <div style={{ fontSize: '24px', fontWeight: 500 }}>{totalUpvotes}</div>
          </div>
        </div>
      </div>

      <h3 style={{ fontSize: '18px', marginBottom: 'var(--space-3)' }}>Published Designs</h3>
      
      <div className="card">
        {userDesigns.length === 0 ? (
          <div className="empty-state">No designs published yet.</div>
        ) : (
          <div className="card-content">
            {userDesigns.map(d => (
              <div key={d.slug} className="anim-item" style={{ cursor: 'default' }}>
                <div>
                  <div className="anim-info">
                    <h4>{d.name}</h4>
                  </div>
                  <div className="anim-author">{d.slug}</div>
                </div>
                <div className="anim-stats">
                  <ArrowUpCircle size={12} style={{ marginRight: '4px' }} /> {d.upvotes_count || 0}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
