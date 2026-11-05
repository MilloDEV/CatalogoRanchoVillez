# Catálogo Rancho Villéz

## Cómo publicarlo gratis en GitHub Pages
1. Creá una cuenta en github.com y un repositorio nuevo (público), por ejemplo `catalogo`.
2. Subí **todo el contenido de esta carpeta** (index.html, assets, images, etc.).
3. En el repositorio: Settings → Pages → Source: "Deploy from a branch" → rama `main` → carpeta `/ (root)` → Save.
4. En 1–2 minutos queda en: `https://TU-USUARIO.github.io/catalogo/`

## Cómo agregar o cambiar productos
- Datos de contacto y textos: `site.json` (poné aquí el WhatsApp real, con código de país y sin signos: `50688887777`).
- Productos: `products.json`. Las fotos van en la carpeta `images/` y se enlazan con el campo `"image": "mi-foto.jpg"`.
- Después ejecutar `python3 build.py` (genera index.html) y `python3 make_pdf.py` (genera el PDF).
