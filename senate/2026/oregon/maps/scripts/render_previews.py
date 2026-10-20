from common import *
import fitz
SELECTED=['benton-precinct','clackamas-precinct','multnomah-splits','wasco-precinct','binary-census-oregon-county2010']
def rendered():
 for key in SELECTED:
  with fitz.open(stream=(M/'previews'/f'{key}.svg').read_bytes(),filetype='svg') as doc:yield 'maps/previews/'+key+'.png',doc[0].get_pixmap().tobytes('png')
if __name__=='__main__':
 for path,b in rendered():(S/path).write_bytes(b)
