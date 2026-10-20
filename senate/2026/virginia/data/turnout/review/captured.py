"""Read exact before-review bodies via fixed captures, never peer discovery."""
from pathlib import Path
import hashlib,json,tarfile,gzip
T=Path(__file__).resolve().parents[1];S=T.parents[1];H=T/'history/resume-citation-reciprocal'
sha=lambda b:hashlib.sha256(b).hexdigest()
class Capture:
 def __init__(self,name):
  self.index=json.loads((H/(name+'.json')).read_text());p=S/self.index['archive_path'];assert sha(p.read_bytes())==self.index['archive_sha256'];self.tar=tarfile.open(p);self.entries={e['path']:e for e in self.index['bodies']}
 def read(self,path):
  e=self.entries[path];b=self.tar.extractfile(e['archive_name']).read() if e['archive_name'] else (S/e['reference_path']).read_bytes();assert len(b)==e['bytes'] and sha(b)==e['sha256'];return b
 def json(self,path):
  b=self.read(path);return json.loads(gzip.decompress(b) if path.endswith('.gz') else b)
