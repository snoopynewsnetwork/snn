#!/usr/bin/env python3
"""Render complete original map PDF pages, preserving originals; extract all text/metadata."""
import json,subprocess
import fitz
from acquire import ROOT,STATE,save_json,sha

def main():
 qa=[]
 for p in sorted((ROOT/'raw').glob('*.pdf')):
  dest=ROOT/'previews/pdf'/p.stem;dest.parent.mkdir(parents=True,exist_ok=True)
  doc=fitz.open(p);subprocess.run(['pdftoppm','-scale-to','1600','-png',str(p),str(dest)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  rows=[]
  for i,page in enumerate(doc):
   png=path=next(dest.parent.glob(dest.name+f'-{i+1:0{len(str(len(doc)))}d}.png'))
   rows.append({'page':i+1,'size_pdf_points':list(page.rect),'text':page.get_text(),'complete_page_png':str(png.relative_to(STATE)),'png_sha256':sha(png.read_bytes())})
  qa.append({'source_path':str(p.relative_to(STATE)),'original_sha256':sha(p.read_bytes()),'metadata':doc.metadata,'page_count':len(doc),'pages':rows})
 save_json(ROOT/'qa/pdf-structure.json',{'renderer':'Poppler pdftoppm -scale-to1600 -png, complete uncropped pages; no cleanup or replacement','PDFs':qa})
 for name in ['douglas-native','lancaster-native','sarpy-native','adams-native','scottsbluff-native','31055-census-vtd20','31153-census-vtd20','31119-census-vtd20']:
  subprocess.run(['rsvg-convert','-o',str(ROOT/'previews'/f'{name}.png'),str(ROOT/'previews'/f'{name}.svg')],check=True)
 print('Rendered',len(qa),'complete PDFs /',sum(x['page_count'] for x in qa),'pages and eight representative SVGs')
if __name__=='__main__':main()
