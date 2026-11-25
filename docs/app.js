/* Original, dependency-free profile renderer. The source data remain immutable. */
(() => {
  'use strict';
  const data = window.CIRCLE_DATA;
  const $ = id => document.getElementById(id);
  const status = message => { $('app-status').textContent = message; };
  if (!data || !Array.isArray(data.indicators) || data.indicators.length !== 28) {
    $('criterion-detail').innerHTML = '<p class="error-box">Nepavyko įkelti 28 rodiklių. Patikrinkite, ar failas indicators.js yra tame pačiame aplanke.</p>';
    $('criterion').disabled = true;
    return;
  }
  const items = data.indicators;
  const countries = {taiwan:'Taivanas',china:'Kinija'};
  const fallbackPalette = ['#d95b55','#e47756','#ed975f','#f2b76f','#eed48a','#c6d49b','#9ec6a1','#70b19b','#409982'];
  const palette = Array.isArray(data.palette) && data.palette.length === 9 ? data.palette : fallbackPalette;
  const onColor = color => {
    const hex=String(color).replace('#','');
    if(!/^[0-9a-f]{6}$/i.test(hex)) return '#142d43';
    const rgb=[0,2,4].map(offset=>parseInt(hex.slice(offset,offset+2),16)/255).map(value=>value<=.04045?value/12.92:((value+.055)/1.055)**2.4);
    const luminance=.2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2];
    return 1.05/(luminance+.05)>=4.5?'#ffffff':'#000000';
  };
  const escape = value => String(value ?? '').replace(/[&<>"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
  const validUrl = value => { try { const url = new URL(String(value)); return ['http:','https:'].includes(url.protocol) ? url.href : null; } catch { return null; } };
  const link = (url, label, className = '') => validUrl(url) ? `<a class="${className}" href="${escape(validUrl(url))}" target="_blank" rel="noopener noreferrer">${escape(label)} ↗</a>` : `<span>${escape(label)}</span>`;
  const number = value => typeof value === 'number' ? new Intl.NumberFormat('lt-LT',{maximumFractionDigits:2}).format(value) : String(value ?? 'Nenurodyta');
  const year = value => value === null || value === undefined ? 'metai nenurodyti' : `${value} m.`;
  const numericScore = (item, country) => Number(item.scores[country]);
  if (items.some(item => !item.scores || Object.keys(countries).some(country => !Number.isInteger(numericScore(item,country)) || numericScore(item,country)<1 || numericScore(item,country)>9))) {
    $('criterion-detail').innerHTML = '<p class="error-box">Rodiklių balai turi būti sveikieji skaičiai nuo 1 iki 9. Duomenų failą reikia patikrinti.</p>';
    $('criterion').disabled = true;
    return;
  }
  let selected = 0;
  let scenario = false;
  let scenarioScores = items.map(item => ({taiwan:numericScore(item,'taiwan'),china:numericScore(item,'china')}));
  const currentScore = (index,country) => scenario ? scenarioScores[index][country] : numericScore(items[index],country);
  const domainNames = [...new Set(items.map(item => item.domain))];
  const groups = domainNames.map(name => ({name,indices:items.map((item,index)=>item.domain===name?index:-1).filter(index=>index>=0)}));
  const years = items.flatMap(item=>Object.keys(countries).map(country=>Number(item[country]?.year))).filter(value=>Number.isFinite(value)&&value>1900&&value<2200);
  const yearRange = years.length ? `${Math.min(...years)}–${Math.max(...years)} m.` : 'Skirtingi ataskaitiniai laikotarpiai';
  $('data-period').textContent = `Rodiklių laikotarpis: ${yearRange}`;
  if (data.updated) $('updated').textContent = `Atnaujinta: ${data.updated}`;
  if (validUrl(data.source_url)) $('circle-source').href = validUrl(data.source_url);
  if (typeof data.method === 'string' && validUrl(data.method)) $('method-link').href = validUrl(data.method);
  $('score-legend').innerHTML = palette.map((color,index)=>`<li style="background:${escape(color)};color:${onColor(color)}" aria-label="${index+1} balas">${index+1}</li>`).join('');
  $('domain-key').innerHTML = groups.map(group=>`<li><span class="range">${String(group.indices[0]+1).padStart(2,'0')}–${String(group.indices.at(-1)+1).padStart(2,'0')}</span><span>${escape(group.name)}</span></li>`).join('');
  $('criterion').innerHTML = groups.map(group=>`<optgroup label="${escape(group.name)}">${group.indices.map(index=>`<option value="${index}">${String(index+1).padStart(2,'0')} · ${escape(items[index].indicator)}</option>`).join('')}</optgroup>`).join('');

  const center = 360, innerRadius = 34, outerRadius = 266, labelRadius = 300;
  const point = (radius,angle) => [center+radius*Math.cos(angle),center+radius*Math.sin(angle)];
  const pair = point => point.map(value=>value.toFixed(3)).join(' ');
  const ringPath = (inner,outer,start,end) => `M ${pair(point(outer,start))} A ${outer} ${outer} 0 0 1 ${pair(point(outer,end))} L ${pair(point(inner,end))} A ${inner} ${inner} 0 0 0 ${pair(point(inner,start))} Z`;
  const angle = index => -Math.PI/2 + index * 2*Math.PI/items.length;
  const wheelContents = (country,exporting = false) => {
    let output = `<circle cx="360" cy="360" r="${outerRadius}" fill="#fff"/>`;
    items.forEach((item,index) => {
      const start=angle(index), end=angle(index+1), score=currentScore(index,country);
      const middle=(start+end)/2, label=point(labelRadius,middle);
      output += `<g class="sector${selected===index&&!exporting?' is-selected':''}" data-index="${index}"><title>${escape(`${String(index+1).padStart(2,'0')}. ${item.indicator}: ${score} iš 9. ${scenario?'Scenarijus.':'Duomenų balas.'}`)}</title>`;
      for(let level=1;level<=9;level++) {
        const r0=innerRadius+(outerRadius-innerRadius)*(level-1)/9, r1=innerRadius+(outerRadius-innerRadius)*level/9;
        output += `<path data-index="${index}" data-level="${level}" d="${ringPath(r0,r1,start,end)}" fill="${level<=score?escape(palette[score-1]):'#ffffff'}" stroke="#d4dce0" stroke-width="0.7"/>`;
      }
      output += `<path class="sector-selection" d="${ringPath(innerRadius,outerRadius,start,end)}" fill="none" stroke="${!exporting&&selected===index?'#142d43':'none'}" stroke-width="3" pointer-events="none"/><text class="criterion-number" x="${label[0].toFixed(3)}" y="${label[1].toFixed(3)}" text-anchor="middle" dominant-baseline="middle" font-family="Arial,sans-serif" font-size="18" fill="#536572">${String(index+1).padStart(2,'0')}</text></g>`;
    });
    groups.forEach(group=>{const a=angle(group.indices[0]);output+=`<path d="M ${pair(point(innerRadius,a))} L ${pair(point(outerRadius+5,a))}" stroke="#607581" stroke-width="1.7" fill="none" pointer-events="none"/>`;});
    output += `<circle cx="360" cy="360" r="${innerRadius-1}" fill="#fff"/><text x="360" y="363" text-anchor="middle" dominant-baseline="middle" font-family="Arial,sans-serif" font-size="22" fill="#536572">1–9</text>`;
    return output;
  };
  function renderWheel(country) {
    const title=`${countries[country]}: ${scenario?'demonstracinis scenarijus':'28 rodiklių duomenų profilis'}`;
    $(`wheel-${country}`).innerHTML=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 720" role="img" aria-labelledby="svg-title-${country} svg-desc-${country}"><title id="svg-title-${country}">${escape(title)}</title><desc id="svg-desc-${country}">28 sektoriai, po 9 žiedus. Sektoriaus numeris atitinka žemiau esantį kriterijų sąrašą. Abiejų šalių reikšmės ir balai prieinami pasirinkus kriterijų sąraše.</desc>${wheelContents(country)}</svg>`;
    resizeLabels(country);
  }
  function resizeLabels(country) {
    const container=$(`wheel-${country}`), width=container.getBoundingClientRect().width;
    const size=width>0?Math.max(18,14*720/width):18;
    container.querySelectorAll('.criterion-number').forEach(label=>label.setAttribute('font-size',String(size)));
  }
  function updateHighlights() {
    for(const country of Object.keys(countries)) $(`wheel-${country}`).querySelectorAll('.sector').forEach(sector=>{
      const active=Number(sector.dataset.index)===selected;
      sector.classList.toggle('is-selected',active);
      sector.querySelector('.sector-selection').setAttribute('stroke',active?'#142d43':'none');
    });
  }
  function updateDetails() {
    const item=items[selected], benchmark=item.benchmark||{};
    const direction=['lower','negative','decrease','mažiau'].includes(String(item.direction).toLowerCase())?'↓ Mažesnė reikšmė palankesnė':'↑ Didesnė reikšmė palankesnė';
    $('criterion-counter').textContent=`${String(selected+1).padStart(2,'0')} / ${items.length}`;
    $('criterion').value=String(selected);
    $('criterion-detail').innerHTML=`<h3 class="detail-title">${escape(item.indicator)}</h3><div class="value-grid">${Object.entries(countries).map(([country,name])=>{
      const observation=item[country]||{}, actual=numericScore(item,country), shown=currentScore(selected,country);
      return `<article class="value-card"><h3>${name} · ${escape(year(observation.year))}</h3><div class="raw-value">${escape(number(observation.value))}</div><p class="value-unit">${escape(item.unit)}</p><div class="score-row"><span>Duomenų balas</span><span class="score-badge" style="background:${escape(palette[actual-1])};color:${onColor(palette[actual-1])}">${actual} / 9</span></div>${scenario?`<div class="score-row" style="margin-top:10px"><span>Scenarijaus balas</span><span class="score-badge" style="background:${escape(palette[shown-1])};color:${onColor(palette[shown-1])}">${shown} / 9</span></div>`:''}${link(observation.source,observation.source_title||'Pirminis šaltinis','source-link')}</article>`;
    }).join('')}</div><dl class="fact-list"><div><dt>Vertinimo kryptis</dt><dd>${direction}</dd></div><div><dt>Atskaitos imtis</dt><dd>${escape(number(benchmark.n))} ekonomikų</dd></div><div><dt>Atskaitos metai</dt><dd>${escape(benchmark.year??'Nurodyti šaltinyje')}</dd></div><div><dt>Imties mažiausia reikšmė</dt><dd>${escape(number(benchmark.min))}</dd></div><div><dt>Imties didžiausia reikšmė</dt><dd>${escape(number(benchmark.max))}</dd></div><div><dt>Imties duomenys</dt><dd>${link(benchmark.source,'Atverti šaltinį')}</dd></div></dl>${benchmark.scope?`<p class="reference-scope"><strong>Imties apimtis.</strong> ${escape(benchmark.scope)}</p>`:''}${item.note?`<p class="note"><strong>Palyginamumas.</strong> ${escape(item.note)}</p>`:''}${item.score_note?`<p class="note"><strong>Balo interpretacija.</strong> ${escape(item.score_note)}</p>`:''}`;
    for(const country of Object.keys(countries)) {
      $(`scenario-${country}`).value=scenarioScores[selected][country];
      $(`scenario-${country}`).setAttribute('aria-label',`${countries[country]}: ${item.indicator}, scenarijaus balas`);
      $(`output-${country}`).value=`${scenarioScores[selected][country]} / 9`;
      $(`output-${country}`).textContent=`${scenarioScores[selected][country]} / 9`;
    }
  }
  function selectCriterion(index) {
    if(!Number.isInteger(index)||index<0||index>=items.length) return;
    selected=index; updateHighlights(); updateDetails();
  }
  function setScenarioScore(country,value) {
    scenarioScores[selected][country]=Math.min(9,Math.max(1,Number(value)));
    renderWheel(country); updateDetails();
  }
  $('criterion').addEventListener('change',event=>selectCriterion(Number(event.target.value)));
  for(const country of Object.keys(countries)) {
    const container=$(`wheel-${country}`);
    container.addEventListener('pointerover',event=>{
      if(event.pointerType==='touch') return;
      const sector=event.target.closest('[data-index]');
      if(sector&&Number(sector.dataset.index)!==selected) selectCriterion(Number(sector.dataset.index));
    });
    container.addEventListener('click',event=>{
      const sector=event.target.closest('[data-index]'); if(!sector) return;
      selectCriterion(Number(sector.dataset.index));
      if(scenario&&sector.dataset.level) setScenarioScore(country,sector.dataset.level);
    });
    $(`scenario-${country}`).addEventListener('input',event=>setScenarioScore(country,event.target.value));
    renderWheel(country);
  }
  if('ResizeObserver' in window) {
    const observer=new ResizeObserver(entries=>entries.forEach(entry=>resizeLabels(entry.target.id.replace('wheel-',''))));
    Object.keys(countries).forEach(country=>observer.observe($(`wheel-${country}`)));
  } else window.addEventListener('resize',()=>Object.keys(countries).forEach(resizeLabels));
  $('scenario').addEventListener('change',event=>{
    scenario=event.target.checked;
    $('scenario-banner').hidden=!scenario; $('scenario-controls').hidden=!scenario;
    document.querySelectorAll('.mode-pill').forEach(pill=>{pill.textContent=scenario?'Scenarijus':'Duomenų profilis';pill.classList.toggle('is-scenario',scenario);});
    Object.keys(countries).forEach(renderWheel);updateDetails();
    status(scenario?'Įjungtas demonstracinis scenarijus. Diagramos rodo scenarijaus balus.':'Rodomi duomenimis apskaičiuoti profiliai.');
  });
  $('reset-scenario').addEventListener('click',()=>{
    scenarioScores=items.map(item=>({taiwan:numericScore(item,'taiwan'),china:numericScore(item,'china')}));
    Object.keys(countries).forEach(renderWheel);updateDetails();status('Visi scenarijaus balai atkurti pagal duomenų profilį.');
  });

  function exportSvg(country) {
    const mode=scenario?'SCENARIJUS – ne faktinis vertinimas':'DUOMENŲ PROFILIS';
    const labels=groups.map((group,index)=>`<text x="${index%2===0?42:378}" y="${886+Math.floor(index/2)*28}" font-size="16" fill="#142d43">${escape(`${String(group.indices[0]+1).padStart(2,'0')}–${String(group.indices.at(-1)+1).padStart(2,'0')} ${group.name}`)}</text>`).join('');
    const legend=palette.map((color,index)=>`<rect x="${42+index*71}" y="956" width="67" height="30" rx="3" fill="${escape(color)}"/><text x="${75+index*71}" y="977" text-anchor="middle" font-size="16" font-weight="bold" fill="${onColor(color)}">${index+1}</text>`).join('');
    const scoreKey=items.map((item,index)=>`<text x="${42+Math.floor(index/7)*165}" y="${1132+(index%7)*28}" font-size="16" fill="#142d43">${escape(`${String(index+1).padStart(2,'0')} · ${item.id} · ${currentScore(index,country)}/9`)}</text>`).join('');
    return `<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="2800" viewBox="0 0 720 1400" font-family="Arial,sans-serif"><title>${escape(`${countries[country]} · ${mode} · ${yearRange}`)}</title><desc>28 rodiklių profilis. Devyni vienodo pločio atskaitos imčių intervalai. Šis profilis nėra oficialus DVT reitingas. Apačioje pateiktas sektorių numerių, kriterijų kodų ir rodomų balų raktas.</desc><rect width="720" height="1400" fill="#fff"/><text x="42" y="50" font-size="14" letter-spacing="1.5" fill="#536572">DARNIOS RAIDOS PROFILIAI</text><text x="42" y="104" font-size="42" font-weight="bold" fill="#142d43">${countries[country]}</text><text x="42" y="137" font-size="17" fill="${scenario?'#9a5900':'#536572'}">${escape(`${yearRange} · ${mode}`)}</text><g transform="translate(0 143)">${wheelContents(country,true)}</g>${labels}${legend}<text x="42" y="1015" font-size="16" fill="#536572">1 – santykinai nepalankiau · 9 – santykinai palankiau</text><text x="42" y="1041" font-size="14" fill="#536572">9 vienodo pločio imties intervalai; ne oficialios būklės kategorijos.</text><line x1="42" x2="678" y1="1072" y2="1072" stroke="#dce3e6"/><text x="42" y="1102" font-size="16" font-weight="bold" fill="#142d43">Sektorius · kriterijaus kodas · ${scenario?'scenarijaus':'duomenų'} balas</text>${scoreKey}<text x="42" y="1340" font-size="14" fill="#536572">Kriterijų pavadinimai, metai, pirminės reikšmės ir šaltiniai:</text><text x="42" y="1364" font-size="14" fill="#536572">github.com/PovilasJan/taiwan-china-storymaps</text></svg>`;
  }
  function download(blob,filename) {
    const url=URL.createObjectURL(blob), anchor=document.createElement('a');
    anchor.href=url;anchor.download=filename;document.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);
  }
  async function exportProfile(country,format,button) {
    button.disabled=true;
    const svg=exportSvg(country), filename=`${country}-${scenario?'scenarijus':'duomenu-profilis'}`;
    try {
      if(format==='svg') download(new Blob([svg],{type:'image/svg+xml;charset=utf-8'}),`${filename}.svg`);
      else {
        const blob=new Blob([svg],{type:'image/svg+xml;charset=utf-8'}), url=URL.createObjectURL(blob);
        try {
          const image=new Image();image.decoding='async';
          await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(new Error('Nepavyko parengti vaizdo.'));image.src=url;});
          const canvas=document.createElement('canvas');canvas.width=1440;canvas.height=2800;
          const context=canvas.getContext('2d');if(!context) throw new Error('Naršyklė nepalaiko PNG eksporto.');
          context.drawImage(image,0,0,1440,2800);
          const png=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
          if(!png) throw new Error('Nepavyko sukurti PNG.');
          download(png,`${filename}.png`);
        } finally {URL.revokeObjectURL(url);}
      }
      status(`${countries[country]}: parengtas ${format.toUpperCase()} (${scenario?'scenarijus':'duomenų profilis'}).`);
    } catch(error) {status(`Eksportas nepavyko: ${error.message} Galite bandyti SVG formatą.`);}
    finally {button.disabled=false;}
  }
  document.querySelectorAll('[data-export]').forEach(button=>button.addEventListener('click',()=>exportProfile(button.dataset.export,button.dataset.format,button)));
  updateDetails();
})();
