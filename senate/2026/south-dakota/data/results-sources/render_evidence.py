#!/usr/bin/env python3
"""Rebuild eight bounded original previews; full originals remain read-only."""
import sys
sys.dont_write_bytecode=True
from common import *
from reconstruct import reconstruct
import subprocess
if __name__=='__main__':
 cases=[('shared','sos-2022-precinct-canvass',110,'2022-brown'),('shared','sos-2022-precinct-canvass',581,'2022-hamlin'),('shared','sos-2024-general-county-aurora-clark',1,'2024-county-aurora-page1'),('owned','lincoln-2022',1,'lincoln-2022'),('owned','lincoln-2024',1,'lincoln-2024'),('owned','lake-2022',1,'lake-2022'),('owned','lincoln-ballot',1,'lincoln-ballot'),('owned','hanson-ballot',1,'hanson-ballot')]
 for which,id,page,name in cases:
  path='/tmp/sd-results-render-'+id+'.pdf';reconstruct(which,id,path);subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','1600' if name.startswith(('2022-','2024-county')) else '1500','-png','-singlefile',path,str(ROOT/'previews'/name)],check=True)
