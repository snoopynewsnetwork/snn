"""Original-only complete page rasters and OCR exception cards for eight views."""
from make_small_presidential_original_review import build

SLUGS=['union','stone','george','lowndes','panola','monroe','prentiss','newton']

def main():build(SLUGS,'batch4')
if __name__=='__main__':main()
