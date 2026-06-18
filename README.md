# Mapa de cuidados y apoyos a personas con discapacidad en Bogotá — demo

Demo navegable (tipo StoryMap por scroll) de la oferta pública de servicios de
cuidado y apoyo a personas con discapacidad y a quienes las cuidan en Bogotá.

Es una **versión demostrativa en software libre** (Python + Leaflet), pensada como
anticipo del StoryMap que IDECA publicará en ArcGIS. Prioriza la accesibilidad
(WCAG 2.1 AA): navegación por teclado, contraste, lectores de pantalla, pictogramas
con forma + color, alternativa en lista por mapa, barra de accesibilidad
(tamaño de texto, alto contraste, modo oscuro, reducir movimiento, lectura fácil).

## Cuatro mapas
1. Centros de atención directa (SDIS)
2. Educación inclusiva
3. Otra oferta para personas con discapacidad (Secretaría General)
4. Apoyo a personas cuidadoras (Manzanas del Cuidado)

## Cómo regenerar el sitio

```bash
pip install geopandas folium jinja2
python3 build.py
```

Genera la carpeta `docs/`, que es lo que publica GitHub Pages.

> El script lee los datos desde `../datos ideca/PNUD.gdb.zip` (no incluido en el repo).
> Para reconstruir hace falta esa geodatabase; el sitio ya generado en `docs/` funciona
> sin ella.

## Publicación

GitHub Pages → rama `main` → carpeta `/docs`.

## Créditos

Datos: Secretaría Distrital de Integración Social, Secretaría Distrital de la Mujer,
Secretaría Distrital de Educación, Secretaría General de la Alcaldía Mayor de Bogotá.
Procesamiento: PNUD. Publicación y mantenimiento: IDECA.
