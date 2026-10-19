"""Lincoln presidential glyph readings from three complete original pages."""
from record_small_presidential_original import build


MANUAL = {
    'lincoln': {
        (3, 1, 'Claudia De la Cruz'): 0,
        (3, 1, 'Donald J. Trump'): 15,
        (3, 1, 'Robert F. Kennedy Jr.'): 0,
        (3, 2, 'Shiva Ayyadurai'): 0,
        (3, 3, 'Claudia De la Cruz'): 0,
        (3, 6, 'Claudia De la Cruz'): 0,
        (3, 6, 'Kamala D. Harris'): 72,
        (3, 6, 'Shiva Ayyadurai'): 0,
        (3, 7, 'Claudia De la Cruz'): 0,
        (3, 7, 'Jill Stein'): 1,
        (3, 7, 'Robert F. Kennedy Jr.'): 0,
        (3, 7, 'Shiva Ayyadurai'): 0,
        (3, 8, 'Kamala D. Harris'): 14,
        (3, 9, 'Donald J. Trump'): 981,
        (3, 9, 'Jill Stein'): 0,
        (3, 9, 'Shiva Ayyadurai'): 0,
        (3, 10, 'Claudia De la Cruz'): 0,
        (3, 10, 'Randall Terry'): 0,
        (3, 10, 'Shiva Ayyadurai'): 0,
        (3, 11, 'Jill Stein'): 0,
        (4, 1, 'Donald J. Trump'): 12,
        (4, 3, 'Shiva Ayyadurai'): 0,
        (4, 5, 'Peter Sonski'): 0,
        (4, 5, 'Robert F. Kennedy Jr.'): 2,
        (4, 5, 'Shiva Ayyadurai'): 0,
        (4, 6, 'Jill Stein'): 0,
        (4, 6, 'Peter Sonski'): 0,
        (4, 6, 'Randall Terry'): 0,
        (4, 7, 'Jill Stein'): 0,
        (4, 8, 'Donald J. Trump'): 147,
        (4, 8, 'Shiva Ayyadurai'): 0,
        (4, 11, 'Donald J. Trump'): 691,
        (4, 11, 'Robert F. Kennedy Jr.'): 3,
        (5, 1, 'Claudia De la Cruz'): 0,
        (5, 1, 'Robert F. Kennedy Jr.'): 0,
        (5, 3, 'Shiva Ayyadurai'): 0,
        (5, 4, 'Kamala D. Harris'): 421,
        (5, 4, 'Shiva Ayyadurai'): 0,
        (5, 5, 'Shiva Ayyadurai'): 0,
        (5, 7, 'Claudia De la Cruz'): 0,
        (5, 7, 'Kamala D. Harris'): 38,
        (5, 8, 'Claudia De la Cruz'): 0,
        (5, 8, 'Jill Stein'): 0,
        (5, 8, 'Kamala D. Harris'): 122,
        (5, 8, 'Randall Terry'): 0,
        (5, 8, 'Robert F. Kennedy Jr.'): 3,
        (5, 8, 'Shiva Ayyadurai'): 0,
        (5, 9, 'Claudia De la Cruz'): 6,
        (5, 9, 'Peter Sonski'): 10,
    },
}


def main():
    build(MANUAL, 'batch19', 30, 297, 49)


if __name__ == '__main__':
    main()
