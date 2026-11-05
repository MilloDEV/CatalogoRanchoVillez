#!/usr/bin/env python3
"""Genera index.html a partir de site.json + products.json.
Uso:  python3 build.py
"""
import html, json, math, os, random, unicodedata, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
esc = html.escape


def load(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return json.load(f)


site = load("site.json")
data = load("products.json")
combos_data = load("combos.json") if os.path.exists(os.path.join(ROOT, "combos.json")) else {"combos": []}
PREVIEW = os.environ.get("PREVIEW") == "1"   # PREVIEW=1 muestra también los combos marcados como borrador
by_id = {it["id"]: it for c in data["categories"] for it in c["items"] if it.get("id")}


def norm(t):
    return "".join(ch for ch in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(ch) != "Mn")


_counts = {}
for _c in data["categories"]:
    for _it in _c["items"]:
        if _it.get("brand"):
            _counts[_it["brand"]] = _counts.get(_it["brand"], 0) + 1
POPULAR = [b for b, n in sorted(_counts.items(), key=lambda x: (-x[1], x[0])) if n >= 2]


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


def card(item, cat_name=""):
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
    who_f = item.get("who") or "Unisex"
    brand_f = item.get("brand") if item.get("brand") in POPULAR else "Otras"
    hay = norm(" ".join([item["name"], item.get("brand", ""), who_f, cat_name, item.get("desc", ""), " ".join(o for o in opts_list if " cm" not in o.lower())]))
    return f"""
      <article class="card"{data_imgs} data-who="{esc(who_f)}" data-brand="{esc(brand_f)}" data-q="{esc(hay)}">
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


steps = "".join(
    f'<li><b class="num">{i + 1}</b><div><h3>{esc(s["t"])}</h3><p>{esc(s["d"])}</p></div></li>'
    for i, s in enumerate(site["steps"])
)

wa_hello = wa_link(f"Hola {site['brand']}, quisiera más información")
def social_li(label, text, url):
    if not text:
        return ""
    inner = f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a>' if url else f"<b>{esc(text)}</b>"
    return f"\n        <li><span>{label}</span>{inner}</li>"


contact_lines = f"""
        <li><span>WhatsApp</span><a href="{wa_hello}" target="_blank" rel="noopener">{esc(site['whatsapp_display'])}</a></li>{social_li("Instagram", site.get("instagram"), site.get("instagram_url"))}{social_li("TikTok", site.get("tiktok"), site.get("tiktok_url"))}{social_li("Facebook", site.get("facebook"), site.get("facebook_url"))}
        <li><span>Ubicación</span><b>{esc(site['location'])}</b></li>"""


def cat_block(cat):
    cards = "".join(card(i, cat["name"]) for i in cat["items"])
    return f"""
    <section class="cat" id="{cat["id"]}" data-products>
      <div class="wire" aria-hidden="true"></div>
      <h2 class="sign">{esc(cat['name'])}</h2>
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

# ---------------- Filtros ----------------
ICON_SEARCH = '<svg class="i-search" viewBox="0 0 24 24" aria-hidden="true"><path d="M10 3a7 7 0 1 0 4.2 12.600l4.600 4.600 1.400-1.400-4.600-4.600A7 7 0 0 0 10 3Zm0 2a5 5 0 1 1 0 10 5 5 0 0 1 0-10Z"/></svg>'
total_products = len(by_id)
brand_chips = "".join(f'<button class="fchip" type="button" data-brand="{esc(b)}" aria-pressed="false">{esc(b)}</button>' for b in POPULAR)
if any(i.get("brand") not in POPULAR for i in by_id.values()):
    brand_chips += '<button class="fchip" type="button" data-brand="Otras" aria-pressed="false">Otras marcas</button>'

FILTERS = f"""
  <section class="filters" id="filtros" aria-label="Filtros del catálogo">
    <div class="filters-box">
      <label class="fsearch">{ICON_SEARCH}<span class="sr">Buscar en el catálogo</span>
        <input id="q" type="search" placeholder="Buscá por nombre, marca o talla" autocomplete="off" enterkeyhint="search"></label>
      <div class="fgroup" role="group" aria-label="Para quién" data-group="who">
        <span class="flabel">Para</span>
        <button class="fchip" type="button" data-who="" aria-pressed="true">Todos</button>
        <button class="fchip" type="button" data-who="Hombre" aria-pressed="false">Hombre</button>
        <button class="fchip" type="button" data-who="Mujer" aria-pressed="false">Mujer</button>
      </div>
      <div class="fgroup" role="group" aria-label="Marca" data-group="brand">
        <span class="flabel">Marca</span>
        <button class="fchip" type="button" data-brand="" aria-pressed="true">Todas</button>{brand_chips}
      </div>
      <div class="fmeta"><span id="fcount" aria-live="polite">{total_products} productos</span>
        <button class="fclear" id="fclear" type="button" hidden>Limpiar filtros</button></div>
    </div>
    <div class="fempty" id="fempty" hidden>
      <p>No encontramos eso en el catálogo… pero lo podemos conseguir por encargo.</p>
      <a class="btn primary" href="#pedido" id="fempty-go">Hacer pedido personalizado</a>
    </div>
  </section>"""

# ---------------- Combos ----------------
combo_list = [c for c in combos_data.get("combos", []) if PREVIEW or not c.get("draft")]


def combo_card(c):
    prods = [by_id[i] for i in c.get("items", []) if i in by_id]
    if not prods:
        return ""
    cells = ""
    for p in prods[:4]:
        im = existing_images(p)
        if im:
            fc = f' style="--focus:{esc(p["focus"])}"' if p.get("focus") else ""
            cells += f'<span{fc}><img src="{esc(im[0])}" alt="{esc(p["name"])}" loading="lazy"></span>'
    n = min(len(prods), 4)
    names = [p["name"] + (f" ({p['who']})" if p.get("who") else "") for p in prods]
    incl = "".join(f"<li>{esc(x)}</li>" for x in names)
    price = c.get("price")
    prices = [p.get("price") for p in prods]
    regular = c.get("regular") or (sum(prices) if all(x is not None for x in prices) and sum(prices) > 0 else None)
    save = ""
    was = ""
    badge = f'<span class="badge">{esc(c.get("tag") or "Combo")}</span>'
    if price is not None and regular and regular > price:
        diff = int(regular - price)
        fmt = lambda v: f"{int(v):,}".replace(",", ".")
        was = f'<s class="was">{esc(site["currency"])}{fmt(regular)}</s>'
        save = f'<p class="save">Ahorrás {esc(site["currency"])}{fmt(diff)}</p>'
        badge = f'<span class="badge">Ahorrás {esc(site["currency"])}{fmt(diff)}</span>'
    msg = f"Hola {site['brand']}, me interesa el combo: {c['name']} ({' + '.join(names)})"
    return f"""
      <article class="combo">
        <i class="nail"></i>{badge}
        <div class="collage n{n}">{cells}</div>
        <div class="combo-body">
          <h3>{esc(c['name'])}</h3>
          <p class="desc">{esc(c.get('desc', ''))}</p>
          <ul class="incl">{incl}</ul>
          <div class="foot"><div class="pbox">{was}{money(price) if price is not None else '<span class="price ask">Precio especial de combo</span>'}{save}</div>
            <a class="btn-order" href="{wa_link(msg)}" target="_blank" rel="noopener">{ICON_CHAT}Pedir combo</a></div>
        </div>
      </article>"""


COMBOS = ""
if combo_list:
    COMBOS = f"""
    <section class="cat combos" id="combos">
      <div class="wire" aria-hidden="true"></div>
      <h2 class="sign">{esc(combos_data.get('titulo', 'Combos'))}</h2>
      <p class="blurb">{esc(combos_data.get('blurb', ''))}</p>
      <div class="combos-grid">{"".join(combo_card(c) for c in combo_list)}
      </div>
    </section>"""

# ---------------- Pedido personalizado ----------------
PEDIDO = f"""
    <section class="cat pp" id="pedido">
      <div class="wire" aria-hidden="true"></div>
      <h2 class="sign">Pedido personalizado</h2>
      <p class="blurb">¿No ves lo que buscás? Contanos y te lo conseguimos por encargo.</p>
      <form class="pp-card" id="ppform" autocomplete="off">
        <i class="nail"></i>
        <label class="ppf wide"><span>¿Qué estás buscando?</span>
          <textarea name="what" rows="3" required placeholder="Ej.: botas western café, jeans Wrangler negros, una faja con hebilla de toro…"></textarea></label>
        <label class="ppf"><span>Marca o modelo</span><input name="brand" type="text" placeholder="Opcional"></label>
        <label class="ppf"><span>Talla</span><input name="size" type="text" placeholder="Ej.: M, 34W, 9.5"></label>
        <label class="ppf"><span>Color</span><input name="color" type="text" placeholder="Opcional"></label>
        <p class="pp-note wide">Al enviar se abre WhatsApp con tu pedido listo. Ahí también podés mandar fotos de referencia.</p>
        <button class="btn primary wide" type="submit">{ICON_CHAT}Enviar pedido por WhatsApp</button>
      </form>
      <div class="pp-print">
        <p>Escribinos por WhatsApp al <b>{esc(site['whatsapp_display'])}</b> y contanos qué buscás:
        marca o modelo, talla, color y, si tenés, una foto de referencia.</p>
      </div>
    </section>"""

# ---------------- Menú de secciones ----------------
chip_list = ([("combos", combos_data.get("titulo", "Combos"))] if combo_list else []) \
    + [(c["id"], c["name"]) for c in data["categories"]] + [("pedido", "A pedido")]
chips = "".join(f'<a href="#{i}">{esc(n)}</a>' for i, n in chip_list)

web_sections = COMBOS + "".join(cat_block(c) for c in data["categories"]) + PEDIDO + HOWTO + END

# ---------------- Entrada de cantina ----------------
_door = '<i class="rail t"></i><i class="rail m"></i><i class="rail b"></i><i class="brace"></i><i class="hinge h1"></i><i class="hinge h2"></i><i class="hinge h3"></i><i class="pull"></i>'
SALOON = f"""
<div class="saloon" aria-hidden="true">
  <div class="door l">{_door}</div>
  <div class="door r">{_door}</div>
  <i class="seam"></i>
  <div class="plaque"><span>{ICON_STAR}{esc(site['brand'])}{ICON_STAR}</span><small>Bienvenido, forastero</small></div>
</div>"""

FAVICON = "data:image/svg+xml," + urllib.parse.quote(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-12 -12 24 24"><rect x="-12" y="-12" width="24" height="24" rx="5" fill="#140b05"/><polygon fill="#e8892b" points="{STAR}"/></svg>'
)


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
<link rel="icon" href="{FAVICON}">
<script>try{{if(!sessionStorage.getItem('rv_intro')&&!matchMedia('(prefers-reduced-motion: reduce)').matches&&!/[?&]nointro/.test(location.search)){{document.documentElement.className='rv-intro'}}}}catch(e){{}}</script>
<link rel="stylesheet" href="assets/style.css">
</head>
<body data-wa="{site['whatsapp']}" data-brand="{esc(site['brand'])}">
{SALOON}
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
        <a class="btn primary" href="#filtros">Ver catálogo</a>
        <a class="btn ghost" href="{wa_hello}" target="_blank" rel="noopener">{ICON_CHAT}Escribinos</a>
      </div>
      <p class="cover-index" aria-hidden="true">{" ★ ".join(esc(n) for _, n in chip_list[:-1])}</p>
      <div class="cover-contact" aria-hidden="true">
        <div class="wire"></div>
        <ul>{contact_lines}
        </ul>
      </div>
    </div>
  </section>
{FILTERS}
{web_sections}
</main>
{LIGHTBOX}
{SCRIPT}
<script src="assets/app.js" defer></script>
</body>
</html>
"""

OUT = os.environ.get("OUT", "index.html")
with open(os.path.join(ROOT, OUT), "w", encoding="utf-8") as f:
    f.write(page)
open(os.path.join(ROOT, ".nojekyll"), "w").close()
print(OUT, "listo —", sum(len(c["items"]) for c in data["categories"]), "productos,", len(combo_list), "combos")

# ---------------- Página 404 temática (GitHub Pages la usa sola) ----------------
random.seed(7)
_stars = "".join(
    f'<i class="st" style="left:{random.uniform(2, 98):.1f}%;top:{random.uniform(2, 46):.1f}%;'
    f'animation-delay:{random.uniform(0, 4):.1f}s;width:{random.choice([2, 2, 3])}px;height:{random.choice([2, 2, 3])}px"></i>'
    for _ in range(36)
)
_weed = ('<svg viewBox="-40 -40 80 80" aria-hidden="true"><g fill="none" stroke="#8a5a2b" stroke-width="2.2" stroke-linecap="round">'
         '<circle r="30"/><circle r="22" transform="rotate(30)"/><ellipse rx="30" ry="14" transform="rotate(20)"/>'
         '<ellipse rx="30" ry="14" transform="rotate(80)"/><ellipse rx="28" ry="10" transform="rotate(140)"/>'
         '<path d="M-26 -14 Q0 -4 24 -22 M-28 10 Q-4 0 26 16 M-10 -28 Q4 0 -8 28 M14 -27 Q-2 4 16 27"/></g></svg>')

NOT_FOUND = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>404 · __BRAND__</title>
<script>
/* En GitHub Pages el catálogo vive en /nombre-del-repositorio/ ; esto hace que las rutas funcionen desde cualquier dirección rota */
(function () {
  var base = '/';
  var parts = location.pathname.split('/');
  if (/github\\.io$/.test(location.hostname) && parts[1]) base = '/' + parts[1] + '/';
  if (location.protocol.indexOf('http') === 0) document.write('<base href="' + base + '">');
})();
</script>
<link rel="icon" href="__FAVICON__">
<link rel="stylesheet" href="assets/style.css">
<style>
body.nf{min-height:100vh;min-height:100dvh;display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden;position:relative;text-align:center;
  background:linear-gradient(180deg,#0e0703 0%,#1d0f06 34%,#4a210b 62%,#a8481a 80%,#f0993a 93%,#f9c06f 100%)}
.nf .st{position:absolute;border-radius:50%;background:#ffeccb;opacity:.2;animation:tw 3.4s ease-in-out infinite}
@keyframes tw{50%{opacity:.95}}
.nf .sun{position:absolute;left:50%;bottom:-16vmin;width:44vmin;height:44vmin;margin-left:-22vmin;border-radius:50%;
  background:radial-gradient(circle,#ffe0a0 0%,#f9b25a 45%,rgba(232,137,43,0) 72%);filter:blur(1px)}
.nf .ground{position:absolute;left:0;right:0;bottom:0;height:22vh;min-height:130px;pointer-events:none}
.nf .ground svg{display:block;width:100%;height:100%}
.nf main{position:relative;z-index:2;width:100%;max-width:560px;padding:0 18px 20vh}
.nf .hang{position:relative;width:fit-content;margin:0 auto;padding-top:78px;transform-origin:50% 0;animation:swing 4.4s ease-in-out infinite alternate}
@keyframes swing{from{transform:rotate(-2.4deg)}to{transform:rotate(2.4deg)}}
.nf .rope{position:absolute;top:0;width:3px;height:84px;background:repeating-linear-gradient(180deg,#b89a6a 0 6px,#7c6238 6px 9px)}
.nf .rope.l{left:18%}.nf .rope.r{right:18%}
.nf .board{padding:12px 44px 8px;border:2px solid #150b04;border-radius:5px;position:relative;
  background:linear-gradient(rgba(18,8,3,.18),rgba(18,8,3,.45)),var(--wood-plank);background-size:auto,auto 100%;
  box-shadow:inset 0 2px 0 rgba(255,220,160,.2),inset 0 -4px 0 rgba(0,0,0,.4),0 14px 26px rgba(0,0,0,.65)}
.nf .board b{display:block;font:400 clamp(4.6rem,24vw,8.6rem)/1 var(--rye);color:var(--amber);text-shadow:0 5px 0 #000,0 0 28px rgba(232,137,43,.4)}
.nf .board small{display:block;margin-top:2px;font:400 .78rem/1 var(--type);letter-spacing:.34em;text-transform:uppercase;color:var(--sand);padding-bottom:4px}
.nf h1{margin-top:26px;font:400 clamp(1.5rem,6vw,2.3rem)/1.15 var(--rye);color:var(--cream);text-shadow:0 3px 0 #000,0 8px 22px rgba(0,0,0,.7)}
.nf p{margin:12px auto 24px;max-width:36ch;font-style:italic;color:var(--sand);text-shadow:0 1px 0 #000}
.nf .cta{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.nf .weed{position:absolute;z-index:1;bottom:calc(5vh + 2px);left:0;width:64px;height:64px;animation:roll 11s linear infinite}
.nf .weed svg{display:block;width:100%;height:100%;animation:spin 11s linear infinite}
@keyframes roll{from{transform:translateX(-90px)}to{transform:translateX(calc(100vw + 90px))}}
@keyframes spin{to{transform:rotate(1080deg)}}
.nf .weed{animation-name:roll,hop;animation-duration:11s,.9s;animation-timing-function:linear,ease-out;animation-iteration-count:infinite,infinite}
@keyframes hop{0%,100%{margin-bottom:0}45%{margin-bottom:22px}}
@media(prefers-reduced-motion:reduce){.nf .hang,.nf .weed,.nf .weed svg,.nf .st{animation:none}.nf .weed{display:none}}
</style>
</head>
<body class="nf">
__STARS__
<i class="sun"></i>
<main>
  <div class="hang">
    <i class="rope l"></i><i class="rope r"></i>
    <div class="board"><b>404</b><small>Ruta no encontrada</small></div>
  </div>
  <h1>¡Ey, forastero! Esa ruta no existe en el rancho.</h1>
  <p>Parece que te perdiste por el desierto. Volvé al catálogo y seguí tu camino.</p>
  <div class="cta">
    <a class="btn primary" href="./">Volver al rancho</a>
    <a class="btn ghost" href="__WA__" target="_blank" rel="noopener">__CHAT__Escribinos</a>
  </div>
</main>
<div class="weed" aria-hidden="true">__WEED__</div>
<div class="ground" aria-hidden="true">
  <svg viewBox="0 0 1200 220" preserveAspectRatio="none">
    <path fill="#150a04" d="M0 150 Q150 120 320 142 T640 138 T960 144 T1200 130 L1200 220 L0 220Z"/>
    <path fill="#0b0502" d="M0 190 Q200 168 420 184 T820 180 T1200 176 L1200 220 L0 220Z"/>
    <g fill="#0b0502">
      <path d="M170 186 v-52 q0-9 8-9 t8 9 v14 q0-18 11-18 t0 18 v-6 q-11 0-11 10 v34Z" transform="translate(40 0)"/>
      <path d="M930 184 v-62 q0-9 8-9 t8 9 v20 q0-20 12-20 t0 20 v-10 q-12 0-12 12 v40Z" transform="translate(60 0)"/>
      <rect x="560" y="150" width="9" height="50"/><rect x="620" y="148" width="9" height="52"/><rect x="680" y="152" width="9" height="48"/>
      <rect x="540" y="160" width="170" height="6"/><rect x="540" y="176" width="170" height="6"/>
    </g>
  </svg>
</div>
</body>
</html>
"""
NOT_FOUND = (NOT_FOUND.replace("__BRAND__", esc(site["brand"])).replace("__FAVICON__", FAVICON)
             .replace("__STARS__", _stars).replace("__WEED__", _weed).replace("__CHAT__", ICON_CHAT)
             .replace("__WA__", wa_hello))
with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8") as f:
    f.write(NOT_FOUND)
