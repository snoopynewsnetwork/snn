"""Separate direct complete-original Greene special and runoff grids."""
from record_2018_native_manual_original import build

SPECIAL = ['Tobey Bernard Bartee', 'Mike Espy', 'Cindy Hyde-Smith', 'Chris McDaniel']
RUNOFF = ['Mike Espy', 'Cindy Hyde-Smith']
HEADERS = {
    2: ['Leakesville', 'North Leakesville', 'State Line', 'Mutual Rights',
        'Wade', 'Jones', 'Piave', 'Maples', 'Vernal', 'Washington Neely', 'Leaf'],
    3: ['Mclain', 'Jonathan', 'TOTAL', '', '', '', '', '', '', '', ''],
}
LABELS = {sid: HEADERS for sid in ('sos-2018-county-greene',
                                    'sos-2018-runoff-county-greene')}
STAGES = [
    dict(source_id='sos-2018-county-greene', date='2018-11-06',
         office='United States-Senate Special', candidate_order=SPECIAL,
         candidate_values={
             'Tobey Bernard Bartee': {
                 2: [9, 13, 12, 1, 1, 1, 1, 10, 5, 2, 2],
                 3: [5, 2, 64, None, None, None, None, None, None, None, None]},
             'Mike Espy': {
                 2: [79, 106, 219, 7, 26, 3, 7, 61, 39, 10, 32],
                 3: [122, 18, 729, None, None, None, None, None, None, None, None]},
             'Cindy Hyde-Smith': {
                 2: [333, 47, 79, 61, 148, 61, 76, 183, 151, 95, 36],
                 3: [53, 102, 1425, None, None, None, None, None, None, None, None]},
             'Chris McDaniel': {
                 2: [281, 51, 89, 81, 187, 65, 127, 145, 120, 97, 35],
                 3: [47, 113, 1438, None, None, None, None, None, None, None, None]},
         }),
    dict(source_id='sos-2018-runoff-county-greene', date='2018-11-27',
         office='United States-Senate Unexpired Term', candidate_order=RUNOFF,
         candidate_values={
             'Mike Espy': {
                 2: [57, 122, 229, 3, 18, 0, 6, 35, 23, 2, 32],
                 3: [126, 8, 661, None, None, None, None, None, None, None, None]},
             'Cindy Hyde-Smith': {
                 2: [507, 78, 139, 117, 281, 117, 181, 286, 225, 183, 53],
                 3: [84, 171, 2422, None, None, None, None, None, None, None, None]},
         }),
]

if __name__ == '__main__':
    build('Greene', '28041', STAGES, LABELS, 13, 3, 3)
