# Catálogo Rancho Villéz

## Publicarlo gratis en GitHub Pages (paso a paso)

1. **Cuenta**: entrá a https://github.com y creá una cuenta (Sign up). Confirmá el correo.
2. **Repositorio nuevo**: arriba a la derecha tocá **+ → New repository**.
   - Repository name: `catalogo` (este nombre queda en el link).
   - Marcá **Public**.
   - Tocá **Create repository**.
3. **Subir los archivos**: en la página del repositorio tocá el link **uploading an existing file**.
   - Abrí la carpeta `Catalogo-Rancho-Villez` del escritorio, entrá y seleccioná TODO lo que hay adentro (Ctrl + A).
   - Arrastralo a la ventana de GitHub y esperá a que termine de cargar (son unos 83 archivos, 20 MB).
   - Abajo tocá **Commit changes**.
4. **Activar Pages**: **Settings → Pages**. En "Build and deployment" elegí:
   - Source: **Deploy from a branch**
   - Branch: **main** y carpeta **/ (root)** → **Save**.
5. **Esperar 1–3 minutos** y refrescar esa misma pantalla. Arriba aparece el link:
   `https://TU-USUARIO.github.io/catalogo/`
6. **Compartir**: copiá ese link y mandalo por WhatsApp, Instagram, TikTok y Facebook (poné el link en la biografía).
   El PDF queda en `https://TU-USUARIO.github.io/catalogo/catalogo-rancho-villez.pdf`.

## Qué trae la página
- **Filtros**: buscador (nombre, marca o talla), Hombre / Mujer y marca. Las marcas con 2 o más productos tienen su propio botón; el resto va en "Otras marcas".
- **Etiquetas**: en `products.json`, campo `"badge": "Premium"` en los productos que quieras destacar (poné pocas).
- **Combos**: se llenan en `combos.json`. Cada combo lleva `name`, `desc`, `items` (los `id` de los productos) y `price` (precio del combo). Si los productos tienen precio, la página calcula sola "Ahorrás ₡X". Quitá `"draft": true` para que se vea.
- **Pedido personalizado**: formulario que abre WhatsApp con el mensaje armado.
- **Entrada de cantina**: se ve una vez por visita. Se puede saltar tocando la pantalla. Para verla otra vez, cerrá la pestaña y abrí el link de nuevo.
- **Página 404**: `404.html` se muestra sola cuando alguien abre un link que no existe.

## Cuando haya cambios o productos nuevos
Mandale las fotos y la info a Claude. Después, en el repositorio: **Add file → Upload files**, subí los archivos que cambiaron
(normalmente `index.html`, `404.html`, `catalogo-rancho-villez.pdf`, la carpeta `assets` y las fotos nuevas de `images/`) y **Commit changes**.
En 1–2 minutos se actualiza el link.

## Datos que se cambian en `site.json`
WhatsApp (con código de país, sin signos: `50684507930`), Instagram, TikTok, Facebook y ubicación.
Los productos están en `products.json` (precio: poné el número, por ejemplo `15000`; si es `null` dice "Consultar precio").
Para regenerar: `python3 build.py` (página y 404) y `python3 make_pdf.py` (PDF).
