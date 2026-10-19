"""Separate direct complete-original Yalobusha special and runoff grids."""
from record_2018_native_manual_original import build

SPECIAL = ['Tobey Bernard Bartee', 'Mike Espy', 'Cindy Hyde-Smith', 'Chris McDaniel']
RUNOFF = ['Mike Espy', 'Cindy Hyde-Smith']
HEADERS = {
    2: ['Beat One North', 'Beat One South', 'Beat Two Water\nValley',
        'Five Coffeeville', 'Five Scobey', "Five Scuna - Vann'S\nMill",
        'Five Tillatoba', 'Four Coffeeville', 'Four Oakland',
        'Three North West', 'Three Sylva Rena'],
    3: ['TOTAL', '', '', '', '', '', '', '', '', '', ''],
}
LABELS = {sid: HEADERS for sid in ('sos-2018-county-yalobusha',
                                    'sos-2018-runoff-county-yalobusha')}
STAGES = [
    dict(source_id='sos-2018-county-yalobusha', date='2018-11-06',
         office='United States-Senate Special', candidate_order=SPECIAL,
         candidate_values={
             'Tobey Bernard Bartee': {
                 2: [19, 3, 10, 9, 0, 0, 1, 13, 9, 7, 4],
                 3: [75, None, None, None, None, None, None, None, None, None, None]},
             'Mike Espy': {
                 2: [258, 119, 515, 152, 62, 35, 37, 259, 340, 166, 85],
                 3: [2028, None, None, None, None, None, None, None, None, None, None]},
             'Cindy Hyde-Smith': {
                 2: [363, 138, 204, 256, 76, 60, 85, 56, 199, 352, 215],
                 3: [2004, None, None, None, None, None, None, None, None, None, None]},
             'Chris McDaniel': {
                 2: [87, 31, 75, 58, 23, 20, 25, 17, 70, 105, 50],
                 3: [561, None, None, None, None, None, None, None, None, None, None]},
         }),
    dict(source_id='sos-2018-runoff-county-yalobusha', date='2018-11-27',
         office='United States-Senate Unexpired Term', candidate_order=RUNOFF,
         candidate_values={
             'Mike Espy': {
                 2: [281, 122, 555, 175, 57, 39, 34, 290, 360, 171, 100],
                 3: [2184, None, None, None, None, None, None, None, None, None, None]},
             'Cindy Hyde-Smith': {
                 2: [390, 160, 225, 276, 82, 78, 113, 66, 241, 407, 243],
                 3: [2281, None, None, None, None, None, None, None, None, None, None]},
         }),
]

if __name__ == '__main__':
    build('Yalobusha', '28161', STAGES, LABELS, 11, 3, 1)
