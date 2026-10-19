"""Clarke presidential glyph readings from three complete original pages."""
from record_small_presidential_original import build


MANUAL = {
    'clarke': {
        (2, 2, 'Chase Oliver'): 0,
        (2, 2, 'Claudia De la Cruz'): 0,
        (2, 3, 'Donald J. Trump'): 97,
        (2, 3, 'Kamala D. Harris'): 112,
        (2, 3, 'Randall Terry'): 1,
        (2, 4, 'Donald J. Trump'): 942,
        (2, 4, 'Randall Terry'): 0,
        (2, 5, 'Chase Oliver'): 1,
        (2, 5, 'Donald J. Trump'): 162,
        (2, 5, 'Peter Sonski'): 0,
        (2, 5, 'Randall Terry'): 1,
        (2, 6, 'Claudia De la Cruz'): 0,
        (2, 6, 'Donald J. Trump'): 953,
        (2, 7, 'Claudia De la Cruz'): 0,
        (2, 7, 'Kamala D. Harris'): 69,
        (2, 8, 'Chase Oliver'): 0,
        (2, 9, 'Kamala D. Harris'): 99,
        (2, 9, 'Randall Terry'): 0,
        (2, 10, 'Kamala D. Harris'): 28,
        (2, 10, 'Randall Terry'): 0,
        (2, 11, 'Chase Oliver'): 0,
        (2, 11, 'Claudia De la Cruz'): 0,
        (2, 11, 'Donald J. Trump'): 114,
        (2, 11, 'Robert F. Kennedy Jr.'): 0,
        (3, 1, 'Kamala D. Harris'): 77,
        (3, 1, 'Peter Sonski'): 1,
        (3, 1, 'Robert F. Kennedy Jr.'): 0,
        (3, 2, 'Kamala D. Harris'): 208,
        (3, 2, 'Peter Sonski'): 0,
        (3, 2, 'Robert F. Kennedy Jr.'): 2,
        (3, 3, 'Peter Sonski'): 0,
        (3, 4, 'Claudia De la Cruz'): 0,
        (3, 4, 'Jill Stein'): 0,
        (3, 4, 'Kamala D. Harris'): 17,
        (3, 4, 'Peter Sonski'): 0,
        (3, 4, 'Randall Terry'): 0,
        (3, 4, 'Shiva Ayyadurai'): 0,
        (3, 5, 'Chase Oliver'): 1,
        (3, 5, 'Jill Stein'): 0,
        (3, 5, 'Randall Terry'): 0,
        (3, 6, 'Claudia De la Cruz'): 0,
        (3, 7, 'Kamala D. Harris'): 15,
        (3, 7, 'Randall Terry'): 0,
        (3, 8, 'Donald J. Trump'): 244,
        # Initial full-page glance read 37; a source-row reread shows 371.
        (3, 8, 'Kamala D. Harris'): 371,
        (3, 8, 'Randall Terry'): 1,
        (3, 8, 'Robert F. Kennedy Jr.'): 3,
        (3, 9, 'Chase Oliver'): 0,
        (3, 9, 'Kamala D. Harris'): 64,
        (3, 9, 'Randall Terry'): 0,
        (3, 10, 'Donald J. Trump'): 306,
        (3, 10, 'Kamala D. Harris'): 70,
        (3, 10, 'Peter Sonski'): 0,
        (3, 11, 'Donald J. Trump'): 92,
        (3, 11, 'Kamala D. Harris'): 195,
        (4, 1, 'Chase Oliver'): 0,
        (4, 1, 'Robert F. Kennedy Jr.'): 1,
        (4, 2, 'Chase Oliver'): 10,
        (4, 2, 'Kamala D. Harris'): 2430,
        (4, 2, 'Randall Terry'): 4,
        (4, 2, 'Robert F. Kennedy Jr.'): 23,
    },
}


def main():
    build(MANUAL, 'batch17', 23, 297, 61)


if __name__ == '__main__':
    main()
