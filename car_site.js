// filter/sort for car site (data-* driven)
window.addEventListener('DOMContentLoaded', () => {
  const cards = [...document.querySelectorAll('.card')];
  const home = cards.map(c => c.getBoundingClientRect().top + window.scrollY);
  const qEl = document.getElementById('q'), mkEl = document.getElementById('fmake'),
        srcEl = document.getElementById('fsource'), selEl = document.getElementById('fseller'),
        sortEl = document.getElementById('fsort'), grpEl = document.getElementById('fgroup'),
        cntEl = document.getElementById('cnt');

  const fill = (el, key) => {
    [...new Set(cards.map(c => c.dataset[k]).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'ar'))
      .forEach(v => { const o = document.createElement('option'); o.value = v; o.textContent = v; el.appendChild(o); });
  };
  fill(mkEl,'make'); fill(srcEl,'source'); fill(selEl,'seller');

  // numeric year chip extraction for sorting
  const yearOf = c => { const m = c.querySelector('.tag'); /* transmission first */ 
    const chips = [...c.querySelectorAll('.tag')].map(t=>t.textContent);
    const y = chips.map(x=>x.match(/\b(19\d{2}|20\d{2})\b/)).find(Boolean);
    return y ? +y[1] : 0; };
  const kmOf = c => { const m = (c.dataset.desc+ ' ' + c.textContent).match(/(\d{2,3})\s*(?:ألف|الف)|(\d{3},\d{3})\s*km|(\d{6})\s*كم|(\d{3})\s*ألف/); 
    if (m) { if (m[1]) return +m[1]*1000; if (m[2]) return +m[2].replace(/,/g,''); if (m[3]) return +m[3]; if(m[4]) return +m[4]*1000; }
    return 1e12; };

  function currentList(){
    const q = (qEl.value||'').trim().toLowerCase().split(/\s+/).filter(Boolean);
    const fm=mkEl.value, fs=srcEl.value, fsel=selEl.value;
    let list = cards.filter(c=>{
      if (fm && c.dataset.make !== fm) return false;
      if (fs && c.dataset.source !== fs) return false;
      if (fsel && (c.dataset.seller||'') !== fsel) return false;
      if (q.length){ const hay = ((c.dataset.desc||'')+' '+(c.dataset.seller||'')+' '+c.textContent).toLowerCase();
        if (!q.every(w=>hay.includes(w))) return false; }
      return true;
    });
    const p = c => +c.dataset.price || 1e12;
    const cmp = {
      'price-asc': (a,b)=>p(a)-p(b),
      'price-desc':(a,b)=>p(b)-p(a),
      'year-desc':(a,b)=>yearOf(b)-yearOf(a),
      'year-asc': (a,b)=>yearOf(a)-yearOf(b),
      'km-asc':   (a,b)=>kmOf(a)-kmOf(b),
    }[sortEl.value];
    if (cmp) list.sort(cmp);
    return list;
  }

  function apply(){
    const list = currentList();
    const grp = grpEl.checked;
    // hide/show in natural order first
    cards.forEach(c => c.style.display = list.includes(c) ? '' : 'none');
    document.querySelectorAll('h2[data-make]').forEach(h => {
      const kids = list.filter(c => c.dataset.make === h.dataset.make);
      h.style.display = kids.length ? '' : 'none';
    });
    if (grp){
      // re-group: for each make section, pull its matching cards directly under its h2
      document.querySelectorAll('h2[data-make]').forEach(h => {
        const mkName = h.dataset.make;
        const kids = list.filter(c => c.dataset.make === mkName);
        let anchor = h;
        kids.forEach(c => { anchor.insertAdjacentElement('afterend', c); anchor = c; });
      });
    } else {
      // restore original positional order: sort by initial y
      cards.filter(c=>c.style.display!=='none').sort((a,b)=>0).forEach(()=>{});
      window.__orig && document.querySelectorAll('h2[data-make]').forEach(h=>{
        const kids = cards.filter(c=>c.dataset.make===h.dataset.make);
        let a=h; kids.forEach(c=>{a.insertAdjacentElement('afterend',c);a=c;});
      });
    }
    cntEl.textContent = `${list.length} نتيجة`;
  }
  [qEl,mkEl,srcEl,selEl,sortEl,grpEl].forEach(el => el.addEventListener(el.tagName==='INPUT'&&(el.type==='search')?'input':'change', apply));
  apply();
});
