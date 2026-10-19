"""Original-only page surfaces for Covington, Leake and Attala."""
from make_small_presidential_original_review import build


def main():
    build(['covington', 'leake', 'attala'], 'batch9')


if __name__ == '__main__':
    main()
