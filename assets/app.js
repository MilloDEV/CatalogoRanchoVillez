/* Rancho Villéz · filtros, pedido personalizado y entrada de cantina */
(function () {
  'use strict';
  var body = document.body;
  var WA = body.getAttribute('data-wa') || '';
  var BRAND = body.getAttribute('data-brand') || '';
  var root = document.documentElement;

  /* ---------- Entrada de cantina ---------- */
  var sal = document.querySelector('.saloon');
  if (sal) {
    var finished = false;
    var finish = function () {
      if (finished) return;
      finished = true;
      root.classList.remove('rv-intro');
      try { sessionStorage.setItem('rv_intro', '1'); } catch (e) {}
    };
    if (root.classList.contains('rv-intro')) {
      sal.addEventListener('click', function () {
        sal.classList.add('skip');
        setTimeout(finish, 260);
      });
      sal.addEventListener('animationend', function (e) { if (e.target === sal) finish(); });
      setTimeout(finish, 4200); /* seguro por si algo falla */
    }
  }

  /* ---------- Filtros ---------- */
  var cards = [].slice.call(document.querySelectorAll('.card[data-q]'));
  var cats = [].slice.call(document.querySelectorAll('.cat[data-products]'));
  var combos = document.querySelector('.combos');
  var qEl = document.getElementById('q');
  if (qEl && cards.length) {
    var whoSel = '', brandSel = '';
    var countEl = document.getElementById('fcount');
    var clearEl = document.getElementById('fclear');
    var emptyEl = document.getElementById('fempty');

    var norm = function (s) {
      return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    };
    var esc = function (t) { return t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); };
    var tokenRe = function (t) {
      var e = esc(t);
      if (t.length > 2) return new RegExp(e);
      if (/^\d+$/.test(t)) return new RegExp('(^|[^0-9])' + e + '(?![0-9])');
      return new RegExp('(^|[^a-z0-9])' + e + '($|[^a-z0-9])');
    };

    var apply = function () {
      var tokens = norm(qEl.value).split(/\s+/).filter(Boolean).map(tokenRe);
      var shown = 0;
      cards.forEach(function (c) {
        var w = c.getAttribute('data-who');
        var ok = (!whoSel || w === whoSel || w === 'Unisex') &&
                 (!brandSel || c.getAttribute('data-brand') === brandSel);
        if (ok) {
          var hay = c.getAttribute('data-q');
          for (var i = 0; i < tokens.length; i++) { if (!tokens[i].test(hay)) { ok = false; break; } }
        }
        c.hidden = !ok;
        if (ok) shown++;
      });
      cats.forEach(function (s) { s.hidden = !s.querySelector('.card:not([hidden])'); });
      var active = !!(whoSel || brandSel || qEl.value.trim());
      if (combos) combos.hidden = active;
      countEl.textContent = (shown === cards.length ? cards.length : shown + ' de ' + cards.length) + ' productos';
      clearEl.hidden = !active;
      emptyEl.hidden = shown !== 0;
    };

    var group = function (name, setter) {
      var g = document.querySelector('.fgroup[data-group="' + name + '"]');
      if (!g) return;
      g.addEventListener('click', function (e) {
        var b = e.target.closest('.fchip');
        if (!b) return;
        [].forEach.call(g.querySelectorAll('.fchip'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        setter(b.getAttribute('data-' + name) || '');
        apply();
      });
    };
    group('who', function (v) { whoSel = v; });
    group('brand', function (v) { brandSel = v; });
    qEl.addEventListener('input', apply);
    clearEl.addEventListener('click', function () {
      whoSel = brandSel = ''; qEl.value = '';
      [].forEach.call(document.querySelectorAll('.fgroup'), function (g) {
        [].forEach.call(g.querySelectorAll('.fchip'), function (x, i) { x.setAttribute('aria-pressed', i === 0 ? 'true' : 'false'); });
      });
      apply();
    });
    var go = document.getElementById('fempty-go');
    if (go) go.addEventListener('click', function () {
      var f = document.getElementById('ppform');
      if (f && qEl.value.trim() && !f.what.value) f.what.value = qEl.value.trim();
    });
  }

  /* ---------- Pedido personalizado → WhatsApp ---------- */
  var form = document.getElementById('ppform');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = function (n) { return (form.elements[n].value || '').trim(); };
      var lines = ['Hola ' + BRAND + ', quiero hacer un pedido personalizado:', '• Busco: ' + v('what')];
      if (v('brand')) lines.push('• Marca o modelo: ' + v('brand'));
      if (v('size')) lines.push('• Talla: ' + v('size'));
      if (v('color')) lines.push('• Color: ' + v('color'));
      window.open('https://wa.me/' + WA + '?text=' + encodeURIComponent(lines.join('\n')), '_blank', 'noopener');
    });
  }
})();
