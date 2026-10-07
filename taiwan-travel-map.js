/**
 * 台灣吃喝玩樂地圖 landing page
 * 只作用於 #twfun-top，適合在 WordPress 頁面另行載入。
 */
(function () {
  'use strict';

  function initTaiwanTravelMap() {
    var root = document.getElementById('twfun-top');
    if (!root) return;

    // 頁內導覽平滑捲動；保留鍵盤與螢幕閱讀器可用性。
    root.querySelectorAll('a[href^="#"]').forEach(function (link) {
      link.addEventListener('click', function (event) {
        var target = document.getElementById(link.getAttribute('href').slice(1));
        if (!target) return;
        event.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: true });
      });
    });

    // 每年自動更新頁尾年份，避免內容過期。
    var footer = root.querySelector('.twfun-footer p');
    if (footer) footer.textContent = footer.textContent.replace(/©\s*\d{4}/, '© ' + new Date().getFullYear());
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTaiwanTravelMap);
  } else {
    initTaiwanTravelMap();
  }
})();
