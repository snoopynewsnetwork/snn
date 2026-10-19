"""Original-page 2024 presidential glyph readings for four county canvasses."""
from record_small_presidential_original import build


MANUAL = {
    'hancock': {
        (3, 3, 'Jill Stein'): 1,
        (4, 2, 'Peter Sonski'): 0,
    },
    'chickasaw': {
        (2, 4, 'Donald J. Trump'): 128,
        (2, 6, 'Donald J. Trump'): 218,
        (2, 8, 'Robert F. Kennedy Jr.'): 0,
    },
    'warren': {
        (2, 4, 'Jill Stein'): 1,
        (2, 4, 'Kamala D. Harris'): 153,
        (2, 8, 'Chase Oliver'): 0,
        (2, 8, 'Claudia De la Cruz'): 0,
        (3, 1, 'Kamala D. Harris'): 469,
        (4, 2, 'Kamala D. Harris'): 8683,
    },
    'jones': {
        (3, 7, 'Robert F. Kennedy Jr.'): 1,
        (4, 1, 'Jill Stein'): 0,
        (4, 2, 'Jill Stein'): 0,
        (4, 2, 'Peter Sonski'): 0,
        (4, 4, 'Chase Oliver'): 0,
        (4, 5, 'Claudia De la Cruz'): 0,
        (4, 6, 'Jill Stein'): 0,
        (4, 9, 'Jill Stein'): 0,
        (6, 5, 'Peter Sonski'): 0,
    },
}


def main():
    build(MANUAL, 'batch10', 102, 1188, 20)


if __name__ == '__main__':
    main()
