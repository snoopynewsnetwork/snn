"""Lauderdale presidential glyph readings from four complete original pages."""
from record_small_presidential_original import build


MANUAL = {
    'lauderdale': {
        (7, 1, 'Randall Terry'): 2,
        (7, 1, 'Shiva Ayyadurai'): 1,
        (7, 2, 'Peter Sonski'): 2,
        (7, 2, 'Shiva Ayyadurai'): 0,
        (7, 3, 'Chase Oliver'): 1,
        (7, 3, 'Kamala D. Harris'): 196,
        (7, 3, 'Shiva Ayyadurai'): 1,
        (7, 5, 'Jill Stein'): 2,
        (7, 6, 'Donald J. Trump'): 141,
        (7, 6, 'Kamala D. Harris'): 768,
        (7, 6, 'Shiva Ayyadurai'): 0,
        (7, 7, 'Kamala D. Harris'): 483,
        (7, 8, 'Kamala D. Harris'): 127,
        (7, 8, 'Shiva Ayyadurai'): 0,
        (7, 9, 'Chase Oliver'): 1,
        (7, 9, 'Jill Stein'): 0,
        (7, 9, 'Kamala D. Harris'): 327,
        (7, 9, 'Shiva Ayyadurai'): 2,
        (7, 11, 'Donald J. Trump'): 108,
        (7, 11, 'Jill Stein'): 0,
        (7, 11, 'Kamala D. Harris'): 115,
        (8, 1, 'Peter Sonski'): 1,
        (8, 1, 'Robert F. Kennedy Jr.'): 1,
        (8, 1, 'Shiva Ayyadurai'): 2,
        (8, 2, 'Randall Terry'): 0,
        (8, 3, 'Claudia De la Cruz'): 0,
        (8, 3, 'Donald J. Trump'): 115,
        (8, 3, 'Jill Stein'): 1,
        (8, 3, 'Randall Terry'): 0,
        (8, 5, 'Chase Oliver'): 1,
        (8, 5, 'Claudia De la Cruz'): 1,
        (8, 5, 'Peter Sonski'): 3,
        (8, 5, 'Randall Terry'): 0,
        (8, 7, 'Shiva Ayyadurai'): 0,
        (8, 9, 'Jill Stein'): 0,
        (8, 10, 'Chase Oliver'): 1,
        (8, 10, 'Claudia De la Cruz'): 0,
        (8, 10, 'Donald J. Trump'): 117,
        (9, 1, 'Kamala D. Harris'): 149,
        (9, 1, 'Shiva Ayyadurai'): 0,
        (9, 2, 'Randall Terry'): 0,
        (9, 2, 'Shiva Ayyadurai'): 0,
        (9, 3, 'Shiva Ayyadurai'): 0,
        (9, 5, 'Jill Stein'): 0,
        (9, 7, 'Donald J. Trump'): 344,
        (9, 8, 'Randall Terry'): 0,
        (9, 9, 'Kamala D. Harris'): 78,
        (9, 10, 'Donald J. Trump'): 199,
        (9, 10, 'Randall Terry'): 0,
        (10, 1, 'Chase Oliver'): 1,
        (10, 1, 'Kamala D. Harris'): 294,
        (10, 2, 'Chase Oliver'): 1,
        (10, 2, 'Jill Stein'): 0,
        (10, 2, 'Kamala D. Harris'): 67,
        (10, 2, 'Randall Terry'): 0,
        (10, 2, 'Robert F. Kennedy Jr.'): 1,
        (10, 3, 'Chase Oliver'): 0,
        (10, 3, 'Kamala D. Harris'): 117,
        (10, 4, 'Jill Stein'): 0,
        (10, 5, 'Chase Oliver'): 42,
        (10, 5, 'Kamala D. Harris'): 10677,
    },
}


def main():
    build(MANUAL, 'batch20', 37, 396, 61)


if __name__ == '__main__':
    main()
