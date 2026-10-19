"""Bolivar presidential glyph readings from three complete original pages."""
from record_small_presidential_original import build


MANUAL = {
    'bolivar': {
        (6, 1, 'Peter Sonski'): 1,
        (6, 1, 'Robert F. Kennedy Jr.'): 1,
        (6, 7, 'Shiva Ayyadurai'): 0,
        (6, 8, 'Randall Terry'): 0,
        (6, 9, 'Jill Stein'): 2,
        (6, 10, 'Randall Terry'): 1,
        (6, 10, 'Shiva Ayyadurai'): 0,
        (6, 11, 'Kamala D. Harris'): 460,
        (6, 11, 'Shiva Ayyadurai'): 0,
        (7, 1, 'Chase Oliver'): 0,
        (7, 1, 'Claudia De la Cruz'): 0,
        (7, 1, 'Kamala D. Harris'): 141,
        (7, 5, 'Jill Stein'): 0,
        (7, 5, 'Peter Sonski'): 0,
        (7, 6, 'Peter Sonski'): 0,
        (7, 8, 'Chase Oliver'): 0,
        (7, 8, 'Donald J. Trump'): 40,
        (7, 8, 'Robert F. Kennedy Jr.'): 0,
        (7, 9, 'Claudia De la Cruz'): 0,
        (7, 9, 'Donald J. Trump'): 7,
        (7, 9, 'Randall Terry'): 0,
        (8, 3, 'Kamala D. Harris'): 457,
        (8, 5, 'Kamala D. Harris'): 148,
    },
}


def main():
    build(MANUAL, 'batch18', 30, 297, 23)


if __name__ == '__main__':
    main()
