#!/usr/bin/env python3
"""Optional full notice OCR with all original word positions/confidences.
OCR is a derivative, never a current identity/geography or legal authority itself.
"""
import gzip,hashlib,json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parent
records=[]
for sid,pages in [('riley-generalnotice',range(1,5)),('saline-general-notice',range(1,5)),('montgomery-generalnotice',range(1,3))]:
 m=json.loads((R/'raw'/f'{sid}.meta.json').read_text())
 for page in pages:
  p=R/'extracts'/f'{sid}-page{page}.png';out=R/'extracts'/f'{sid}-page{page}.ocr'
  subprocess.run(['tesseract',str(p),str(out),'-l','eng','txt','tsv'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  records.append({'source_id':sid,'source_original_sha256':m['original_sha256'],'source_pdf_page':page,'render_path':str(p.relative_to(R)),'render_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'full_text_path':str(out.with_suffix('.ocr.txt').relative_to(R)),'full_word_positions_path':str(out.with_suffix('.ocr.tsv').relative_to(R)),'position_policy':'TSV page_num1 is this single rendered source_pdf_page; block/par/line/word/left/top/width/height/conf/text retained in full; repeated names/addresses not deduped','scope':'OCR can err. Original scan and visual checks control; no physical/current reporting-unit crosswalk approved.'})
(R/'notice-ocr-inventory.json').write_text(json.dumps({'records':records,'tool':'tesseract -l eng txt tsv; full page derivatives; no cleaned candidate/unit replacements'},indent=2)+'\n');print('OCR fullnoticepages',len(records))
