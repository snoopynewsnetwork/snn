"""Original-only page renders and exception cards for four further SEMS views."""
from make_small_presidential_original_review import build

SLUGS=['walthall','jasper','yalobusha','washington']

def main():build(SLUGS,'batch5')
if __name__=='__main__':main()
