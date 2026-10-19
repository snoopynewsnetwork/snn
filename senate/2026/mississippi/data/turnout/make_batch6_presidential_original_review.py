"""Original-only page renders and exception cards for four source views."""
from make_small_presidential_original_review import build

SLUGS=['montgomery','tallahatchie','lawrence','copiah']

def main():build(SLUGS,'batch6')
if __name__=='__main__':main()
