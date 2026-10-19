"""Direct complete-original 2020 Union Senate native grid reading."""
from record_2020_native_manual_original import build

LABELS = {
    2: [
        'Macedonia', 'Blythe', 'Myrtle', 'Glenfield', 'Pinedale',
        'West Union', 'Sportsplex', 'Ingomar', "King's Chapel",
        'Courthouse', 'Central Maintenance',
    ],
    3: [
        'Beacon Hill', 'Blue Springs', 'Hillcrest Church', 'Center',
        'Ellistown Baptist\nChurch', 'Watson Grove Baptist\nChurch',
        'Keownville', 'Pleasant Ridge', 'Jericho', 'TOTAL', '',
    ],
}
GRIDS = {
    2: {
        'Mike Espy': [26, 33, 193, 206, 35, 60, 314, 159, 76, 256, 123],
        'Cindy Hyde-Smith': [279, 198, 809, 461, 323, 540, 581, 711, 354, 562, 667],
        'Jimmy L. Edwards': [17, 14, 39, 30, 32, 27, 28, 24, 19, 21, 31],
    },
    3: {
        'Mike Espy': [158, 61, 288, 31, 154, 362, 53, 32, 40, 2660, None],
        'Cindy Hyde-Smith': [525, 403, 381, 360, 652, 738, 468, 224, 336, 9572, None],
        'Jimmy L. Edwards': [18, 13, 18, 14, 17, 33, 7, 13, 9, 424, None],
    },
}

if __name__ == '__main__':
    build('union', 'union', GRIDS, LABELS, 20, hint_version='v7')
