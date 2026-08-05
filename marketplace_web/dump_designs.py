import subprocess
import urllib.request
import json

def get_token():
    return subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode('utf-8').strip()

try:
    token = get_token()
    req = urllib.request.Request(
        "https://firestore.googleapis.com/v1/projects/clearfx-29744/databases/(default)/documents/designs",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        docs = []
        if 'documents' in data:
            for d in data['documents']:
                fields = d.get('fields', {})
                doc = {}
                for k, v in fields.items():
                    if 'stringValue' in v:
                        doc[k] = v['stringValue']
                    elif 'integerValue' in v:
                        doc[k] = int(v['integerValue'])
                docs.append(doc)
        with open('src/lib/mockData.ts', 'w') as f:
            f.write("export const mockDesigns = " + json.dumps(docs, indent=2) + ";\n")
        print("Successfully dumped", len(docs), "designs!")
except Exception as e:
    print(f"Error: {e}")
