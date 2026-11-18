/** Text/table-only menu HTML, shared with the ActivityEvent editor. */
(function (root) {
  const allowed = new Set(['P', 'BR', 'DIV', 'SPAN', 'STRONG', 'B', 'EM', 'I', 'U', 'S', 'SMALL', 'H3', 'H4', 'UL', 'OL', 'LI', 'TABLE', 'CAPTION', 'THEAD', 'TBODY', 'TFOOT', 'TR', 'TH', 'TD', 'HR']);
  const blocked = new Set(['SCRIPT', 'STYLE', 'IFRAME', 'OBJECT', 'EMBED', 'SVG', 'MATH', 'TEMPLATE', 'FORM', 'INPUT', 'BUTTON', 'TEXTAREA', 'SELECT', 'LINK', 'META', 'BASE', 'NOSCRIPT']);
  const classes = new Set(['menu-row', 'm-name', 'm-desc', 'm-price']);
  function sanitize(value, doc = document) {
    const source = doc.createElement('template');
    source.innerHTML = typeof value === 'string' ? value : '';
    const result = doc.createElement('div');
    function append(node, parent) {
      if (node.nodeType === 3) { parent.appendChild(doc.createTextNode(node.textContent)); return; }
      if (node.nodeType !== 1 || blocked.has(node.tagName) || node.namespaceURI !== 'http://www.w3.org/1999/xhtml') return;
      if (!allowed.has(node.tagName)) { for (const child of node.childNodes) append(child, parent); return; }
      const clean = doc.createElement(node.tagName.toLowerCase());
      const kept = [...node.classList].filter(name => classes.has(name));
      if (kept.length) clean.className = kept.join(' ');
      if (['TD', 'TH'].includes(node.tagName)) {
        for (const name of ['colspan', 'rowspan']) {
          const count = Number(node.getAttribute(name));
          if (Number.isInteger(count) && count > 1 && count <= 20) clean.setAttribute(name, String(count));
        }
      }
      for (const child of node.childNodes) append(child, clean);
      parent.appendChild(clean);
    }
    for (const node of source.content.childNodes) append(node, result);
    return result.textContent.trim() ? result.innerHTML : '';
  }
  root.CafeMenuHtml = { sanitize };
})(globalThis);
