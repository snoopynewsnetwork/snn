"""Original-page 2024 presidential glyph readings for three county canvasses."""
from record_small_presidential_original import build


MANUAL = {
    'covington': {
        (2, 1, 'Donald J. Trump'): 801,
        (2, 3, 'Claudia De la Cruz'): 0,
        (2, 3, 'Jill Stein'): 0,
        (2, 5, 'Robert F. Kennedy Jr.'): 0,
        (2, 6, 'Kamala D. Harris'): 473,
        (2, 8, 'Peter Sonski'): 0,
        (2, 9, 'Donald J. Trump'): 109,
        (2, 9, 'Randall Terry'): 0,
        (2, 9, 'Shiva Ayyadurai'): 0,
        (2, 10, 'Chase Oliver'): 1,
        (2, 10, 'Kamala D. Harris'): 69,
        (2, 10, 'Randall Terry'): 1,
        (2, 11, 'Jill Stein'): 1,
        (3, 1, 'Peter Sonski'): 0,
        (3, 3, 'Donald J. Trump'): 81,
        (3, 4, 'Robert F. Kennedy Jr.'): 3,
        (3, 5, 'Jill Stein'): 7,
        (3, 5, 'Peter Sonski'): 2,
    },
    'leake': {
        (2, 1, 'Robert F. Kennedy Jr.'): 1,
        (2, 4, 'Donald J. Trump'): 373,
        (2, 4, 'Shiva Ayyadurai'): 0,
        (2, 7, 'Jill Stein'): 1,
        (2, 8, 'Claudia De la Cruz'): 0,
        (2, 8, 'Kamala D. Harris'): 75,
        (2, 8, 'Robert F. Kennedy Jr.'): 1,
        (2, 8, 'Shiva Ayyadurai'): 0,
        (2, 9, 'Jill Stein'): 0,
        (2, 9, 'Randall Terry'): 0,
        (2, 9, 'Robert F. Kennedy Jr.'): 3,
        (2, 10, 'Shiva Ayyadurai'): 1,
        (2, 11, 'Jill Stein'): 0,
        (3, 1, 'Claudia De la Cruz'): 0,
        (3, 1, 'Randall Terry'): 0,
        (3, 2, 'Randall Terry'): 0,
        (3, 3, 'Donald J. Trump'): 217,
        (3, 6, 'Shiva Ayyadurai'): 1,
        (3, 8, 'Peter Sonski'): 0,
    },
    'attala': {
        (3, 1, 'Robert F. Kennedy Jr.'): 0,
        (3, 2, 'Kamala D. Harris'): 6,
        (3, 3, 'Robert F. Kennedy Jr.'): 0,
        (3, 3, 'Shiva Ayyadurai'): 0,
        (3, 4, 'Kamala D. Harris'): 88,
        (3, 4, 'Randall Terry'): 0,
        (3, 7, 'Randall Terry'): 1,
        (3, 7, 'Robert F. Kennedy Jr.'): 1,
        (3, 8, 'Donald J. Trump'): 166,
        (3, 8, 'Peter Sonski'): 0,
        (3, 10, 'Shiva Ayyadurai'): 0,
        (4, 1, 'Kamala D. Harris'): 237,
        (4, 2, 'Kamala D. Harris'): 63,
        (4, 4, 'Claudia De la Cruz'): 0,
        (4, 4, 'Kamala D. Harris'): 461,
        (4, 6, 'Peter Sonski'): 0,
        (4, 7, 'Claudia De la Cruz'): 0,
        (4, 7, 'Robert F. Kennedy Jr.'): 1,
        (4, 8, 'Randall Terry'): 6,
    },
}


def main():
    build(MANUAL, 'batch9', 54, 594, 56)


if __name__ == '__main__':
    main()
