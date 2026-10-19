"""Original-page 2024 presidential glyph readings for three county canvasses."""
from record_small_presidential_original import build


MANUAL = {
    'marion': {
        (2, 1, 'Randall Terry'): 1,
        (2, 1, 'Robert F. Kennedy Jr.'): 4,
        (2, 4, 'Kamala D. Harris'): 100,
        (2, 11, 'Kamala D. Harris'): 111,
        (3, 2, 'Claudia De la Cruz'): 0,
        (3, 2, 'Kamala D. Harris'): 133,
        (3, 2, 'Randall Terry'): 0,
        (4, 1, 'Chase Oliver'): 21,
        (4, 1, 'Claudia De la Cruz'): 10,
        (4, 1, 'Robert F. Kennedy Jr.'): 41,
    },
    'wayne': {
        (2, 7, 'Chase Oliver'): 0,
        (2, 10, 'Donald J. Trump'): 82,
        (2, 11, 'Shiva Ayyadurai'): 0,
        (3, 3, 'Robert F. Kennedy Jr.'): 6,
        (3, 7, 'Jill Stein'): 0,
        (3, 8, 'Claudia De la Cruz'): 1,
        (3, 8, 'Donald J. Trump'): 91,
        (3, 8, 'Robert F. Kennedy Jr.'): 1,
        (3, 9, 'Jill Stein'): 0,
    },
    'pearl-river': {
        (2, 3, 'Kamala D. Harris'): 102,
        (2, 6, 'Kamala D. Harris'): 53,
        (2, 7, 'Robert F. Kennedy Jr.'): 2,
        (3, 3, 'Kamala D. Harris'): 393,
        (3, 5, 'Chase Oliver'): 3,
        (3, 8, 'Kamala D. Harris'): 151,
        (4, 1, 'Kamala D. Harris'): 20,
        (4, 4, 'Robert F. Kennedy Jr.'): 1,
        (4, 5, 'Donald J. Trump'): 174,
        (4, 5, 'Peter Sonski'): 0,
        (4, 6, 'Robert F. Kennedy Jr.'): 101,
    },
}


def main():
    build(MANUAL, 'batch12', 71, 891, 30)


if __name__ == '__main__':
    main()
