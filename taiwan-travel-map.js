/**
 * 台灣吃喝玩樂地圖 (Taiwan Travel Map) - WordPress 獨立 JavaScript
 * 
 * 使用方式：
 * 1. 可複製至 WordPress 的「自訂外觀」->「自訂 JS」、佈景主題 footer.php，
 *    或使用 WPCode / Simple Custom CSS and JS 等外掛載入。
 * 2. 亦可在文章底部以 <script src=".../taiwan-travel-map.js"></script> 載入。
 * 
 * 特色：
 * - 純原生 JavaScript，零外部依賴套件。
 * - 嚴格作用於 #twfun-top，絕不干擾 WordPress 既有外掛與主題樣式。
 * - 支援現代平滑捲動無障礙焦點跳轉、自動更新年份、桌面手機視差微互動、FAQ 展開反饋。
 */
(function () {
  'use strict';

  function initTaiwanTravelMap() {
    var root = document.getElementById('twfun-top');
    if (!root) return;

    // 1. 頁內導覽平滑捲動，保留鍵盤與螢幕閱讀器可用性
    root.querySelectorAll('a[href^="#"]').forEach(function (link) {
      link.addEventListener('click', function (event) {
        var href = link.getAttribute('href');
        if (!href || href === '#') return;
        var target = document.getElementById(href.slice(1));
        if (!target) return;
        event.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        if (!target.hasAttribute('tabindex')) {
          target.setAttribute('tabindex', '-1');
        }
        target.focus({ preventScroll: true });
      });
    });

    // 2. 每年自動更新頁尾年份，避免內容過期
    var footer = root.querySelector('.twfun-footer p');
    if (footer) {
      var currentYear = new Date().getFullYear();
      footer.textContent = footer.textContent.replace(/©\s*\d{4}/, '© ' + currentYear);
    }

    // 3. 現代旗艦機樣機 3D 微視差懸浮互動（僅在支援游標懸停的桌面裝置啟用）
    var phoneFrame = root.querySelector('.twfun-phone-frame');
    if (phoneFrame && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      var hero = root.querySelector('.twfun-polaroid-hero');
      if (hero) {
        hero.addEventListener('mousemove', function (e) {
          var rect = hero.getBoundingClientRect();
          var x = e.clientX - rect.left - rect.width / 2;
          var y = e.clientY - rect.top - rect.height / 2;
          var rotateY = (x / rect.width) * 14;
          var rotateX = -(y / rect.height) * 14;
          phoneFrame.style.transform = 'perspective(900px) rotateX(' + rotateX.toFixed(2) + 'deg) rotateY(' + rotateY.toFixed(2) + 'deg) translateY(-6px)';
        });
        hero.addEventListener('mouseleave', function () {
          phoneFrame.style.transform = '';
        });
      }
    }

    // 4. FAQ 點擊微互動反饋
    var faqItems = root.querySelectorAll('.twfun-faq-item');
    faqItems.forEach(function (item) {
      item.style.cursor = 'pointer';
      item.addEventListener('click', function () {
        faqItems.forEach(function (other) {
          if (other !== item) other.classList.remove('is-active');
        });
        item.classList.toggle('is-active');
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTaiwanTravelMap);
  } else {
    initTaiwanTravelMap();
  }
})();
