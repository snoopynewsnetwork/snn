"""Direct complete-original Sunflower special and runoff native readings."""
from record_2018_native_manual_original import build

HEADERS = {
    2: [
        '11-Inverness', '12-Moorhead', '13-Indianola #1\nSoutheast',
        '21-Indianola #2\nWest', '22-Indianola #2 East',
        '31-Indianola #3\nSouth', '32-Indianola #3\nNorth',
        '33-Indianola #3\nNortheast', '41-Fairview-Hale',
        '42-Boyer-Linn', '43-Doddsville',
    ],
    3: [
        '44-Ruleville', '45-Sunflower 4', '51-Ruleville North',
        '52-Sunflower\nPlantation', '53-Rome', '54-Drew',
        'TOTAL', '', '', '', '',
    ],
}
STAGES = [
    dict(source_id='sos-2018-county-sunflower', date='2018-11-06',
         office='United States-Senate Special',
         candidate_order=['Tobey Bernard Bartee', 'Mike Espy',
                          'Cindy Hyde-Smith', 'Chris McDaniel'],
         candidate_values={
             'Tobey Bernard Bartee': {
                 2: [4, 10, 6, 4, 15, 9, 8, 4, 0, 4, 4],
                 3: [11, 6, 4, 0, 1, 10, 100, None, None, None, None],
             },
             'Mike Espy': {
                 2: [239, 523, 345, 333, 1153, 379, 155, 162, 11, 130, 73],
                 3: [595, 317, 134, 17, 61, 463, 5090, None, None, None, None],
             },
             'Cindy Hyde-Smith': {
                 2: [282, 91, 10, 152, 21, 349, 119, 173, 57, 133, 16],
                 3: [52, 73, 144, 72, 41, 119, 1904, None, None, None, None],
             },
             'Chris McDaniel': {
                 2: [27, 16, 6, 28, 15, 52, 19, 24, 12, 16, 4],
                 3: [19, 8, 43, 15, 11, 59, 374, None, None, None, None],
             },
         }),
    dict(source_id='sos-2018-runoff-county-sunflower', date='2018-11-27',
         office='United States-Senate Unexpired Term',
         candidate_order=['Mike Espy', 'Cindy Hyde-Smith'],
         candidate_values={
             'Mike Espy': {
                 2: [249, 534, 345, 350, 1154, 407, 162, 166, 9, 131, 85],
                 3: [632, 318, 145, 8, 69, 537, 5301, None, None, None, None],
             },
             'Cindy Hyde-Smith': {
                 2: [292, 91, 1, 148, 14, 359, 119, 174, 69, 138, 17],
                 3: [63, 68, 165, 97, 50, 169, 2034, None, None, None, None],
             },
         }),
]
LABELS = {stage['source_id']: HEADERS for stage in STAGES}

if __name__ == '__main__':
    build('Sunflower', '28133', STAGES, LABELS, 17, 3, 7)
