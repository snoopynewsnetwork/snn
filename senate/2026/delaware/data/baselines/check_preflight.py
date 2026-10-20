#!/usr/bin/env python3
"""Run requested coordinator preflight with all writes redirected into owned scope."""
from pathlib import Path
P=Path(__file__).resolve().parent
code=(P.parent/'preflight_primary_sources.py').read_text()
ns={'__name__':'independently_invoked_preflight','__file__':str(P.parent/'preflight_primary_sources.py')}
exec(compile(code,ns['__file__'],'exec'),ns)
ns['D']=P/'source';ns['N']=P.parent/'news';ns['main']()
