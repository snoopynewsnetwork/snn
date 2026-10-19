"""Yazoo presidential glyph readings from three complete original pages."""
from record_small_presidential_original import build


MANUAL = {
    'yazoo': {
        (4, 1, 'Jill Stein'): 0,
        (4, 1, 'Kamala D. Harris'): 210,
        (4, 1, 'Peter Sonski'): 0,
        (4, 1, 'Shiva Ayyadurai'): 0,
        (4, 3, 'Chase Oliver'): 2,
        (4, 4, 'Kamala D. Harris'): 98,
        (4, 8, 'Shiva Ayyadurai'): 0,
        (4, 11, 'Jill Stein'): 0,
        (4, 11, 'Peter Sonski'): 1,
        (5, 1, 'Kamala D. Harris'): 34,
        (5, 2, 'Kamala D. Harris'): 176,
        (5, 2, 'Shiva Ayyadurai'): 0,
        (5, 4, 'Claudia De la Cruz'): 1,
        (5, 4, 'Kamala D. Harris'): 930,
        (5, 5, 'Kamala D. Harris'): 11,
        (5, 8, 'Peter Sonski'): 0,
        (5, 8, 'Shiva Ayyadurai'): 0,
        (5, 11, 'Shiva Ayyadurai'): 1,
        (6, 1, 'Donald J. Trump'): 201,
        (6, 1, 'Kamala D. Harris'): 38,
        (6, 1, 'Shiva Ayyadurai'): 0,
        (6, 2, 'Kamala D. Harris'): 4342,
        (6, 2, 'Randall Terry'): 11,
    },
}


def main():
    build(MANUAL, 'batch15', 23, 297, 23)


if __name__ == '__main__':
    main()
