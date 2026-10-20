#!/usr/bin/env python3
"""Independent source-page extraction; every column sums to its printed footer."""
from pathlib import Path
import csv, gzip, json, re
OUT=Path(__file__).resolve().parents[1]

def read(key):return gzip.decompress((OUT/'source'/f'{key}.layout.txt.gz').read_bytes()).decode()
def write_csv(path,rows):
    with path.open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def save(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')

SPECS=[
 ('2024-president','2024-abstract',1,'US President',[
 ('Kennedy Jr / Robert F / (WTP)','Robert F Kennedy Jr','WTP'),
 ('West / Cornel (P)','Cornel West','P'),('Oliver / Chase (L)','Chase Oliver','L'),
 ('Terry / Randall (C)','Randall Terry','C'),('Trump / Donald J (R)','Donald J Trump','R'),
 ('Stein / Jill (PG)','Jill Stein','PG'),('**Harris / Kamala D (D)','Kamala D Harris','D'),('Misc.','Misc.','')]),
 ('2020-senate','2020-abstract',2,'US Senator',[
 ('Perkins / Jo Rae (R)','Jo Rae Perkins','R'),('**Merkley / Jeff (D)','Jeff Merkley','D'),
 ('Taher / Ibrahim A (PG)','Ibrahim A Taher','PG'),('Dye / Gary (L)','Gary Dye','L'),('Misc.','Misc.','')]),
 ('2022-senate','2022-abstract',1,'US Senator',[
 ('Perkins / Jo Rae (R)','Jo Rae Perkins','R'),('Pulju / Dan (PG)','Dan Pulju','PG'),
 ('**Wyden / Ron (D)','Ron Wyden','D'),('Henry / Chris (P)','Chris Henry','P'),('Misc.','Misc.','')]),
 ('2022-governor','2022-abstract',4,'Governor',[
 ('**Kotek / Tina (D)','Tina Kotek','D'),('Smith / Donice Noelle (C)','Donice Noelle Smith','C'),
 ('Noble / R Leon (L)','R Leon Noble','L'),('Johnson / Betsy (NAV)','Betsy Johnson','NAV'),
 ('Drazan / Christine (R)','Christine Drazan','R'),('Misc.','Misc.','')])]

def main():
    candidates=[];controls=[];counties=None;wide={};footers=[];universe=[]
    for contest,key,page,heading,cols in SPECS:
        lines=read(key).split('\f')[page-1].splitlines()
        assert heading in [l.strip()for l in lines]
        n=len(cols);rows=[];footer=[]
        pat=re.compile(r'^\s*([A-Za-z ]+?)\s+'+r'\s+'.join([r'([\d,]+)']*n)+r'\s*$')
        for line_no,line in enumerate(lines,1):
            m=pat.fullmatch(line)
            if not m:continue
            label=m[1].strip();values=[int(v.replace(',',''))for v in m.groups()[1:]]
            r=dict(county=label,values=values,source_key=key,page=page,line=line_no,raw_line=line)
            (footer if label.lower()=='total'else rows).append(r)
        assert len(rows)==len({r['county']for r in rows})==36 and len(footer)==1
        names=[r['county']for r in rows]
        if counties is None:
            counties=names
            wide={name:dict(county=name,county_fips=f'41{2*i+1:03d}')for i,name in enumerate(names)}
        assert names==counties
        sums=[sum(r['values'][i]for r in rows)for i in range(n)]
        assert sums==footer[0]['values']
        footers.append(dict(contest=contest,**footer[0]))
        for i,(literal,name,party)in enumerate(cols):
            scope='reported_Misc_unresolved_writein_validity'if name=='Misc.'else 'named_ballot_candidate'
            universe.append(dict(contest=contest,column_index=i,candidate_key=f'{contest}:{i}',source_header_literal=literal,
                                 candidate=name,party_label=party,scope=scope,statewide_votes=sums[i]))
        for r in rows:
            fips=wide[r['county']]['county_fips'];vals=r['values']
            for i,v in enumerate(vals):
                candidates.append(dict(contest=contest,county=r['county'],county_fips=fips,column_index=i,
                    candidate_key=f'{contest}:{i}',source_header_literal=cols[i][0],candidate=cols[i][1],party_label=cols[i][2],
                    scope='reported_Misc_unresolved_writein_validity'if i==n-1 else 'named_ballot_candidate',votes=v,
                    source_key=key,PDF_page=page,text_line_1based=r['line'],raw_line=r['raw_line']))
            total=sum(vals);named=sum(vals[:-1])
            wide[r['county']][contest+'_reported_votes']=total
            wide[r['county']][contest+'_named_votes']=named
            wide[r['county']][contest+'_Misc']=vals[-1]
            controls.append(dict(contest=contest,county=r['county'],county_fips=fips,reported_votes=total,
                named_candidate_votes=named,source_Misc=vals[-1],source_key=key,page=page,line=r['line']))
    registration=[]
    for year in (2020,2022,2024):
        key=f'{year}-registration';text=read(key)
        pattern=re.compile(r'^\s*([A-Za-z ]+?)\s+([\d,]+)\s+([\d,]+)\s+(-?[\d.]+%)\s+([\d,]+)\s+(-?[\d.]+%)\s*$')
        rows=[];totals=[]
        for p,pg in enumerate(text.split('\f'),1):
            for i,line in enumerate(pg.splitlines(),1):
                m=pattern.match(line)
                if not m:continue
                name=m[1].strip()
                if name not in wide and name.upper()!='TOTAL':continue
                row=dict(year=year,county=name,county_fips=wide.get(name,{}).get('county_fips',''),
                    this_month=int(m[2].replace(',','')),last_month=int(m[3].replace(',','')),
                    change_percent_literal=m[4],earlier_reference=int(m[5].replace(',','')),
                    earlier_change_percent_literal=m[6],source_key=key,page=p,line=i,raw_line=line,
                    date_scope=f'November {year}; report does not establish election-day stock or status definition')
                (totals if name.upper()=='TOTAL'else rows).append(row)
        assert len(rows)==36
        for r in rows:
            registration.append(r);wide[r['county']][f'registration_November_{year}_monthly_report']=r['this_month']
        # Printed statewide total may be formatted without percent columns.
        save(OUT/'source'/f'{key}-extracted.json',dict(rows=rows,footer_rows=totals,whole_text_locator=key+'.layout.txt.gz'))
    write_csv(OUT/'county-candidates.csv',candidates)
    write_csv(OUT/'county-controls.csv',controls)
    write_csv(OUT/'monthly-registration.csv',registration)
    save(OUT/'candidate-universe.json',universe)
    save(OUT/'source'/'statewide-footers.json',footers)
    save(OUT/'source'/'county-wide.json',list(wide.values()))
    print({x['contest']:sum(x['values'])for x in footers})

if __name__=='__main__':main()
