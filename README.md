# Web Scraper en Python → CSV y Excel

Script que recorre automáticamente todas las páginas de un catálogo web, extrae los datos de cada producto y los entrega limpios en **CSV** y **Excel**, listos para analizar.

Como ejemplo usa [books.toscrape.com](https://books.toscrape.com), un sitio público creado para practicar scraping: **1000 libros en 50 páginas, extraídos en un par de minutos**.

## Qué hace

- Recorre la paginación sola (sigue el botón "next" hasta la última página).
- Extrae título, precio, calificación (1 a 5), disponibilidad y URL de cada libro.
- Con `--detalle` entra a la página de cada libro para sacar también **categoría** y **unidades en stock**.
- Limpia los datos: precios como número, calificación como entero y sin duplicados.
- Exporta a **CSV** (UTF-8, abre bien en Excel) y a **Excel** con filtros, encabezado fijo y columnas ajustadas.
- Reintenta automáticamente si falla la conexión y espera entre peticiones para no saturar el sitio.

## Resultado

| titulo | precio_gbp | calificacion | disponible | categoria | unidades_stock |
|---|---|---|---|---|---|
| A Light in the Attic | 51.77 | 3 | True | Poetry | 22 |
| Tipping the Velvet | 53.74 | 1 | True | Historical Fiction | 20 |
| Soumission | 50.10 | 1 | True | Fiction | 20 |

Los archivos completos están en [`ejemplos/libros.csv`](ejemplos/libros.csv) y [`ejemplos/libros.xlsx`](ejemplos/libros.xlsx).

## Cómo usarlo

```bash
pip install -r requirements.txt

python scraper.py                 # todo el catálogo
python scraper.py --paginas 3     # solo las 3 primeras páginas
python scraper.py --detalle       # incluye categoría y stock de cada libro
```

Los archivos se guardan en la carpeta `output/`.

## Tecnologías

Python 3 · requests · BeautifulSoup · pandas · openpyxl

## Adaptarlo a otro sitio

La lógica está separada en funciones (`descargar`, `extraer_libros`, `extraer_detalle`), así que para otro sitio solo hay que cambiar la URL inicial y los selectores CSS. El resto (paginación, reintentos, limpieza y exportación) se reutiliza tal cual.

> Solo para sitios públicos y respetando sus términos de uso y su `robots.txt`.

---

Hecho por **Mauricio Cardona** · ¿Necesitas extraer datos de un sitio web? Escríbeme.
