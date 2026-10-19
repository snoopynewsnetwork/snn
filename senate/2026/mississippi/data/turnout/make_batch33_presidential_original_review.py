"""Render complete original Kemper presidential pages, including parallel page 6."""
from make_small_presidential_original_review import build

if __name__=='__main__':
    build(['kemper'],'batch33',peer_position_only=True)
