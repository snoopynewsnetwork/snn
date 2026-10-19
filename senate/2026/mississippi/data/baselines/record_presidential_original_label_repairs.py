"""Own original printed candidate labels, never identity from row order alone."""
import json
from sources import OUT,BASE,save,sha
# Source-y reading points inside the actually printed candidate's label.
# These are original-image targeting readings, not exact typographic boxes.
READINGS={1:('Chase Oliver',589),2:('Donald J. Trump',801),3:('Shiva Ayyadurai',869),4:('Claudia De la Cruz',940),5:('Peter Sonski',1064),6:('Kamala D. Harris',523),7:('Peter Sonski',1058),8:('Peter Sonski',1133),9:('Robert F. Kennedy Jr.',985),10:('Donald J. Trump',790),11:('Randall Terry',738),12:('Chase Oliver',638),13:('Shiva Ayyadurai',610),14:('Robert F. Kennedy Jr.',710),15:('Kamala D. Harris',520),16:('Chase Oliver',585),17:('Jill Stein',650),18:('Randall Terry',718),19:('Donald J. Trump',785),20:('Shiva Ayyadurai',850),21:('Claudia De la Cruz',920),22:('Robert F. Kennedy Jr.',985),23:('Peter Sonski',1050),24:('Kamala D. Harris',521)}
READINGS.update({25:('Kamala D. Harris',520),26:('Chase Oliver',585),27:('Jill Stein',650),28:('Randall Terry',718),29:('Donald J. Trump',785),30:('Shiva Ayyadurai',850),31:('Claudia De la Cruz',920),32:('Robert F. Kennedy Jr.',985),33:('Peter Sonski',1050),34:('Donald J. Trump',760),35:('Donald J. Trump',790),36:('Kamala D. Harris',560)})
READINGS.update({37:('Randall Terry',780),38:('Donald J. Trump',845),39:('Peter Sonski',1055),40:('Peter Sonski',1053),41:('Claudia De la Cruz',980),42:('Kamala D. Harris',531),43:('Jill Stein',650),44:('Randall Terry',699),45:('Kamala D. Harris',532),46:('Claudia De la Cruz',919)})
def main():
    pointers=json.loads((OUT/'source/presidential-original-label-repair-pointers-v9.json').read_text());rows=[]
    for r in pointers:
        if r['card'] not in READINGS:continue
        label,y=READINGS[r['card']];assert label==r['candidate'];evidence=OUT/'qa'/f'presidential-original-label-repair-v9-atlas-{(r["card"]-1)//6+1}.png';rows.append(r|dict(accepted_source_candidate_name=label,manual_original_label_y=y,basis='Printed source candidate name actually read in original crop; margin source-y scale supplies an approximate interior reading point, not inferred from expected candidate ordinal or any vote/control.',evidence_path=str(evidence.relative_to(BASE)),evidence_sha256=sha(evidence.read_bytes())))
    save(OUT/'source/presidential-original-label-manual-readings.json',dict(qualification='Original source candidate-label readings only, no numeric field acceptance or current geography. Unreviewed card identities remain unresolved.',readings=rows,unreviewed_cards=[r['card'] for r in pointers if r['card'] not in READINGS]));print(len(rows),'candidate-label original readings;',len(pointers)-len(rows),'remaining')
if __name__=='__main__':main()
