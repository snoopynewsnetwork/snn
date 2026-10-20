/* Offline file:// supported: no network, fetch, eval or external library. */
'use strict';
function filterUnits(data,query,parent,scope,order){
 const q=query.toLocaleLowerCase('en-US');
 return data.units.filter(u=>(!parent||u.parent_literal===parent)&&(scope==='all'||(scope==='priority'?u.in_priority:u.in_remainder))&&(!q||JSON.stringify(u.full_source_object).toLocaleLowerCase('en-US').includes(q))).sort((a,b)=>order==='source'?a.full_source_object.csv_record_ordinal-b.full_source_object.csv_record_ordinal:a.rank-b.rank);
}
if(typeof module!=='undefined')module.exports={filterUnits};
if(typeof document!=='undefined'){
const $=id=>document.getElementById(id), pre=value=>{const p=document.createElement('pre');p.textContent=JSON.stringify(value,null,2);return p;};
for(const p of ATLAS.parents){const o=document.createElement('option');o.value=p.parent_literal;o.textContent=p.parent_literal; $('parent').append(o);}
$('contract').textContent=JSON.stringify(CONTRACT,null,2);$('hierarchy').textContent=JSON.stringify(ATLAS.source_parent_objects,null,2);$('gis').textContent=JSON.stringify(GIS,null,2);
function draw(){const parent=$('parent').value,rows=filterUnits(ATLAS,$('search').value,parent,$('scope').value,$('order').value);$('count').textContent=rows.length+' matching source contexts';$('rows').replaceChildren();$('parentDetail').replaceChildren();
if(parent){const p=ATLAS.parents.find(p=>p.parent_literal===parent);if(p.native_context.preview){const img=document.createElement('img');img.src=p.native_context.preview;img.alt=parent+' historical native-coordinate geographic context; no result crosswalk';$('parentDetail').append(img);}const d=document.createElement('details'),s=document.createElement('summary');s.textContent='Complete parent authority, acquisition, full child arrays and specific gaps';d.append(s,pre(p));$('parentDetail').append(d);if(p.municipal_chain){const a=document.createElement('a');a.href=p.municipal_chain.complete_chain_object_path;a.textContent='Complete municipal chain object: all source text / literal links / receipts';$('parentDetail').append(a,document.createElement('br'));}for(const m of p.state_published_maps){if(m.complete_pdf){const a=document.createElement('a');a.href='pdf-review/'+m.raw_sha256+'/document.json';a.textContent=m.name+' original receipt and page renders';$('parentDetail').append(a,document.createElement('br'));}}}
for(const u of rows){const r=u.full_source_object,tr=document.createElement('tr');for(const value of [r.rank,...r.literal_tuple,r.votes]){const td=document.createElement('td');td.textContent=value;tr.append(td);}const td=document.createElement('td'),d=document.createElement('details'),s=document.createElement('summary');s.textContent=(u.in_priority?'Priority':'Remainder')+' / complete source object';d.append(s,pre(u));td.append(d);tr.append(td);$('rows').append(tr);}}
for(const id of ['search','parent','scope','order'])$(id).addEventListener('input',draw);draw();
}
