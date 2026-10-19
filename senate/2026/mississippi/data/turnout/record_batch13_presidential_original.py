"""Original-page 2024 presidential glyph readings for three publications."""
from record_small_presidential_original import build


MANUAL = {
    'pike-updated': {
        (3, 5, 'Shiva Ayyadurai'): 0,
        (3, 8, 'Jill Stein'): 2,
        (3, 11, 'Randall Terry'): 1,
        (4, 1, 'Shiva Ayyadurai'): 0,
    },
    'marshall': {
        (2, 1, 'Claudia De la Cruz'): 2,
        (2, 4, 'Randall Terry'): 0,
        (2, 5, 'Chase Oliver'): 0,
        (2, 5, 'Robert F. Kennedy Jr.'): 0,
        (2, 5, 'Shiva Ayyadurai'): 0,
        (2, 6, 'Shiva Ayyadurai'): 0,
        (2, 7, 'Shiva Ayyadurai'): 0,
        (2, 8, 'Donald J. Trump'): 191,
        (2, 9, 'Robert F. Kennedy Jr.'): 2,
        (2, 10, 'Shiva Ayyadurai'): 0,
        (3, 5, 'Kamala D. Harris'): 185,
        (3, 8, 'Kamala D. Harris'): 166,
        (3, 9, 'Shiva Ayyadurai'): 0,
        (4, 3, 'Claudia De la Cruz'): 10,
        (4, 3, 'Peter Sonski'): 6,
        (4, 3, 'Robert F. Kennedy Jr.'): 52,
    },
    'simpson': {
        (2, 6, 'Shiva Ayyadurai'): 1,
        (2, 9, 'Peter Sonski'): 0,
        (2, 10, 'Kamala D. Harris'): 178,
        (3, 3, 'Donald J. Trump'): 526,
        (3, 3, 'Randall Terry'): 0,
        (3, 3, 'Shiva Ayyadurai'): 0,
        (3, 4, 'Claudia De la Cruz'): 0,
        (3, 4, 'Shiva Ayyadurai'): 0,
        (3, 6, 'Peter Sonski'): 0,
        (3, 6, 'Shiva Ayyadurai'): 0,
        (3, 8, 'Donald J. Trump'): 132,
        (3, 8, 'Jill Stein'): 1,
        (3, 10, 'Claudia De la Cruz'): 0,
        (3, 10, 'Shiva Ayyadurai'): 0,
        (3, 11, 'Claudia De la Cruz'): 1,
        (3, 11, 'Randall Terry'): 1,
        (4, 1, 'Chase Oliver'): 11,
        (4, 1, 'Kamala D. Harris'): 3479,
    },
}


def main():
    build(MANUAL, 'batch13', 71, 891, 38)


if __name__ == '__main__':
    main()
