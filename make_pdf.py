#!/usr/bin/env python3
"""Genera catalogo-rancho-villez.pdf desde index.html
(requiere: pip install playwright pillow  +  Chrome/Chromium instalado)."""
import os, shutil, tempfile, pathlib
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("SRC", "index.html")
PDF = os.environ.get("PDF", "catalogo-rancho-villez.pdf")
chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")

try:
    from PIL import Image
except ImportError:
    Image = None

PAGINATE = r"""
() => {
  const IN = 96, PAGE_H = 10.9 * IN, LIMIT = PAGE_H - 0.38 * IN - 4;
  const main = document.querySelector('main');
  const blocks = [...main.children].filter(e => e.matches('section.cat, section.howto, footer.end'));
  blocks.forEach(b => b.remove());
  let page = null;
  const newPage = () => { page = document.createElement('div'); page.className = 'page'; main.appendChild(page); };
  const fits = () => {
    const k = page.lastElementChild;
    return !k || (k.getBoundingClientRect().bottom - page.getBoundingClientRect().top) <= LIMIT;
  };
  const place = (...els) => {
    if (!page) newPage();
    els.forEach(e => page.appendChild(e));
    if (!fits()) { els.forEach(e => e.remove()); newPage(); els.forEach(e => page.appendChild(e)); }
  };
  const howto = blocks.find(b => b.matches('section.howto'));
  const end = blocks.find(b => b.matches('footer.end'));
  for (const cat of blocks.filter(b => b.matches('section.cat'))) {
    const grid = cat.querySelector('.grid, .combos-grid');
    if (!grid) { place(cat); continue; }
    const items = [...grid.children];
    grid.innerHTML = '';
    let sec = null, first = true;
    const start = cont => {
      const s = cat.cloneNode(true);
      if (cont) {
        s.removeAttribute('id'); s.classList.add('cont');
        s.querySelector('.sign').insertAdjacentHTML('beforeend', '<span class="cont-tag"> · continuación</span>');
        const bl = s.querySelector('.blurb'); if (bl) bl.remove();
      }
      page.appendChild(s);
      return s;
    };
    for (const item of items) {
      if (!page) newPage();
      if (!sec) sec = start(!first);
      const g = sec.querySelector('.grid, .combos-grid');
      g.appendChild(item);
      if (!fits()) {
        if (g.children.length === 1) {            // ni siquiera cabe el primero: pasa todo a la página nueva
          sec.remove(); newPage(); sec = start(!first);
          sec.querySelector('.grid, .combos-grid').appendChild(item);
        } else {
          g.removeChild(item); newPage(); sec = start(true);
          sec.querySelector('.grid, .combos-grid').appendChild(item);
        }
      }
      first = false;
    }
  }
  place(...[howto, end].filter(Boolean));
  return main.querySelectorAll('.page').length;
}
"""

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome, args=["--no-sandbox"]) if chrome else p.chromium.launch()
    pg = b.new_page()
    pg.goto("file://" + os.path.join(ROOT, SRC))
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")

    # Versiones más livianas de las fotos solo para el PDF (la página web conserva la calidad completa)
    if Image:
        tmp = tempfile.mkdtemp()
        srcs = pg.evaluate("[...new Set([...document.querySelectorAll('.card img, .combo img')].map(i => i.getAttribute('src')))]")
        mapping = {}
        for n, s in enumerate(srcs):
            im = Image.open(os.path.join(ROOT, s)).convert("RGB")
            im.thumbnail((1000, 1000))
            out = os.path.join(tmp, f"{n}.jpg")
            im.save(out, quality=80, optimize=True)
            mapping[s] = pathlib.Path(out).as_uri()
        pg.evaluate("""m => document.querySelectorAll('.card img, .combo img').forEach(i => {
            i.loading = 'eager'; const s = i.getAttribute('src'); if (m[s]) i.src = m[s]; })""", mapping)
        pg.wait_for_function("[...document.querySelectorAll('.card img, .combo img')].every(i => i.complete)")

    pg.emulate_media(media="print")
    pg.wait_for_timeout(500)

    # Paginación: se mide la altura real de cada tarjeta y se reparten en páginas Carta
    n_pages = pg.evaluate(PAGINATE)
    pg.wait_for_timeout(400)
    print("páginas de contenido:", n_pages)
    pg.pdf(path=os.path.join(ROOT, PDF), prefer_css_page_size=True, print_background=True)
    b.close()
print("PDF listo")
