"""Lee and Madison presidential corrections read from the original page grids."""
from record_small_presidential_original import build


MANUAL = {
    'lee': {
        (2, 3, 'Peter Sonski'): 1,
        (2, 4, 'Robert F. Kennedy Jr.'): 0,
        (2, 6, 'Robert F. Kennedy Jr.'): 0,
        (2, 8, 'Randall Terry'): 0,
        (2, 8, 'Shiva Ayyadurai'): 0,
        (3, 3, 'Jill Stein'): 0,
        (4, 3, 'Jill Stein'): 2,
        (4, 8, 'Kamala D. Harris'): 46,
        (4, 11, 'Peter Sonski'): 0,
        (5, 1, 'Kamala D. Harris'): 10616,
    },
    'madison': {
        (2, 9, 'Shiva Ayyadurai'): 0,
        (3, 4, 'Robert F. Kennedy Jr.'): 11,
        (3, 10, 'Robert F. Kennedy Jr.'): 11,
        (4, 1, 'Claudia De la Cruz'): 1,
        (4, 1, 'Donald J. Trump'): 2320,
        (4, 2, 'Donald J. Trump'): 235,
        (4, 9, 'Shiva Ayyadurai'): 0,
        (5, 1, 'Claudia De la Cruz'): 2,
        (5, 1, 'Peter Sonski'): 5,
        (5, 3, 'Robert F. Kennedy Jr.'): 2,
        (5, 5, 'Randall Terry'): 1,
        (5, 9, 'Shiva Ayyadurai'): 1,
        (5, 10, 'Jill Stein'): 3,
        (5, 10, 'Kamala D. Harris'): 854,
        (5, 11, 'Kamala D. Harris'): 257,
        (6, 1, 'Chase Oliver'): 169,
        (6, 1, 'Claudia De la Cruz'): 30,
        (6, 1, 'Donald J. Trump'): 32333,
        (6, 1, 'Jill Stein'): 109,
        (6, 1, 'Kamala D. Harris'): 22700,
        (6, 1, 'Peter Sonski'): 56,
        (6, 1, 'Randall Terry'): 33,
        (6, 1, 'Robert F. Kennedy Jr.'): 253,
        (6, 1, 'Shiva Ayyadurai'): 27,
    },
}


def main():
    build(MANUAL, 'batch8', 77, 891, 34)


if __name__ == '__main__':
    main()
