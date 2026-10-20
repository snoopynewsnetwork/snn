from common import *
m=fetch('court-usps-sep14-order','https://www.supremecourt.gov/opinions/25pdf/26a305_4g15.pdf?inline=1',basis='exact official Supreme Court primary search discovery; September14 denial of stay, preserve order/concurrence/dissent separately from AG guidance');inspect(m);print(m.get('status'),m.get('raw_bytes'))
