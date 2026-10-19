"""Grenada presidential glyph readings from full original scan rasters."""
from record_small_presidential_original import build


MANUAL = {
    'grenada': {
        (3, 1, 'Kamala D. Harris'): 539,
        (3, 1, 'Randall Terry'): 0,
        (3, 2, 'Claudia De la Cruz'): 0,
        (3, 2, 'Randall Terry'): 1,
        (3, 3, 'Jill Stein'): 1,
        (3, 4, 'Kamala D. Harris'): 227,
        (3, 5, 'Claudia De la Cruz'): 0,
        (3, 5, 'Donald J. Trump'): 461,
        (3, 6, 'Claudia De la Cruz'): 0,
        (3, 7, 'Chase Oliver'): 1,
        (3, 7, 'Kamala D. Harris'): 864,
        (3, 8, 'Jill Stein'): 0,
        (3, 8, 'Robert F. Kennedy Jr.'): 0,
        (3, 9, 'Randall Terry'): 0,
        (3, 10, 'Kamala D. Harris'): 1137,
        (3, 10, 'Robert F. Kennedy Jr.'): 2,
        (3, 10, 'Shiva Ayyadurai'): 0,
        (3, 11, 'Chase Oliver'): 0,
        (3, 11, 'Jill Stein'): 0,
        (4, 1, 'Claudia De la Cruz'): 1,
        (4, 1, 'Kamala D. Harris'): 150,
        (4, 1, 'Randall Terry'): 0,
        (4, 1, 'Shiva Ayyadurai'): 0,
        (4, 3, 'Chase Oliver'): 8,
        (4, 3, 'Claudia De la Cruz'): 4,
        (4, 3, 'Jill Stein'): 11,
        (4, 3, 'Peter Sonski'): 0,
        (4, 3, 'Randall Terry'): 2,
        (4, 3, 'Robert F. Kennedy Jr.'): 28,
        (4, 3, 'Shiva Ayyadurai'): 2,
    },
}


def main():
    build(MANUAL, 'batch21', 13, 198, 30)


if __name__ == '__main__':
    main()
