'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const base=__dirname,ctx={window:{}};vm.createContext(ctx);
for(const f of ['contract.js','gis-objects.js','atlas-data.js'])vm.runInContext(fs.readFileSync(path.join(base,f),'utf8'),ctx);
const a=ctx.window.ATLAS,c=ctx.window.CONTRACT,g=ctx.window.GIS,filterCtx={module:{exports:{}}};
vm.createContext(filterCtx);vm.runInContext(fs.readFileSync(path.join(base,'atlas.js'),'utf8'),filterCtx);const {filterUnits}=filterCtx.module.exports;
assert.equal(a.units.length,2394);assert.equal(a.parents.length,351);assert.equal(Object.keys(c).length,25);assert.equal(g.wards.length,2256);assert.equal(g.subprecinct.length,147);
assert.equal(filterUnits(a,'','','priority','rank').length,1470);assert.equal(filterUnits(a,'','','remainder','rank').length,924);
assert.deepEqual(Array.from(filterUnits(a,'','','all','rank'),u=>u.full_source_object.native_key),Array.from(a.rank_order));assert.deepEqual(Array.from(filterUnits(a,'','','all','source'),u=>u.full_source_object.native_key),Array.from(a.original_source_order));
let sums=0;for(const p of a.parents){const rows=filterUnits(a,'',p.parent_literal,'all','rank');sums+=rows.length;assert.deepEqual(Array.from(rows,u=>u.full_source_object.native_key),Array.from(p.canonical_rank_ordered_children));for(const u of rows)assert.equal(JSON.stringify(u.full_source_object),JSON.stringify(c.all_unit_order[u.rank-1]));}assert.equal(sums,2394);
assert.equal(filterUnits(a,'not-a-real-town-unique-xx','','all','rank').length,0);assert.equal(filterUnits(a,'Northampton','Northampton','priority','rank').filter(u=>u.full_source_object.literal_tuple[1]==='3'&&u.full_source_object.literal_tuple[2]==='B').length,1);
// Execute the actual DOM path with a minimal DOM, checking event-driven filtering and text nodes.
class E{constructor(){this.children=[];this.value='';this.textContent='';this.handlers={};}append(...v){this.children.push(...v);}replaceChildren(...v){this.children=v;}addEventListener(k,f){this.handlers[k]=f;}}
const els={};for(const id of ['search','parent','scope','order','rows','count','parentDetail','contract','hierarchy','gis'])els[id]=new E();els.scope.value='all';els.order.value='rank';const document={getElementById:id=>els[id],createElement:()=>new E()};const run={window:ctx.window,ATLAS:a,CONTRACT:c,GIS:g,document};vm.createContext(run);vm.runInContext(fs.readFileSync(path.join(base,'atlas.js'),'utf8'),run);assert.equal(els.rows.children.length,2394);assert.equal(els.parent.children.length,351);els.scope.value='remainder';els.scope.handlers.input();assert.equal(els.rows.children.length,924);els.parent.value='Nantucket';els.scope.value='all';els.parent.handlers.input();assert.equal(els.rows.children.length,1);assert.equal(els.count.textContent,'1 matching source contexts');
assert(!fs.readFileSync(path.join(base,'atlas.js'),'utf8').includes('innerHTML'));
console.log(JSON.stringify({status:'pass',fullobjects:2394,parents:351,priority:1470,remainder:924,all_parent_filters:true,source_and_rank_orders:true,actual_dom_execution:true,full_source_objects_equal:true,network:false}));

const fixture=JSON.parse(fs.readFileSync(path.join(base,'atlas-escaping-fixture.json'),'utf8'));assert(!fixture.encoded.includes('<'));assert(!fixture.encoded.includes(String.fromCharCode(8232)));const fx={};vm.createContext(fx);vm.runInContext('value='+fixture.encoded,fx);assert.equal(fx.value,fixture.literal);
