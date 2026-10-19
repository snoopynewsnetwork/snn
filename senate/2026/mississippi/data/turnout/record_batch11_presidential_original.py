"""Original-page 2024 presidential glyph readings for three county canvasses."""
from record_small_presidential_original import build


MANUAL = {
    'lamar': {
        (2, 3, 'Robert F. Kennedy Jr.'): 11,
        (4, 1, 'Jill Stein'): 0,
        (4, 1, 'Shiva Ayyadurai'): 0,
    },
    'neshoba': {
        # Initial full-page glance interchanged these adjacent columns;
        # the retained enlarged ORIGINAL cells show Herbert 1 and Hope 0.
        (3, 2, 'Claudia De la Cruz'): 1,
        (3, 3, 'Claudia De la Cruz'): 0,
        (4, 1, 'Kamala D. Harris'): 51,
    },
    'oktibbeha': {
        (2, 1, 'Chase Oliver'): 1,
        (2, 1, 'Donald J. Trump'): 117,
        (2, 1, 'Kamala D. Harris'): 175,
        (2, 3, 'Kamala D. Harris'): 17,
        (2, 6, 'Shiva Ayyadurai'): 2,
        (2, 8, 'Jill Stein'): 1,
        (2, 8, 'Shiva Ayyadurai'): 1,
        (2, 10, 'Peter Sonski'): 1,
        (2, 10, 'Randall Terry'): 2,
        (3, 2, 'Chase Oliver'): 11,
        (3, 10, 'Randall Terry'): 17,
    },
}


def main():
    build(MANUAL, 'batch11', 67, 792, 17)


if __name__ == '__main__':
    main()
