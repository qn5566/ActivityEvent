/** Visual menu editor. Persist only sanitized HTML; keep each language independent. */
(function (root) {
  function markup() {
    return `<div class="card cafe-menu-editor">
      <h2>☕ 招牌菜單 menuHtml</h2>
      <p class="hint">直接點選下方表格編輯品項、介紹與價格。僅儲存目前語言；留白時前台隱藏此語言菜單。</p>
      <div class="menu-editor-toolbar">
        <button type="button" data-menu-action="add">＋ 新增品項</button>
        <button type="button" data-menu-action="remove">刪除選取列</button>
        <button type="button" data-menu-action="bold">粗體</button>
      </div>
      <div class="menu-visual-editor" contenteditable="true" role="textbox" aria-label="菜單內容" aria-multiline="true"></div>
      <details class="menu-source-details"><summary>編輯 HTML 原始碼</summary>
        <label>menuHtml<textarea class="menu-source" spellcheck="false" aria-label="菜單 HTML 原始碼"></textarea></label>
      </details>
      <h3>菜單預覽</h3>
      <iframe class="menu-editor-preview" sandbox="" title="菜單預覽"></iframe>
    </div>`;
  }
  function mount(container, article, onChange) {
    const editor = container.querySelector('.menu-visual-editor');
    const source = container.querySelector('.menu-source');
    const preview = container.querySelector('.menu-editor-preview');
    const sanitize = value => CafeMenuHtml.sanitize(value);
    const previewStyle = 'body{font:14px/1.7 system-ui;color:#231f1d;padding:12px;background:#faf8f5;overflow-wrap:anywhere}table{width:100%;table-layout:fixed;border-collapse:collapse}th,td{padding:12px 6px;border-bottom:1px dotted #d8d0c5;text-align:left;vertical-align:top}tr>:last-child:not(:first-child){width:30%;text-align:right;color:#b85233}small,.m-desc{display:block;font-size:12px;color:#6e655f}.menu-row{display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px dotted #d8d0c5}';
    function showPreview(html) {
      preview.srcdoc = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>${previewStyle}</style></head><body>${html}</body></html>`;
    }
    function update(html, origin) {
      const clean = sanitize(html);
      article.menuHtml = clean;
      if (origin !== 'visual') editor.innerHTML = clean;
      if (origin !== 'source') source.value = clean;
      showPreview(clean);
      onChange();
    }
    editor.innerHTML = sanitize(article.menuHtml);
    source.value = editor.innerHTML;
    showPreview(editor.innerHTML);
    editor.addEventListener('input', () => update(editor.innerHTML, 'visual'));
    source.addEventListener('input', () => update(source.value, 'source'));
    source.addEventListener('blur', () => { source.value = article.menuHtml || ''; });
    editor.addEventListener('paste', event => {
      event.preventDefault();
      const html = event.clipboardData.getData('text/html');
      const text = document.createElement('p'); text.textContent = event.clipboardData.getData('text/plain');
      document.execCommand('insertHTML', false, sanitize(html || text.outerHTML));
      update(editor.innerHTML, 'visual');
    });
    editor.addEventListener('drop', event => event.preventDefault());
    container.querySelectorAll('[data-menu-action]').forEach(button => {
      button.addEventListener('mousedown', event => event.preventDefault());
      button.addEventListener('click', () => {
        const action = button.dataset.menuAction;
        if (action === 'add') {
          let body = editor.querySelector('tbody');
          if (!body) {
            const table = document.createElement('table');
            table.innerHTML = '<thead><tr><th>品項 / 介紹</th><th>價格</th></tr></thead><tbody></tbody>';
            editor.appendChild(table); body = table.tBodies[0];
          }
          const row = body.insertRow();
          row.insertCell().innerHTML = '<strong>品項名稱</strong><br><small>品項介紹</small>';
          row.insertCell().textContent = '依現場菜單';
          editor.focus();
          const range = document.createRange(); range.selectNodeContents(row.cells[0]);
          const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
        } else {
          const anchor = window.getSelection()?.anchorNode;
          const element = anchor?.nodeType === 1 ? anchor : anchor?.parentElement;
          if (!element || !editor.contains(element)) return;
          if (action === 'remove') {
            const row = element.closest('tbody tr');
            if (!row) return;
            const table = row.closest('table'); row.remove();
            if (!table.querySelector('tbody tr')) table.remove();
          } else if (action === 'bold') document.execCommand('bold');
        }
        update(editor.innerHTML, 'visual');
      });
    });
  }
  root.CafeMenuEditor = { markup, mount };
})(globalThis);
