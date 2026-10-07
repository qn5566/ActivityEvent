/** 台灣吃喝玩樂地圖原始落地頁互動 */
(function () {
  'use strict';
  function init() {
    var root = document.querySelector('.twfun-landing#twfun-top');
    if (!root) return;
    root.classList.add('twfun-js');
    var items = root.querySelectorAll('.twfun-reveal');
    if (!('IntersectionObserver' in window)) {
      items.forEach(function (item) { item.classList.add('twfun-visible'); });
      return;
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('twfun-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    items.forEach(function (item) { observer.observe(item); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
