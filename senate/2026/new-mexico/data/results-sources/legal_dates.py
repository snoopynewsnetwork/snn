"""Explicit statutory calendar arithmetic; no source-printed hours invented."""
from acquire import *
from datetime import date,timedelta,datetime,timezone
from zoneinfo import ZoneInfo
def calculate():
    e=date(2026,11,3)
    before=[e-timedelta(days=n) for n in range(1,22)]
    sats=[d for d in before if d.weekday()==5]
    board=e+timedelta(days=21)
    assert board.weekday()==1 and len(sats)==3
    rows=[]
    def add(name,source,formula,value,hour=None):rows.append(dict(name=name,source=source,formula=formula,date=value.isoformat(),source_printed_hour=hour))
    add('ordinary mailed application','NMSA 1-6-5(A)','Election Day minus 14 days',e-timedelta(days=14))
    add('clerk early voting and ordinary mailing begins','NMSA 1-6-5 / 1-6-5.7(A)','Election Day minus 28 days',e-timedelta(days=28))
    add('alternate early voting begins','NMSA 1-6-5.7(B)','third Saturday preceding Election Day',sats[2])
    add('early voting Saturday endpoint','NMSA 1-6-5.7','Saturday immediately preceding Election Day',sats[0])
    add('military-overseas transmission','NMSA 1-6B-7','Election Day minus 45 days; transmission, not voted-return grace',e-timedelta(days=45))
    add('Election Day polls','NMSA 1-12-1','Election Day',e,'7:00 a.m.–7:00 p.m.')
    add('mailed receipt','NMSA 1-6-10(A), 1-6B-8','Election Day; no ordinary postmark grace',e,'7:00 p.m.')
    add('ordinary county canvass earliest','NMSA 1-13-13(A)','Election Day plus 6 days',e+timedelta(days=6))
    add('ordinary county canvass latest','NMSA 1-13-13(A)','Election Day plus 10 days',e+timedelta(days=10))
    add('over150000 voter county canvass latest','NMSA 1-13-13(A)','Election Day plus 13 days; county category not independently assigned',e+timedelta(days=13))
    add('state canvass','NMSA 1-13-15','third Tuesday after Election Day',board)
    add('rule information/documentation endpoint','1.10.22.11 NMAC','Friday prior to statutory state-canvass meeting; written appeal process retained separately',board-timedelta(days=4))
    add('earliest state election certificate','NMSA 1-13-16(B)','Election Day plus 31 days; approval also required',e+timedelta(days=31))
    local=datetime(2026,11,3,19,tzinfo=ZoneInfo('America/Denver'))
    return dict(calculations=rows,conditional_timezone_calculation=dict(assumption='America/Denver civil time; complete current federal boundary/DST authority not independently recovered',local=local.isoformat(),utc=local.astimezone(timezone.utc).isoformat(),source_printed_UTC=False,not_a_publisher_timestamp=True),no_deadline_hour_inferred=True,no_future_court_extension_assumed=True)
def main():dump(HERE/'legal-calculations.json',calculate())
if __name__=='__main__':main()
