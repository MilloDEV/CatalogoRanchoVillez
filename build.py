#!/usr/bin/env python3
"""Genera index.html a partir de site.json + products.json.
Uso:  python3 build.py
"""
import html, json, math, os, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
esc = html.escape


def load(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return json.load(f)


site = load("site.json")
data = load("products.json")


def star_points(cx, cy, ro, ri, n=5):
    pts = []
    for i in range(n * 2):
        r = ro if i % 2 == 0 else ri
        a = -math.pi / 2 + i * math.pi / n
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


STAR = star_points(0, 0, 10, 4.2)
ICON_STAR = f'<svg class="i-star" viewBox="-11 -11 22 22" aria-hidden="true"><polygon points="{STAR}"/></svg>'
ICON_CHAT = (
    '<svg class="i-chat" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 3h14a3 3 0 0 1 3 3v9a3 3 0 0 1-3 3H10l-5 4v-4a3 3 0 0 1-3-3V6a3 3 0 0 1 3-3Zm3 6v2h8V9H8Zm0 3.500V14h5v-1.500H8Z"/></svg>'
)
ICON_CAM = (
    '<svg class="i-cam" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4 7.500 6H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-3.500L15 4H9Zm3 4.500a4.500 4.500 0 1 1 0 9 4.500 4.500 0 0 1 0-9Zm0 2a2.500 2.500 0 1 0 0 5 2.500 2.500 0 0 0 0-5Z"/></svg>'
)

# Placeholder para productos sin foto: cráneo de toro + estrella
PLACEHOLDER = f"""<svg viewBox="0 0 200 120" aria-hidden="true">
<g fill="currentColor">
<path id="h" d="M92 52 C74 50 52 52 36 44 C24 38 14 28 8 12 C14 30 26 44 40 54 C56 64 76 70 90 68 Z"/>
<use href="#h" transform="translate(200 0) scale(-1 1)"/>
<path fill-rule="evenodd" d="M86 46 Q100 40 114 46 L111 70 Q109 88 100 104 Q91 88 89 70 Z M91 64a3.600 3.600 0 1 0 7.200 0a3.600 3.600 0 1 0 -7.200 0Z M102 64a3.600 3.600 0 1 0 7.200 0a3.600 3.600 0 1 0 -7.200 0Z"/>
<g transform="translate(100 26)"><polygon points="{star_points(0, 0, 11, 4.600)}"/></g>
</g></svg>"""


def money(p):
    cur = esc(site["currency"])
    if p is None:
        return '<span class="price ask">Consultar precio</span>'
    if p == 0:
        return f'<span class="price"><span class="cur">{cur}</span>00.000</span>'
    s = f"{int(p):,}".replace(",", ".")
    return f'<span class="price"><span class="cur">{cur}</span>{s}</span>'


def wa_link(text):
    return f"https://wa.me/{site['whatsapp']}?text=" + urllib.parse.quote(text)


def existing_images(item):
    return [i for i in item.get("images", []) if os.path.exists(os.path.join(ROOT, i))]


def card(item):
    imgs = existing_images(item)
    full_name = item["name"] + (f" ({item['who']})" if item.get("who") else "")
    badge = f'<span class="badge">{esc(item["badge"])}</span>' if item.get("badge") else ""
    opts_list = item.get("options", [])
    opts = "".join(f"<li>{esc(o)}</li>" for o in opts_list)
    opts = f'<ul class="opts">{opts}</ul>' if opts else ""
    who = f'<span class="who">{esc(item["who"])}</span>' if item.get("who") else ""
    msg = f"Hola {site['brand']}, me interesa: {full_name}"
    if opts_list:
        msg += " – " + ", ".join(opts_list)
    focus = f' style="--focus:{esc(item["focus"])}"' if item.get("focus") else ""
    if imgs:
        n = len(imgs)
        count = f'<span class="count">{ICON_CAM}{n}</span>' if n > 1 else ""
        photo = (f'<span class="photo"{focus}><img src="{esc(imgs[0])}" alt="{esc(full_name)}" loading="lazy">{count}</span>')
        thumbs = "".join(
            f'<li><img src="{esc(i)}" alt="" loading="lazy"></li>' for i in imgs[1:5]
        )
        thumbs = f'<ul class="thumbs" aria-hidden="true">{thumbs}</ul>' if thumbs else ""
        data_imgs = f" data-imgs='{esc(json.dumps(imgs), quote=False)}'"
        label = f"Ver fotos de {esc(full_name)}"
    else:
        photo = f'<span class="photo ph">{PLACEHOLDER}<span class="soon">Foto próximamente</span></span>'
        thumbs = ""
        data_imgs = ""
        label = esc(full_name)
    return f"""
      <article class="card"{data_imgs}>
        <i class="nail"></i>{badge}
        <button class="open" type="button" aria-label="{label}">
          {photo}
          {who}
          <h3>{esc(item['name'])}</h3>
        </button>
        <p class="desc">{esc(item.get('desc', ''))}</p>
        {opts}
        {thumbs}
        <div class="foot">{money(item.get('price'))}
          <a class="btn-order" href="{wa_link(msg)}" target="_blank" rel="noopener">{ICON_CHAT}Pedir</a>
        </div>
      </article>"""


chips = "".join(f'<a href="#{c["id"]}">{esc(c["name"])}</a>' for c in data["categories"])

steps = "".join(
    f'<li><b class="num">{i + 1}</b><div><h3>{esc(s["t"])}</h3><p>{esc(s["d"])}</p></div></li>'
    for i, s in enumerate(site["steps"])
)

wa_hello = wa_link(f"Hola {site['brand']}, quisiera más información")
contact_lines = f"""
        <li><span>WhatsApp</span><a href="{wa_hello}" target="_blank" rel="noopener">{esc(site['whatsapp_display'])}</a></li>
        <li><span>Instagram</span><b>{esc(site['instagram'])}</b></li>
        <li><span>Facebook</span><b>{esc(site['facebook'])}</b></li>
        <li><span>Ubicación</span><b>{esc(site['location'])}</b></li>"""


def cat_block(cat, items, cont):
    cards = "".join(card(i) for i in items)
    cls = "cat cont" if cont else "cat"
    ident = "" if cont else f' id="{cat["id"]}"'
    cont_tag = f'<span class="cont-tag"> · continuación</span>' if cont else ""
    return f"""
    <section class="{cls}"{ident}>
      <div class="wire" aria-hidden="true"></div>
      <h2 class="sign">{esc(cat['name'])}{cont_tag}</h2>
      <p class="blurb">{esc(cat.get('blurb', ''))}</p>
      <div class="grid">{cards}
      </div>
    </section>"""


HOWTO = f"""
    <section class="howto" id="como-pedir">
      <div class="wire" aria-hidden="true"></div>
      <h2 class="sign">¿Cómo pedir?</h2>
      <ol>{steps}</ol>
    </section>"""

END = f"""
  <footer class="end" id="contacto">
    <div class="wire" aria-hidden="true"></div>
    <p class="end-brand">{ICON_STAR}{esc(site['brand'])}{ICON_STAR}</p>
    <p class="end-tag">{esc(site['tagline'])}</p>
    <ul class="contact">{contact_lines}
    </ul>
    <a class="btn primary big" href="{wa_hello}" target="_blank" rel="noopener">{ICON_CHAT}Escribinos por WhatsApp</a>
    <p class="fine">© 2026 {esc(site['brand'])} · Precios sujetos a cambio</p>
  </footer>"""

# ---- Empaquetado de páginas para el PDF (alturas estimadas en pulgadas) ----
CAP, HEAD, HEAD_CONT, CARD, W_HOWTO, W_END = 10.0, 1.02, 0.64, 2.72, 2.1, 2.7
pages, used = [[]], 0.0


def new_page():
    global used
    pages.append([])
    used = 0.0


for cat in data["categories"]:
    items, first = list(cat["items"]), True
    while items:
        head = HEAD if first else HEAD_CONT
        k = int((CAP - used - head) // CARD)
        if k < 1:
            if used == 0:
                k = 1
            else:
                new_page()
                continue
        pages[-1].append(cat_block(cat, items[:k], not first))
        used += head + min(k, len(items)) * CARD
        items, first = items[k:], False
if used + W_HOWTO + W_END > CAP:
    new_page()
pages[-1].append(HOWTO)
used += W_HOWTO
if used + W_END > CAP:
    new_page()
pages[-1].append(END)

body_pages = "".join(f'\n  <div class="page">{"".join(p)}\n  </div>' for p in pages)

LIGHTBOX = f"""
<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Fotos del producto" hidden>
  <div class="lb-back" data-close></div>
  <div class="lb-box">
    <button class="lb-x" type="button" data-close aria-label="Cerrar">&times;</button>
    <div class="lb-media">
      <div class="lb-stage">
        <button class="lb-nav prev" type="button" aria-label="Foto anterior">&#8249;</button>
        <img class="lb-img" alt="">
        <button class="lb-nav next" type="button" aria-label="Foto siguiente">&#8250;</button>
        <span class="lb-count"></span>
      </div>
      <div class="lb-thumbs"></div>
    </div>
    <div class="lb-info">
      <p class="lb-who"></p>
      <h3 class="lb-name"></h3>
      <p class="lb-desc"></p>
      <ul class="lb-opts"></ul>
      <div class="lb-foot"><span class="lb-price"></span>
        <a class="btn primary lb-order" target="_blank" rel="noopener">{ICON_CHAT}Pedir por WhatsApp</a></div>
    </div>
  </div>
</div>"""

SCRIPT = """
<script>
(function () {
  /* --- Menú de categorías: resalta la sección visible --- */
  var nav = document.querySelector('.chips');
  var links = [].slice.call(nav.querySelectorAll('a'));
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (l) {
          var on = l.getAttribute('href') === '#' + e.target.id;
          l.classList.toggle('on', on);
          if (on) nav.scrollTo({ left: l.offsetLeft - nav.clientWidth / 2 + l.offsetWidth / 2, behavior: 'smooth' });
        });
      });
    }, { rootMargin: '-35% 0px -55% 0px' });
    document.querySelectorAll('.cat[id]').forEach(function (s) { io.observe(s); });
  }

  /* --- Galería de fotos --- */
  var lb = document.getElementById('lb');
  var img = lb.querySelector('.lb-img');
  var thumbsEl = lb.querySelector('.lb-thumbs');
  var countEl = lb.querySelector('.lb-count');
  var prev = lb.querySelector('.prev'), next = lb.querySelector('.next');
  var imgs = [], idx = 0, name = '', lastFocus = null;

  function show(i) {
    idx = (i + imgs.length) % imgs.length;
    img.src = imgs[idx];
    img.alt = name + ' – foto ' + (idx + 1) + ' de ' + imgs.length;
    countEl.textContent = (idx + 1) + ' / ' + imgs.length;
    [].forEach.call(thumbsEl.children, function (t, n) {
      t.classList.toggle('on', n === idx);
      if (n === idx) thumbsEl.scrollTo({ left: t.offsetLeft - thumbsEl.clientWidth / 2 + t.offsetWidth / 2, behavior: 'smooth' });
    });
    [idx + 1, idx - 1].forEach(function (n) { var p = new Image(); p.src = imgs[(n + imgs.length) % imgs.length]; });
  }

  function open(card) {
    imgs = JSON.parse(card.getAttribute('data-imgs'));
    var who = card.querySelector('.who');
    name = card.querySelector('h3').textContent + (who ? ' (' + who.textContent + ')' : '');
    lb.querySelector('.lb-who').textContent = who ? who.textContent : '';
    lb.querySelector('.lb-name').textContent = card.querySelector('h3').textContent;
    lb.querySelector('.lb-desc').textContent = card.querySelector('.desc').textContent;
    lb.querySelector('.lb-opts').innerHTML = (card.querySelector('.opts') || { innerHTML: '' }).innerHTML;
    lb.querySelector('.lb-price').innerHTML = card.querySelector('.price').outerHTML;
    lb.querySelector('.lb-order').href = card.querySelector('.btn-order').href;
    thumbsEl.innerHTML = '';
    imgs.forEach(function (src, n) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', 'Ver foto ' + (n + 1));
      b.innerHTML = '<img src="' + src + '" alt="" loading="lazy">';
      b.addEventListener('click', function () { show(n); });
      thumbsEl.appendChild(b);
    });
    var multi = imgs.length > 1;
    prev.hidden = next.hidden = countEl.hidden = thumbsEl.hidden = !multi;
    lastFocus = document.activeElement;
    lb.hidden = false;
    document.body.classList.add('lb-open');
    show(0);
    lb.querySelector('.lb-x').focus();
  }

  function close() {
    lb.hidden = true;
    document.body.classList.remove('lb-open');
    if (lastFocus) lastFocus.focus();
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest('.open');
    if (b) { open(b.closest('.card')); return; }
    if (e.target.closest('[data-close]')) close();
  });
  prev.addEventListener('click', function () { show(idx - 1); });
  next.addEventListener('click', function () { show(idx + 1); });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft' && imgs.length > 1) show(idx - 1);
    else if (e.key === 'ArrowRight' && imgs.length > 1) show(idx + 1);
    else if (e.key === 'Tab') {
      var f = [].filter.call(lb.querySelectorAll('button,a[href]'), function (x) { return !x.hidden && x.offsetParent !== null; });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  /* deslizar con el dedo */
  var sx = null;
  lb.querySelector('.lb-stage').addEventListener('touchstart', function (e) { sx = e.touches[0].clientX; }, { passive: true });
  lb.querySelector('.lb-stage').addEventListener('touchend', function (e) {
    if (sx === null || imgs.length < 2) return;
    var dx = e.changedTouches[0].clientX - sx; sx = null;
    if (Math.abs(dx) > 45) show(idx + (dx < 0 ? 1 : -1));
  }, { passive: true });
})();
</script>"""

first_img = next((i for c in data["categories"] for it in c["items"] for i in existing_images(it)), None)

page = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(site['brand'])} · Catálogo de accesorios vaqueros</title>
<meta name="description" content="{esc(site['tagline'])}. Catálogo de {esc(site['brand'])}.">
<meta name="theme-color" content="#140b05">
<meta property="og:title" content="{esc(site['brand'])} · Catálogo">
<meta property="og:description" content="{esc(site['tagline'])}">
<meta property="og:image" content="assets/img/hero.jpg">
<link rel="preload" href="assets/fonts/rye-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top">
  <div class="bar">
    <a class="brand" href="#inicio">{ICON_STAR}<span>{esc(site['brand'])}</span>{ICON_STAR}</a>
    <a class="wa-mini" href="{wa_hello}" target="_blank" rel="noopener">{ICON_CHAT}<span>WhatsApp</span></a>
  </div>
  <nav class="chips" aria-label="Categorías">{chips}</nav>
</header>

<main id="inicio">
  <section class="hero">
    <h1 class="sr">{esc(site['brand'])}</h1>
    <img src="assets/img/hero.jpg" width="1536" height="1024" alt="Logo de {esc(site['brand'])} sobre un atardecer en el rancho">
    <div class="hero-copy">
      <p class="kicker">{esc(site['kicker'])}</p>
      <p class="tag">{esc(site['tagline'])}</p>
      <p class="intro">{esc(site['intro'])}</p>
      <div class="cta">
        <a class="btn primary" href="#{data['categories'][0]['id']}">Ver catálogo</a>
        <a class="btn ghost" href="{wa_hello}" target="_blank" rel="noopener">{ICON_CHAT}Escribinos</a>
      </div>
      <p class="cover-index" aria-hidden="true">{" ★ ".join(esc(c["name"]) for c in data["categories"])}</p>
      <div class="cover-contact" aria-hidden="true">
        <div class="wire"></div>
        <ul>{contact_lines}
        </ul>
      </div>
    </div>
  </section>
{body_pages}
</main>
{LIGHTBOX}
{SCRIPT}
</body>
</html>
"""

OUT = os.environ.get("OUT", "index.html")
with open(os.path.join(ROOT, OUT), "w", encoding="utf-8") as f:
    f.write(page)
open(os.path.join(ROOT, ".nojekyll"), "w").close()
print(OUT, "listo —", sum(len(c["items"]) for c in data["categories"]), "productos,", len(pages), "páginas de contenido en el PDF")
