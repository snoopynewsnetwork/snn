"""Original-only pages for three preferred 2024 county publications."""
from make_small_presidential_original_review import build


def main():
    build(['pike-updated', 'marshall', 'simpson'], 'batch13')


if __name__ == '__main__':
    main()
