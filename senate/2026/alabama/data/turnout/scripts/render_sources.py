#!/usr/bin/env python3
"""Recreate full-page visual witnesses without modifying original bytes."""
import fitz,pathlib,gzip,json
from freeze import write
R=pathlib.Path(__file__).resolve().parents[1]
for y,pages in [(2024,[5,6]),(2022,[4,5]),(2020,[3,4])]:
 b=gzip.decompress((R.parent/'news'/f'sos-{y}-canvass-original.html.gz').read_bytes());d=fitz.open(stream=b,filetype='pdf')
 for page in pages:write(R/f'source/visual/canvass-{y}-p{page}.png',d[page-1].get_pixmap(matrix=fitz.Matrix(1.6,1.6)).tobytes('png'))
for prefix,name,pages,scale in [('dbb854','2026-dem-cert',[1,2,3],1.5),('a3a109','2026-rep-cert',[1,2],1.5),('707afb','2026-ind-cert',[1],1.5),('4f1a69','2026-autauga-sample',[1],1.25)]:
 b=gzip.decompress(next((R/'source/http').glob(prefix+'*.gz')).read_bytes());d=fitz.open(stream=b,filetype='pdf')
 for page in pages:write(R/f'source/visual/{name}-p{page}.png',d[page-1].get_pixmap(matrix=fitz.Matrix(scale,scale)).tobytes('png'))
