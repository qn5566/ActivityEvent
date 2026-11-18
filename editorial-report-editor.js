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
  function mount({root, list, reports, selected, select, changed, language, kind='reports', restaurants=[], requestedRestaurantId=null, openRestaurant}) {
    const michelin=kind==='michelin',title=michelin?'米其林餐廳專刊':'台灣吃喝玩樂採訪報導';
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
      const available=restaurants.filter(r=>!reports.some(a=>a.restaurantId===r.id));
      const restaurant=michelin?(available.find(r=>r.id===requestedRestaurantId)||available[0]):null;
      if(michelin&&!restaurant){alert('所有餐廳都已建立文章，請在列表選擇既有文章編輯。');return;}
      const id = 'report_' + Date.now().toString(36);
      reports.push({id, slug:id, language, title:'新報導', summary:'', status:'draft', published:false,
        isSample:false, reviewStatus:'needs-fact-check', sections:[], photos:[], nearby:[],
        ...(michelin?{restaurantId:restaurant.id,title:restaurant.name,menuVariants:[],honors:{years:[]}}:{})});
      notify(); select(reports.length - 1);
    };
    list.appendChild(button(michelin?'＋ 新增餐廳文章':'＋ 新增採訪報導', add));
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
    if (!report) { const name=restaurants.find(r=>r.id===requestedRestaurantId)?.name;card(title).appendChild(el('p',michelin?(name?`「${name}」在目前語言尚未建立文章，請按「新增餐廳文章」。`:'目前沒有餐廳文章，請按「新增餐廳文章」。'):'目前沒有報導，請按「新增採訪報導」。')); return; }
    const intro = card(title);
    intro.appendChild(el('p', `目前語言：${language}。本次儲存只修改目前語言；其他語言請切換語言分頁編輯。`, 'hint'));
    intro.appendChild(el('p', `固定 ID：${report.id}`, 'mono'));
    const actions = el('div', null, 'toolbar');
    const preview = el('a', '查看前台（請先存檔）', 'jump-btn');
    preview.href = `/preview/${michelin?'michelin_info':'report_info'}.html?` + new URLSearchParams({id:michelin?report.restaurantId:report.id,lang:language === 'zh' ? 'zh-TW' : language});
    preview.target = '_blank'; preview.rel = 'noopener noreferrer'; actions.appendChild(preview);
    if(michelin && openRestaurant){
      actions.appendChild(button('🍽️ 前往對應餐廳 →', () => openRestaurant(report.restaurantId), 'jump-btn'));
    }
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
    if(michelin){
      const caption=el('label','對應餐廳（固定 ID，不依排名）'),restaurant=el('select');restaurant.id='article-restaurant';caption.htmlFor=restaurant.id;
      for(const item of restaurants){const option=el('option',`${item.name} · ${item.id}`);option.value=item.id;option.disabled=reports.some(a=>a!==report&&a.restaurantId===item.id);restaurant.appendChild(option);}
      restaurant.value=report.restaurantId || '';restaurant.onchange=()=>{report.restaurantId=restaurant.value;notify();preview.href=`/preview/michelin_info.html?`+new URLSearchParams({id:report.restaurantId,lang:language==='zh'?'zh-TW':language});};intro.append(caption,restaurant);
      fields(card('餐廳專刊資訊'),report,[['enTitle','外文名稱'],['bookingUrl','官網訂位網址','url'],['coverImageRole','封面性質：illustration 示意／photo 實拍'],['menuNote','菜單／服務費說明','textarea']]);
      const lineField=(parent,object,key,label)=>{const caption=el('label',label),input=el('textarea');input.value=(object[key]||[]).join('\n');input.oninput=()=>{object[key]=input.value.split('\n').map(v=>v.trim()).filter(Boolean);notify();};parent.append(caption,input);};
      lineField(intro,report,'quickFacts','餐廳重點（每行一筆）');
      report.honors||={years:[]};const honors=card('歷年獲獎紀錄');fields(honors,report.honors,[['heading','紀錄標題'],['content','說明','textarea'],['note','紀錄期間／查核說明','textarea']]);lineField(honors,report.honors,'years','獲獎年份（每行一筆，例如 2025 ★★★）');
      const menu=card('多語招牌菜單');
      menu.appendChild(button('＋ 新增菜單語言',()=>{const languages=['zh','en','ja','ko','es','th','vi','ms','fil','hi','id','de'];const language=languages.find(l=>!(report.menuVariants||[]).some(v=>v.language===l));if(!language)return;(report.menuVariants||=[]).push({language,title:language,items:[]});notify();refresh();}));
      (report.menuVariants||[]).forEach((variant,index)=>{
        const panel=el('details',null,'section-card');panel.open=index===0;panel.appendChild(el('summary',`${variant.language} · ${variant.items.length} 道菜`));
        fields(panel,variant,[['language','語言代碼（zh、en、ja 等）'],['title','菜單標題']]);
        for(const [i,item] of variant.items.entries()){const row=el('div',null,'section-card');fields(row,item,[['name','菜名'],['price','價格（文字）'],['description','菜色說明','textarea']]);row.appendChild(button('刪除此道菜',()=>{variant.items.splice(i,1);notify();refresh();}));panel.appendChild(row);}
        panel.append(button('＋ 新增菜色',()=>{variant.items.push({id:'dish_'+Date.now().toString(36),name:'新菜色',description:'',price:''});notify();refresh();}),button('刪除此語言菜單',()=>{if(confirm('刪除此語言菜單？')){report.menuVariants.splice(index,1);notify();refresh();}}));menu.appendChild(panel);
      });
    }
    const sections = card('文章段落');
    sections.appendChild(button('＋ 新增段落', () => { (report.sections ||= []).push({heading:'新段落',content:'',blocks:[{tag:'p',children:[{text:'請輸入內容'}]}]}); notify(); refresh(); }));
    (report.sections || []).forEach((section, index) => {
      const panel = el('details', null, 'section-card'); panel.open = index === 0;
      panel.appendChild(el('summary', `${index + 1}. ${section.heading || '未命名段落'}`));
      fields(panel, section, [['heading','段落標題'],['image','段落圖片網址','url'],['caption','圖片說明']]);
      if(michelin){
        const caption=el('label','段落版型'),layout=el('select');layout.setAttribute('aria-label',`第 ${index+1} 段版型`);
        for(const [value,label]of[['intro','餐廳故事'],['ambiance','空間氛圍'],['dish','招牌菜色'],['guide','用餐須知']]){const option=el('option',label);option.value=value;layout.appendChild(option);}layout.value=section.layout||'intro';layout.onchange=()=>{section.layout=layout.value;notify();};panel.append(caption,layout);
        fields(panel,section,[['imageRole','圖片性質：illustration 示意／photo 實拍']]);
      }
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
    if(!michelin)collections('nearby','周邊推薦（前台最多顯示三筆）',[['name','名稱'],['description','介紹','textarea'],['walk','步行距離／時間'],['image','圖片網址','url'],['address','地址'],['mapUrl','地圖網址','url']],{name:'',description:''});
    report.practicalInfo ||= {};
    fields(card('探訪資訊（選填）'),report.practicalInfo,[['name','店家／景點名稱'],['address','地址'],['addressEn','英文地址'],['businessHours','營業時間','textarea'],['phone','電話'],['transport','交通說明','textarea'],['mapUrl','地圖網址','url']]);
    const metadata = card('來源與翻譯紀錄');
    metadata.appendChild(el('p', '原始來源與翻譯紀錄會保留，未重新翻譯前不會被標記為已校對。', 'hint'));
    metadata.appendChild(el('pre', JSON.stringify({source:report.source,translation:report.translation,reviewStatus:report.reviewStatus},null,2)));
  }
  function validate() {
    if (invalid.size) { const input = invalid.values().next().value; input.closest('details').open = true; input.focus(); throw Error('段落 JSON 有錯誤，請先修正再存檔'); }
  }
  return {mount,validate,validateBlocks,plain};
})();
