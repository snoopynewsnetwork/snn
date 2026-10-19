"""Direct readings from all four complete original 2024 county canvass grids.

Only values that disagreed with the earlier independent pixel aid are entered
here. Each was read in its full-page candidate row and physical source column;
the peer is used solely by the generic builder for reciprocal comparison after
this source-bound ledger is constructed.
"""
from record_small_presidential_original import build


MANUAL = {
    'harrison': {
        (3, 1, 'Kamala D. Harris'): 686,
        (3, 3, 'Peter Sonski'): 1,
        (3, 10, 'Kamala D. Harris'): 469,
        (3, 11, 'Claudia De la Cruz'): 1,
        (4, 1, 'Kamala D. Harris'): 163,
        (4, 7, 'Claudia De la Cruz'): 2,
        (5, 5, 'Kamala D. Harris'): 827,
        (5, 7, 'Kamala D. Harris'): 48,
        (5, 7, 'Shiva Ayyadurai'): 0,
        (5, 8, 'Donald J. Trump'): 781,
        (5, 10, 'Peter Sonski'): 0,
        (5, 11, 'Robert F. Kennedy Jr.'): 11,
    },
    'desoto': {
        (2, 4, 'Peter Sonski'): 1,
        (2, 6, 'Kamala D. Harris'): 420,
        (2, 9, 'Shiva Ayyadurai'): 2,
        (2, 10, 'Kamala D. Harris'): 861,
        (3, 2, 'Kamala D. Harris'): 906,
        (3, 8, 'Chase Oliver'): 6,
        (4, 5, 'Randall Terry'): 11,
        (4, 9, 'Claudia De la Cruz'): 11,
        (4, 9, 'Jill Stein'): 8,
        (4, 11, 'Peter Sonski'): 3,
        (6, 1, 'Kamala D. Harris'): 384,
        (6, 2, 'Donald J. Trump'): 592,
    },
    'rankin': {
        (2, 6, 'Robert F. Kennedy Jr.'): 14,
        (2, 10, 'Shiva Ayyadurai'): 0,
        (3, 1, 'Jill Stein'): 1,
        (3, 1, 'Randall Terry'): 0,
        (3, 10, 'Claudia De la Cruz'): 1,
        (3, 10, 'Randall Terry'): 1,
        (3, 11, 'Chase Oliver'): 2,
        (4, 3, 'Donald J. Trump'): 971,
        (4, 10, 'Jill Stein'): 1,
        (4, 10, 'Kamala D. Harris'): 311,
        (4, 10, 'Randall Terry'): 1,
        (5, 5, 'Chase Oliver'): 1,
        (5, 9, 'Jill Stein'): 0,
        (5, 9, 'Kamala D. Harris'): 148,
    },
    'forrest': {
        (2, 1, 'Kamala D. Harris'): 354,
        (2, 3, 'Peter Sonski'): 0,
        (2, 4, 'Kamala D. Harris'): 29,
        (2, 10, 'Peter Sonski'): 0,
        (3, 9, 'Peter Sonski'): 1,
        (3, 11, 'Kamala D. Harris'): 487,
        (3, 11, 'Peter Sonski'): 0,
        (5, 1, 'Claudia De la Cruz'): 4,
    },
}


def main():
    build(MANUAL, 'batch7', 176, 1881, 46)


if __name__ == '__main__':
    main()
