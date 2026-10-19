"""Original-page 2024 presidential glyph readings for three publications."""
from record_small_presidential_original import build


MANUAL = {
    'pontotoc': {
        (2, 1, 'Peter Sonski'): 0,
        (2, 1, 'Shiva Ayyadurai'): 0,
        (2, 4, 'Kamala D. Harris'): 62,
        (2, 6, 'Peter Sonski'): 0,
        (2, 7, 'Peter Sonski'): 0,
        (2, 8, 'Jill Stein'): 0,
        (2, 11, 'Kamala D. Harris'): 13,
        (3, 1, 'Kamala D. Harris'): 95,
        (3, 1, 'Peter Sonski'): 0,
        (3, 1, 'Shiva Ayyadurai'): 0,
        (3, 3, 'Kamala D. Harris'): 70,
        (3, 8, 'Jill Stein'): 2,
        (3, 10, 'Peter Sonski'): 0,
        (3, 10, 'Robert F. Kennedy Jr.'): 1,
        (3, 11, 'Chase Oliver'): 3,
        (3, 11, 'Jill Stein'): 0,
        (4, 1, 'Claudia De la Cruz'): 1,
        (4, 5, 'Peter Sonski'): 0,
    },
    'tate': {
        (2, 1, 'Shiva Ayyadurai'): 0,
        (2, 3, 'Claudia De la Cruz'): 1,
        (2, 3, 'Robert F. Kennedy Jr.'): 0,
        (2, 4, 'Robert F. Kennedy Jr.'): 1,
        (2, 5, 'Kamala D. Harris'): 363,
        (2, 7, 'Jill Stein'): 0,
        (2, 8, 'Randall Terry'): 0,
        (2, 9, 'Kamala D. Harris'): 71,
        (2, 11, 'Kamala D. Harris'): 288,
        (3, 1, 'Peter Sonski'): 0,
        (3, 2, 'Randall Terry'): 0,
        (3, 2, 'Shiva Ayyadurai'): 0,
        (3, 3, 'Claudia De la Cruz'): 0,
        (3, 3, 'Robert F. Kennedy Jr.'): 3,
        (3, 5, 'Randall Terry'): 1,
        (3, 8, 'Randall Terry'): 0,
        (3, 8, 'Shiva Ayyadurai'): 0,
        (3, 9, 'Shiva Ayyadurai'): 3,
    },
    'humphreys': {
        (3, 1, 'Claudia De la Cruz'): 0,
        (3, 4, 'Peter Sonski'): 0,
        (3, 5, 'Robert F. Kennedy Jr.'): 0,
        (3, 6, 'Jill Stein'): 0,
        (3, 6, 'Randall Terry'): 0,
        (3, 7, 'Kamala D. Harris'): 8,
        (3, 7, 'Randall Terry'): 0,
        (3, 7, 'Shiva Ayyadurai'): 0,
        (3, 8, 'Donald J. Trump'): 143,
        (3, 9, 'Jill Stein'): 0,
        (3, 9, 'Peter Sonski'): 0,
        (3, 9, 'Robert F. Kennedy Jr.'): 0,
        (3, 10, 'Jill Stein'): 0,
        (3, 10, 'Randall Terry'): 0,
        (3, 11, 'Chase Oliver'): 1,
        (4, 3, 'Kamala D. Harris'): 2443,
        (4, 3, 'Robert F. Kennedy Jr.'): 10,
    },
}


def main():
    build(MANUAL, 'batch14', 60, 693, 53)


if __name__ == '__main__':
    main()
