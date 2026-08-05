import urllib.request
import urllib.parse
import json
import subprocess

def get_token():
    result = subprocess.run(['gcloud', 'auth', 'print-access-token'], capture_output=True, text=True, check=True)
    return result.stdout.strip()

try:
    token = get_token()
except Exception as e:
    print(f"Failed to get gcloud token: {e}")
    exit(1)

base_url = "https://firestore.googleapis.com/v1/projects/clearfx-29744/databases/(default)/documents/designs"

dummy_designs = [
  { "slug": 'matrix-rain', "name": 'Matrix Digital Rain', "desc": 'Classic falling green code effect with varying speeds.' },
  { "slug": 'starfield-warp', "name": 'Starfield Warp', "desc": 'Hyperspace jump effect flying through a field of stars.' },
  { "slug": 'sys-boot', "name": 'System Boot Sequence', "desc": 'Simulated retro OS boot sequence with random hex dumps.' },
  { "slug": 'neon-waves', "name": 'Neon Synthwave', "desc": 'Retro 80s grid with a neon sun and scanlines.' },
  { "slug": 'fire-particles', "name": 'Campfire', "desc": 'Cozy ascii fire animation burning at the bottom of your screen.' },
  { "slug": 'snow-fall', "name": 'Blizzard', "desc": 'Heavy snow falling across the terminal with wind effects.' },
  { "slug": 'glitch-art', "name": 'Glitch Text', "desc": 'Corrupted text blocks that randomly glitch and tear.' },
  { "slug": 'radar-sweep', "name": 'Submarine Radar', "desc": 'Classic sweeping green radar detecting blips.' },
  { "slug": 'conways-game', "name": 'Game of Life', "desc": 'Conways Game of Life cellular automaton running briefly.' },
  { "slug": 'dvd-bounce', "name": 'DVD Logo', "desc": 'The iconic bouncing DVD logo hitting the corners.' }
]

def format_doc(d, upvotes):
    return {
        "fields": {
            "slug": {"stringValue": d["slug"]},
            "name": {"stringValue": d["name"]},
            "description": {"stringValue": d["desc"]},
            "author_uid": {"stringValue": "dummy-uid-12345"},
            "author_handle": {"stringValue": "Rand0m_unkn0wn"},
            "upvotes_count": {"integerValue": str(upvotes)}
        }
    }

print("Seeding designs via REST...")
for i, d in enumerate(dummy_designs):
    upvotes = 500 - (i * 40)
    doc_data = format_doc(d, upvotes)
    
    # We use PATCH to create or update the document with the specific ID
    url = f"{base_url}/{d['slug']}"
    req = urllib.request.Request(url, data=json.dumps(doc_data).encode('utf-8'), method='PATCH')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Added {d['slug']}")
    except Exception as e:
        print(f"Failed to add {d['slug']}: {e}")

print("Done!")
