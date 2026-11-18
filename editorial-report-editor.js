/* Form and structured rich-content editor for editorial_reports.json. */
window.EditorialReportEditor = (() => {
  const tags = new Set(['p','h3','h4','h5','h6','ul','ol','li','strong','em','s','code','blockquote','br','hr','table','thead','tbody','tr','th','td','a']);
  const el = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text != null) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const safeUrl = value => { try { const u = new URL(value); return /^https?:$/.test(u.protocol) ? u.href : ''; } catch (_) { return ''; } };
  const button = (text, action, className = 'add-link') => {
    const b = el('button', text, className); b.type = 'button'; b.onclick = action; return b;
  };
  let invalid = new Set();
  function validateBlocks(nodes, depth = 0) {
    if (!Array.isArray(nodes) || depth > 32) throw Error('段落必須是陣列，且巢狀不可超過 32 層');
    for (const n of nodes) {
      if (!n || typeof n !== 'object' || Array.isArray(n)) throw Error('節點必須是物件');
      if ('text' in n) { if (typeof n.text !== 'string' || 'tag' in n) throw Error('文字節點格式錯誤'); }
      else {
        if (!tags.has(n.tag)) throw Error(`不支援的標籤：${n.tag}`);
        if (n.tag === 'a' && n.href && !safeUrl(n.href)) throw Error('連結只接受完整 HTTP(S) 網址');
        validateBlocks(n.children || [], depth + 1);
      }
    }
  }
  function append(parent, nodes) {
    for (const n of nodes || []) {
      if ('text' in n) { parent.appendChild(document.createTextNode(n.text)); continue; }
      if (!tags.has(n.tag)) continue;
      const element = el(n.tag === 'a' && !safeUrl(n.href) ? 'span' : n.tag);
      if (n.tag === 'a' && safeUrl(n.href)) { element.href = safeUrl(n.href); element.rel = 'noopener noreferrer'; }
      if (n.tag === 'ol' && Number.isInteger(n.start)) element.start = n.start;
      append(element, n.children); parent.appendChild(element);
    }
  }
  function read(parent) {
    return [...parent.childNodes].flatMap(node => {
      if (node.nodeType === Node.TEXT_NODE) return [{text:node.textContent}];
      if (node.nodeType !== Node.ELEMENT_NODE) return [];
      let tag = node.tagName.toLowerCase();
      if (['script','style','iframe','object'].includes(tag)) return [];
      tag = ({div:'p',b:'strong',i:'em'})[tag] || tag;
      if (!tags.has(tag)) return read(node);
      const value = {tag, children:read(node)};
      if (tag === 'a') {
        if (!safeUrl(node.getAttribute('href'))) return value.children;
        value.href = node.getAttribute('href');
      }
      if (tag === 'ol' && node.start > 1) value.start = node.start;
      return [value];
    });
  }
  function plain(nodes) {
    return (nodes || []).map(n => 'text' in n ? n.text : plain(n.children) +
      (['p','h3','h4','li','tr','blockquote','br','hr'].includes(n.tag) ? '\n' : ['th','td'].includes(n.tag) ? ' | ' : '')).join('');
  }
  function mount({root, list, reports, selected, select, changed, language}) {
    invalid = new Set();
    root.replaceChildren(); list.replaceChildren();
    const notify = () => changed();
    const refresh = () => select(selected);
    const fields = (parent, object, definitions) => {
      const grid = el('div', null, 'field-grid'); parent.appendChild(grid);
      for (const [key, label, type = 'text'] of definitions) {
        const wrap = el('div', null, type === 'textarea' ? 'full' : '');
        const id = `report-field-${Math.random().toString(36).slice(2)}`;
        const caption = el('label', label); caption.htmlFor = id;
        const input = el(type === 'textarea' ? 'textarea' : 'input'); input.id = id;
        input.dataset.reportField = key; input.value = object[key] ?? '';
        if (type !== 'textarea') input.type = type;
        input.oninput = () => { object[key] = type === 'number' ? (input.value ? Number(input.value) : 0) : input.value; notify(); };
        wrap.append(caption, input); grid.appendChild(wrap);
      }
    };
    const card = title => { const section = el('section', null, 'card'); section.appendChild(el('h2', title)); root.appendChild(section); return section; };
    const fail = (input, message) => {
      invalid.add(input); input.setAttribute('aria-invalid', 'true'); input.setCustomValidity(message);
    };
    const pass = input => { invalid.delete(input); input.removeAttribute('aria-invalid'); input.setCustomValidity(''); };
    const add = () => {
      const id = 'report_' + Date.now().toString(36);
      reports.push({id, slug:id, language, title:'新報導', summary:'', status:'draft', published:false,
        isSample:false, reviewStatus:'needs-fact-check', sections:[], photos:[], nearby:[]});
      notify(); select(reports.length - 1);
    };
    list.appendChild(button('＋ 新增採訪報導', add));
    const search = el('input'); search.placeholder = '搜尋報導標題或 ID'; search.setAttribute('aria-label', '搜尋報導');
    search.style.margin = '10px 0'; list.appendChild(search);
    const entries = el('div'); list.appendChild(entries);
    const renderItems = () => {
      entries.replaceChildren();
      reports.forEach((report, index) => {
        if (!`${report.title} ${report.id}`.toLowerCase().includes(search.value.toLowerCase())) return;
        const entry = button(`${report.status === 'published' ? '●' : '○'} ${report.title || report.id}`, () => select(index), 'topic-item' + (selected === index ? ' on' : ''));
        entry.style.cssText = 'width:100%;text-align:left;white-space:normal'; entries.appendChild(entry);
      });
    };
    search.oninput = renderItems; renderItems();
    const report = reports[selected];
    if (!report) { card('台灣吃喝玩樂採訪報導').appendChild(el('p', '目前沒有報導，請按「新增採訪報導」。')); return; }
    const intro = card('台灣吃喝玩樂採訪報導');
    intro.appendChild(el('p', `目前語言：${language}。本次儲存只修改目前語言；其他語言請切換語言分頁編輯。`, 'hint'));
    intro.appendChild(el('p', `固定 ID：${report.id}`, 'mono'));
    const actions = el('div', null, 'toolbar');
    const preview = el('a', '查看前台（請先存檔）', 'jump-btn');
    preview.href = '/preview/report_info.html?' + new URLSearchParams({id:report.id,lang:language === 'zh' ? 'zh-TW' : language});
    preview.target = '_blank'; preview.rel = 'noopener noreferrer'; actions.appendChild(preview);
    const move = delta => { const other = selected + delta; if (other < 0 || other >= reports.length) return;
      [reports[selected], reports[other]] = [reports[other], reports[selected]]; notify(); select(other); };
    actions.append(button('↑ 上移', () => move(-1)), button('↓ 下移', () => move(1)), button('刪除報導', () => {
      if (!confirm(`刪除「${report.title}」？只會刪除目前語言，按存檔後生效。`)) return;
      reports.splice(selected, 1); notify(); select(Math.max(0, selected - 1));
    })); intro.appendChild(actions);
    const statusLabel = el('label', '發布狀態'); const status = el('select'); status.id = 'report-publication-status'; statusLabel.htmlFor = status.id;
    for (const [value,label] of [['published','已發布（前台顯示）'],['draft','草稿（不顯示）'],['archived','封存（不顯示）']]) {
      const option = el('option', label); option.value = value; status.appendChild(option);
    }
    status.value = report.status || 'draft';
    status.onchange = () => { report.status = status.value; report.published = status.value === 'published'; notify(); renderItems(); };
    intro.append(statusLabel, status);
    const reviewLabel=el('label','資料查核狀態'),review=el('select');review.id='report-review-status';reviewLabel.htmlFor=review.id;
    for(const [value,label] of [['needs-fact-check','待查核'],['verified','已查核']]){const option=el('option',label);option.value=value;review.appendChild(option);}
    review.value=report.reviewStatus || 'needs-fact-check';review.onchange=()=>{report.reviewStatus=review.value;notify();};intro.append(reviewLabel,review);
    const sampleLabel = el('label'); const sample = el('input'); sample.type = 'checkbox'; sample.checked = !!report.isSample; sample.style.width = 'auto';
    sample.onchange = () => { report.isSample = sample.checked; notify(); };
    sampleLabel.append(sample, document.createTextNode(' 範例資料（前台顯示範例提示）')); intro.appendChild(sampleLabel);
    fields(card('基本資料'), report, [['title','標題'],['slug','網址代稱 slug'],['summary','摘要','textarea'],['city','城市（住宿搜尋使用，建議保留中文）'],['area','街區／地區'],['author','作者'],['date','日期'],['coverImg','封面圖片網址','url'],['readingTimeMinutes','閱讀分鐘','number'],['editorialNote','編輯／資料查核註記','textarea']]);
    report.seo ||= {};
    fields(card('SEO'), report.seo, [['title','SEO 標題'],['description','SEO 摘要','textarea'],['keywords','關鍵字']]);
    const sections = card('文章段落');
    sections.appendChild(button('＋ 新增段落', () => { (report.sections ||= []).push({heading:'新段落',content:'',blocks:[{tag:'p',children:[{text:'請輸入內容'}]}]}); notify(); refresh(); }));
    (report.sections || []).forEach((section, index) => {
      const panel = el('details', null, 'section-card'); panel.open = index === 0;
      panel.appendChild(el('summary', `${index + 1}. ${section.heading || '未命名段落'}`));
      fields(panel, section, [['heading','段落標題'],['image','段落圖片網址','url'],['caption','圖片說明']]);
      const toolbar = el('div', null, 'menu-editor-toolbar');
      const editor = el('div', null, 'report-body-editor'); editor.contentEditable = 'true'; editor.role = 'textbox'; editor.setAttribute('aria-multiline','true'); editor.setAttribute('aria-label',`第 ${index + 1} 段內文`);
      const initial = Array.isArray(section.blocks) && section.blocks.length ? section.blocks : [{tag:'p',children:[{text:section.content || ''}]}];
      append(editor, initial);
      const source = el('textarea', null, 'menu-source'); source.value = JSON.stringify(initial, null, 2); source.setAttribute('aria-label',`第 ${index + 1} 段結構 JSON`);
      const error = el('p', '', 'report-editor-error'); error.setAttribute('role','alert');
      const update = () => { section.blocks = read(editor); section.content = plain(section.blocks).trim(); source.value = JSON.stringify(section.blocks,null,2); pass(source); error.textContent = ''; notify(); };
      editor.oninput = update;
      editor.addEventListener('click', event => { if (event.target.closest('a')) event.preventDefault(); });
      editor.addEventListener('paste', event => { event.preventDefault(); document.execCommand('insertText', false, event.clipboardData.getData('text/plain')); update(); });
      const command = (label, name, value) => {
        const control = button(label, () => { editor.focus(); document.execCommand(name, false, value); update(); });
        control.onmousedown = e => e.preventDefault(); toolbar.appendChild(control);
      };
      command('粗體','bold'); command('小標題','formatBlock','h3'); command('項目清單','insertUnorderedList'); command('編號清單','insertOrderedList');
      const appendNode = node => { editor.appendChild(node); update(); };
      toolbar.appendChild(button('＋ 段落', () => appendNode(el('p','請輸入內容'))));
      toolbar.appendChild(button('＋ 連結', () => {
        const href = prompt('輸入完整 HTTP(S) 連結'); if (!href) return;
        if (!safeUrl(href)) { alert('連結只接受完整 HTTP(S) 網址'); return; }
        const label = prompt('連結文字', href); if (label === null) return;
        const a = el('a', label || href); a.href = href; appendNode(a);
      }));
      const changeLink = button('修改連結網址', () => {
        const focus = window.getSelection()?.anchorNode;
        const element = focus?.nodeType === Node.ELEMENT_NODE ? focus : focus?.parentElement;
        const anchor = element?.closest('a');
        if (!anchor || !editor.contains(anchor)) { alert('請先將游標放在連結文字內'); return; }
        const href = prompt('修改連結網址',anchor.getAttribute('href'));
        if (href === null) return;
        if (!safeUrl(href)) { alert('連結只接受完整 HTTP(S) 網址'); return; }
        anchor.href=href;update();
      });
      changeLink.onmousedown=e=>e.preventDefault();toolbar.appendChild(changeLink);
      toolbar.appendChild(button('＋ 表格', () => {
        const table = el('table'), head = el('thead'), body = el('tbody'), top = el('tr');
        for (let i=0;i<3;i++) top.appendChild(el('th',`欄位 ${i+1}`)); head.appendChild(top);
        for(let r=0;r<2;r++) { const row=el('tr'); for(let c=0;c<3;c++) row.appendChild(el('td','內容')); body.appendChild(row); }
        table.append(head,body); appendNode(table);
      }));
      toolbar.appendChild(button('＋ 表格列', () => {
        const selection = window.getSelection(); const focus = selection?.anchorNode;
        const cell = focus?.nodeType === Node.ELEMENT_NODE ? focus : focus?.parentElement;
        const table = cell?.closest('table');
        if (!table || !editor.contains(table)) { alert('請先將游標放在要編輯的表格內'); return; }
        const row = el('tr'); for(let c=0;c<(table.rows[0]?.cells.length || 3);c++) row.appendChild(el('td','內容'));
        (table.tBodies[0] || table).appendChild(row); update();
      }));
      toolbar.lastChild.onmousedown = e => e.preventDefault();
      const advanced = el('details',null,'menu-source-details'); advanced.append(el('summary','進階：段落結構 JSON'), source, error);
      source.oninput = () => {
        try { const nodes=JSON.parse(source.value); validateBlocks(nodes); editor.replaceChildren(); append(editor,nodes); section.blocks=nodes; section.content=plain(nodes).trim(); pass(source); error.textContent=''; notify(); }
        catch(e) { fail(source,e.message); error.textContent=e.message; notify(); }
      };
      const sectionActions = el('div',null,'menu-editor-toolbar');
      for (const [label,delta] of [['↑ 上移',-1],['↓ 下移',1]]) sectionActions.appendChild(button(label,()=>{
        const target=index+delta;if(target<0||target>=report.sections.length)return;
        [report.sections[index],report.sections[target]]=[report.sections[target],report.sections[index]];notify();refresh();
      }));
      sectionActions.appendChild(button('刪除此段',()=>{if(confirm('刪除此段落？按存檔後生效。')){report.sections.splice(index,1);notify();refresh();}}));
      panel.append(toolbar,editor,advanced,sectionActions);sections.appendChild(panel);
    });
    const collections = (key, title, definitions, defaults) => {
      const area = card(title);
      area.appendChild(button('＋ 新增', () => { (report[key] ||= []).push({...defaults}); notify(); refresh(); }));
      (report[key] || []).forEach((item,index) => {
        const row = el('div',null,'section-card'); fields(row,item,definitions);
        row.appendChild(button('刪除此筆',()=>{report[key].splice(index,1);notify();refresh();}));area.appendChild(row);
      });
    };
    collections('photos','照片集',[['image','圖片網址','url'],['caption','圖說']],{image:'',caption:''});
    collections('nearby','周邊推薦（前台最多顯示三筆）',[['name','名稱'],['description','介紹','textarea'],['walk','步行距離／時間'],['image','圖片網址','url'],['address','地址'],['mapUrl','地圖網址','url']],{name:'',description:''});
    report.practicalInfo ||= {};
    fields(card('探訪資訊（選填）'),report.practicalInfo,[['name','店家／景點名稱'],['address','地址'],['addressEn','英文地址'],['businessHours','營業時間','textarea'],['mapUrl','地圖網址','url']]);
    const metadata = card('來源與翻譯紀錄');
    metadata.appendChild(el('p', '原始來源與翻譯紀錄會保留，未重新翻譯前不會被標記為已校對。', 'hint'));
    metadata.appendChild(el('pre', JSON.stringify({source:report.source,translation:report.translation,reviewStatus:report.reviewStatus},null,2)));
  }
  function validate() {
    if (invalid.size) { const input = invalid.values().next().value; input.closest('details').open = true; input.focus(); throw Error('段落 JSON 有錯誤，請先修正再存檔'); }
  }
  return {mount,validate,validateBlocks,plain};
})();
