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

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome, args=["--no-sandbox"]) if chrome else p.chromium.launch()
    pg = b.new_page()
    pg.goto("file://" + os.path.join(ROOT, SRC))
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")

    # Versiones más livianas de las fotos solo para el PDF (la página web conserva la calidad completa)
    if Image:
        tmp = tempfile.mkdtemp()
        srcs = pg.evaluate("[...new Set([...document.querySelectorAll('.card img')].map(i => i.getAttribute('src')))]")
        mapping = {}
        for n, s in enumerate(srcs):
            im = Image.open(os.path.join(ROOT, s)).convert("RGB")
            im.thumbnail((1000, 1000))
            out = os.path.join(tmp, f"{n}.jpg")
            im.save(out, quality=80, optimize=True)
            mapping[s] = pathlib.Path(out).as_uri()
        pg.evaluate("""m => document.querySelectorAll('.card img').forEach(i => {
            i.loading = 'eager'; const s = i.getAttribute('src'); if (m[s]) i.src = m[s]; })""", mapping)
        pg.wait_for_function("[...document.querySelectorAll('.card img')].every(i => i.complete)")

    pg.emulate_media(media="print")
    pg.wait_for_timeout(500)
    pg.pdf(path=os.path.join(ROOT, PDF), prefer_css_page_size=True, print_background=True)
    b.close()
print("PDF listo")
