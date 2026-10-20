// Actual generated atlas script evaluated offline with a minimal DOM test harness.
// This is a functional JS check, explicitly not a browser/visual claim.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const file=path.join(__dirname,'atlas.html'),html=fs.readFileSync(file,'utf8');
const script=html.match(/<script>([\s\S]*)<\/script>/)[1];
const elements={};
function element(id){if(!elements[id])elements[id]={value:({mode:'priority',authority:'',query:''}[id]||''),children:[],options:[],add(o){this.options.push(o)},set innerHTML(v){this.content=v;if(id==='rows')this.children=[...v.matchAll(/data-rank="(\d+)"/g)].map(m=>({dataset:{rank:m[1]}}));},get innerHTML(){return this.content}};return elements[id];}
const sandbox={document:{getElementById:element},Option:function(label,value){this.label=label;this.value=value}};vm.createContext(sandbox);vm.runInContext(script,sandbox);
function evaluate(code){return vm.runInContext(code,sandbox)}
assert.equal(element('rows').children.length,5540);assert.equal(element('authority').options.length,108);
const full=JSON.parse(require('zlib').gunzipSync(fs.readFileSync(path.join(__dirname,'derived/full-inventory.json.gz'))));assert.deepStrictEqual(JSON.parse(JSON.stringify(evaluate('records.map(r=>r.source_observation)'))),full.map(r=>r.source_observation));
assert.equal(evaluate('records.length'),10062);assert.equal(evaluate('parents.length'),108);
for(const [mode,count] of [['all',10062],['remainder',4522],['priority',5540]]){element('mode').value=mode;element('mode').oninput();assert.equal(element('rows').children.length,count);}
assert.equal(evaluate('records[5539].label'),'O FALLON 3');assert.equal(evaluate('records[5539].votes'),523);
element('authority').value='105';element('mode').value='all';element('mode').oninput();const expected=evaluate('records.filter(r=>r.authority==="105").length');assert.equal(element('rows').children.length,expected);
element('rows').children[0].onclick();assert(element('detail').innerHTML.includes('physical polygon: null'));assert.equal(element('preview').src,'derived/previews/17031.svg');
element('query').value='a-label-that-does-not-exist';element('query').oninput();assert.equal(element('rows').children.length,0);
assert.equal(evaluate('esc("<script>&\\\"\\\'")'),'&lt;script&gt;&amp;&quot;&#39;');
const result={status:'pass',scope:'generated JavaScript evaluated with minimal DOM; no browser or visual claim',priority_rows:5540,full_rows:10062,remainder_rows:4522,parent_options:108,exact_crossing:true,city_filter:true,empty_filter:true,detail_and_local_preview:true,html_escaping:true,all_complete_source_observation_objects:true};
fs.writeFileSync(path.join(__dirname,'qa/atlas-js-check.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
