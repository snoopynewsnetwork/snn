"""Lafayette presidential glyph readings from two complete original pages."""
from record_small_presidential_original import build


MANUAL = {
    'lafayette': {
        (2, 1, 'Kamala D. Harris'): 485,
        (2, 1, 'Peter Sonski'): 1,
        (2, 3, 'Kamala D. Harris'): 93,
        (2, 4, 'Jill Stein'): 1,
        (2, 6, 'Kamala D. Harris'): 71,
        (2, 6, 'Peter Sonski'): 2,
        (2, 8, 'Donald J. Trump'): 1948,
        (2, 8, 'Kamala D. Harris'): 1009,
        (2, 8, 'Peter Sonski'): 10,
        (2, 8, 'Shiva Ayyadurai'): 0,
        (2, 9, 'Jill Stein'): 21,
        (2, 10, 'Claudia De la Cruz'): 1,
        (3, 1, 'Jill Stein'): 15,
        (3, 1, 'Kamala D. Harris'): 847,
        (3, 1, 'Robert F. Kennedy Jr.'): 11,
        (3, 2, 'Chase Oliver'): 1,
        (3, 2, 'Claudia De la Cruz'): 0,
        (3, 2, 'Shiva Ayyadurai'): 1,
        (3, 3, 'Kamala D. Harris'): 70,
        (3, 4, 'Kamala D. Harris'): 362,
        (3, 5, 'Chase Oliver'): 0,
        (3, 6, 'Peter Sonski'): 0,
        (3, 8, 'Claudia De la Cruz'): 25,
        (3, 8, 'Donald J. Trump'): 14050,
        (3, 8, 'Randall Terry'): 20,
        (3, 8, 'Shiva Ayyadurai'): 6,
    },
}


def main():
    build(MANUAL, 'batch16', 18, 198, 26)


if __name__ == '__main__':
    main()
