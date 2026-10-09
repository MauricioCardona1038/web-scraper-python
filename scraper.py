"""
Scraper de libros de https://books.toscrape.com (sitio público hecho para practicar scraping).

Recorre todas las páginas del catálogo, extrae título, precio, calificación,
disponibilidad, categoría y URL de cada libro, y guarda el resultado en CSV y Excel.

Uso:
    python scraper.py                 # todo el catálogo (50 páginas, 1000 libros)
    python scraper.py --paginas 3     # solo las 3 primeras páginas
    python scraper.py --detalle       # además entra a cada libro para sacar categoría y stock exacto
"""

import argparse
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

URL_BASE = "https://books.toscrape.com/catalogue/"
URL_INICIO = urljoin(URL_BASE, "page-1.html")
CARPETA_SALIDA = Path(__file__).parent / "output"

CALIFICACIONES = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
HEADERS = {"User-Agent": "Mozilla/5.0 (portfolio scraper; contacto: github.com/MauricioCardona1038)"}


def descargar(session: requests.Session, url: str, reintentos: int = 3) -> BeautifulSoup:
    """Descarga una página y la devuelve parseada. Reintenta si falla la conexión."""
    for intento in range(1, reintentos + 1):
        try:
            resp = session.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as error:
            if intento == reintentos:
                raise
            print(f"  Error en {url} ({error}). Reintentando ({intento}/{reintentos})...")
            time.sleep(2 * intento)


def extraer_libros(soup: BeautifulSoup, url_pagina: str) -> list[dict]:
    """Extrae los datos básicos de cada libro listado en una página del catálogo."""
    libros = []
    for articulo in soup.select("article.product_pod"):
        enlace = articulo.h3.a
        precio_texto = articulo.select_one("p.price_color").get_text(strip=True)
        clase_estrellas = articulo.select_one("p.star-rating")["class"][1]
        libros.append({
            "titulo": enlace["title"],
            "precio_gbp": float(re.sub(r"[^\d.]", "", precio_texto)),
            "calificacion": CALIFICACIONES.get(clase_estrellas, 0),
            "disponible": "In stock" in articulo.select_one("p.availability").get_text(),
            "url": urljoin(url_pagina, enlace["href"]),
        })
    return libros


def extraer_detalle(session: requests.Session, libro: dict) -> None:
    """Entra a la página del libro y agrega categoría y unidades en stock."""
    soup = descargar(session, libro["url"])
    libro["categoria"] = soup.select("ul.breadcrumb li a")[-1].get_text(strip=True)
    stock = re.search(r"\((\d+) available\)", soup.select_one("p.availability").get_text())
    libro["unidades_stock"] = int(stock.group(1)) if stock else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Scraper de books.toscrape.com")
    parser.add_argument("--paginas", type=int, default=0, help="Máximo de páginas a recorrer (0 = todas)")
    parser.add_argument("--detalle", action="store_true", help="Entrar a cada libro para sacar categoría y stock")
    parser.add_argument("--pausa", type=float, default=0.5, help="Segundos de espera entre peticiones")
    args = parser.parse_args()

    session = requests.Session()
    libros = []
    url = URL_INICIO
    pagina = 0

    while url and (args.paginas == 0 or pagina < args.paginas):
        pagina += 1
        print(f"Página {pagina}: {url}")
        soup = descargar(session, url)
        libros.extend(extraer_libros(soup, url))
        siguiente = soup.select_one("li.next a")
        url = urljoin(url, siguiente["href"]) if siguiente else None
        time.sleep(args.pausa)

    if args.detalle:
        print(f"Descargando el detalle de {len(libros)} libros...")
        for i, libro in enumerate(libros, 1):
            extraer_detalle(session, libro)
            if i % 20 == 0:
                print(f"  {i}/{len(libros)}")
            time.sleep(args.pausa)

    df = pd.DataFrame(libros).drop_duplicates(subset="url")
    CARPETA_SALIDA.mkdir(exist_ok=True)
    ruta_csv = CARPETA_SALIDA / "libros.csv"
    ruta_xlsx = CARPETA_SALIDA / "libros.xlsx"
    df.to_csv(ruta_csv, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(ruta_xlsx, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Libros", index=False)
        hoja = writer.sheets["Libros"]
        hoja.auto_filter.ref = hoja.dimensions
        hoja.freeze_panes = "A2"
        for columna in hoja.columns:
            ancho = max(len(str(celda.value or "")) for celda in columna)
            hoja.column_dimensions[columna[0].column_letter].width = min(ancho + 2, 60)

    print(f"\nListo: {len(df)} libros de {pagina} páginas")
    print(f"Precio promedio: £{df['precio_gbp'].mean():.2f}")
    print(f"Guardado en:\n  {ruta_csv}\n  {ruta_xlsx}")


if __name__ == "__main__":
    main()
