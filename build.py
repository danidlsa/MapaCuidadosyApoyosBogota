"""
build.py  —  Generador del StoryMap demo (versión accesible).
Uso:  python3 build.py
Salida: carpeta site/ lista para subir a Netlify o abrir localmente.

Cada mapa se genera con un template Leaflet propio (templates/mapa.html.j2) que
incluye filtros accesibles, iconografía por forma+color y clustering.
"""
import shutil, json, html, ast, re, time
from pathlib import Path

import geopandas as gpd
import pandas as pd
from jinja2 import Environment, FileSystemLoader

import config

HERE  = Path(__file__).parent
SITE  = HERE / "docs"        # GitHub Pages publica desde /docs
MAPAS = SITE / "mapas"

# ── Utilidades ────────────────────────────────────────────────────────────────

def limpiar_sitio():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    MAPAS.mkdir()
    shutil.copytree(HERE / "static", SITE, dirs_exist_ok=True)

def cargar(capa):
    return gpd.read_file(config.GDB, layer=capa).to_crs(epsg=4326)

def nd(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "No disponible"
    s = str(v).strip()
    return s if s and s.upper() not in ("NO DISPONIBLE", "NONE", "NAN", "") else "No disponible"

def tel_link(v):
    s = nd(v)
    return f'<a href="tel:{s}">{s}</a>' if s != "No disponible" else s

def mail_link(v):
    s = nd(v)
    return f'<a href="mailto:{s}">{s}</a>' if s != "No disponible" else s

def comollegar(lat, lng):
    """Enlace a la ruta en Google Maps hasta el servicio (abre la app de mapas)."""
    return (f'<a class="popup-ir" target="_blank" rel="noopener" '
            f'href="https://www.google.com/maps/dir/?api=1&destination={lat},{lng}">'
            f'Cómo llegar →</a>')

def popup(titulo, subtitulo, filas, latlng=None):
    """Construye HTML de popup uniforme entre los cuatro mapas."""
    out = [f'<div style="max-width:280px"><b style="font-size:14px">{html.escape(titulo)}</b>']
    if subtitulo:
        out.append(f'<br><em>{html.escape(subtitulo)}</em>')
    out.append('<br><br>')
    for etq, val in filas:
        out.append(f'<b>{etq}:</b> {val}<br>')
    if latlng:
        out.append(comollegar(latlng[0], latlng[1]))
    out.append('</div>')
    return ''.join(out)

# ── Pictogramas: badge (círculo de color + pictograma blanco) ─────────────────
_ICONS_DIR = HERE / "static" / "icons"
_icon_cache = {}

def inner_svg(nombre):
    """Devuelve el contenido interno (paths) de un SVG de static/icons/."""
    if nombre in _icon_cache:
        return _icon_cache[nombre]
    txt = (_ICONS_DIR / f"{nombre}.svg").read_text(encoding="utf-8")
    inner = txt[txt.index(">", txt.index("<svg")) + 1: txt.rindex("</svg>")]
    _icon_cache[nombre] = inner
    return inner

def badge_html(est, size=28):
    """Círculo de color con pictograma blanco. Mismo formato en leyenda y marcador."""
    inner = est.get("icon_svg") or inner_svg(est["icon"])
    g = round(size * 0.56)
    return (
        f'<span class="pin" style="background:{est["color"]};width:{size}px;height:{size}px">'
        f'<svg viewBox="0 0 16 16" fill="#fff" width="{g}" height="{g}" aria-hidden="true">{inner}</svg>'
        f'</span>'
    )

def svg_leyenda(est, size=26):
    return badge_html(est, size)

def picto(nombre, color, size=40):
    """Badge de pictograma para usar en la narrativa (menú, pasos)."""
    return badge_html({"icon": nombre, "color": color}, size)

def picto_ring(nombre, color, size=64):
    """Pictograma estilo 'aro': círculo claro con borde de color y pictograma del color."""
    inner = inner_svg(nombre)
    g = round(size * 0.5)
    return (
        f'<span class="pin-ring" style="--c:{color};width:{size}px;height:{size}px">'
        f'<svg viewBox="0 0 16 16" fill="{color}" width="{g}" height="{g}" aria-hidden="true">{inner}</svg>'
        f'</span>'
    )

# ── Constructores por mapa ────────────────────────────────────────────────────
# Cada uno devuelve: (features[list], estilos[dict], filtros[list], tabla_html[str])

def discs_de(row):
    return {c: int(row.get(c, 0) or 0) for c in config.DISC_LABELS}

def disc_texto(row):
    ds = [config.DISC_LABELS[c] for c in config.DISC_LABELS if row.get(c) == 1]
    return ", ".join(ds) if ds else "Sin registro"

def _parse_tramo(s):
    """Convierte un tramo de edad textual en un conjunto de edades."""
    s = (s or "").lower()
    m = re.search(r"(\d+)\s*a\s*(\d+)", s)
    if m:
        return set(range(int(m.group(1)), int(m.group(2)) + 1))
    if "mayores de edad" in s:
        return set(range(18, 60))
    m = re.search(r"a partir de\s*(\d+)", s)
    if m:
        return set(range(int(m.group(1)), 60))
    return set()

def grupos_edad_de(row):
    """Marca a qué grupos de edad atiende el servicio.
    Si no hay dato de edad, marca todos los grupos (= se muestra con cualquier filtro)."""
    raw = row.get("edades_lista")
    ages = set()
    try:
        if isinstance(raw, str) and raw.strip().startswith("["):
            ages = set(int(x) for x in ast.literal_eval(raw))
    except Exception:
        ages = set()
    if not ages:
        ages = _parse_tramo(str(row.get("tramo_edad") or ""))
    if not ages:  # sin dato: no esconder, pasa cualquier filtro de edad
        return {"edad_pi": 1, "edad_ni": 1, "edad_ad": 1, "edad_adu": 1}
    en = lambda a, b: 1 if any(a <= x <= b for x in ages) else 0
    return {"edad_pi": en(0, 5), "edad_ni": en(6, 11),
            "edad_ad": en(12, 17), "edad_adu": en(18, 200)}

def tabla_de_feats(feats, etiquetas):
    """Tabla enlazable al mapa: cada fila lleva data-id (= id del marcador) y un botón 'Ver en el mapa'."""
    th = "".join(f"<th>{html.escape(e)}</th>" for e in etiquetas)
    th += '<th><span class="sr-only">Acción</span></th>'
    body = []
    for f in feats:
        fid  = f["props"]["id"]
        fila = f["props"].get("fila", {})
        tds  = "".join(f"<td>{fila.get(e, 'No disponible')}</td>" for e in etiquetas)
        tds += (f'<td><button type="button" class="ver-en-mapa" data-id="{fid}">'
                f'Ver en el mapa</button></td>')
        body.append(f'<tr data-id="{fid}">{tds}</tr>')
    return (f'<table class="tabla-servicios"><thead><tr>{th}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table>')


def build_mapa1():
    gdf = cargar("Cuidados_SDIS")
    map_mod = {
        "CENTRO DISTRITAL DE REFERENCIACION Y APOYO INTEGRAL PARA LA INCLUSION SOCIAL - CADIS+": "CADIS+",
        "CENTROS CRECER": "Centros Crecer",
        "CENTROS INTEGRARTE ATENCION INTERNA": "Integrarte Interno",
        "CENTROS INTEGRARTE ATENCION EXTERNA": "Integrarte Externo",
    }
    feats, locs = [], set()
    for i, (_, r) in enumerate(gdf.iterrows()):
        cat = map_mod.get(str(r.get("ModServ", "")).strip(), "Otro")
        loc = config.norm_localidad(r.get("LocNombre"))
        if loc: locs.add(loc)
        nombre = nd(r.get("OSSUOpera"))
        p = popup(nombre, config.ESTILO_MAPA1[cat]["label"], [
            ("Tipo de discapacidad", nd(r.get("tipo_discapacidad"))),
            ("Edades atendidas",     nd(r.get("tramo_edad"))),
            ("Descripción",          nd(r.get("descripcion_oferta"))),
            ("Dirección",            nd(r.get("direccion"))),
            ("Teléfono",             tel_link(r.get("telefono"))),
            ("Correo",               mail_link(r.get("correo"))),
            ("Horario",              nd(r.get("horario"))),
        ], latlng=(r.geometry.y, r.geometry.x))
        feats.append({"lat": r.geometry.y, "lng": r.geometry.x, "props": {
            "id": i, "cat": cat, "tooltip": nombre, "popup": p,
            "localidad": loc or "No disponible", "tipo": cat,
            "buscar": f"{nombre} {nd(r.get('direccion'))} {loc or ''}",
            "fila": {"Centro": nombre, "Tipo": cat, "Localidad": loc or "No disponible",
                     "Dirección": nd(r.get("direccion")), "Teléfono": tel_link(r.get("telefono"))},
        }})
    estilos = config.ESTILO_MAPA1
    filtros = [
        {"tipo":"select","campo":"localidad","etiqueta":"Localidad","opciones":sorted(locs)},
        {"tipo":"select","campo":"tipo","etiqueta":"Tipo de centro",
         "opciones":["CADIS+","Centros Crecer","Integrarte Interno","Integrarte Externo"]},
        {"tipo":"texto","campo":"buscar","etiqueta":"Buscar por nombre o dirección"},
    ]
    tabla = tabla_de_feats(feats, ["Centro", "Tipo", "Localidad", "Dirección", "Teléfono"])
    return feats, estilos, filtros, tabla


def build_mapa2():
    gdf = cargar("Educacion_Inclusiva")
    disc_cols = list(config.DISC_LABELS)
    feats, locs = [], set()
    for i, (_, r) in enumerate(gdf.iterrows()):
        atiende = any(r.get(c) == 1 for c in disc_cols)
        sector_n = int(r.get("SECTOR")) if pd.notna(r.get("SECTOR")) else 2
        sector = "Oficial" if sector_n == 1 else "No oficial"
        cat = sector if atiende else "Sin discapacidad"
        cod = str(r.get("COD_LOCA")).zfill(2) if pd.notna(r.get("COD_LOCA")) else None
        loc = config.LOCALIDADES.get(cod, "No disponible")
        if loc != "No disponible": locs.add(loc)
        nombre = nd(r.get("NOMBRE_EST"))
        p = popup(nombre, sector, [
            ("Localidad",  loc),
            ("Dirección",  nd(r.get("DIRECCION"))),
            ("Teléfono",   tel_link(r.get("TELEFONO"))),
            ("Correo",     mail_link(r.get("EMAIL"))),
            ("Sitio web",  nd(r.get("WEB"))),
            ("Discapacidades atendidas", disc_texto(r)),
        ], latlng=(r.geometry.y, r.geometry.x))
        d = discs_de(r)
        feats.append({"lat": r.geometry.y, "lng": r.geometry.x, "props": {
            "id": i, "cat": cat, "tooltip": nombre, "popup": p,
            "localidad": loc, "sector": sector,
            "buscar": f"{nombre} {nd(r.get('DIRECCION'))} {loc}", **d,
            "fila": {"Colegio": nombre, "Sector": sector, "Localidad": loc,
                     "Dirección": nd(r.get("DIRECCION"))},
        }})
    estilos = config.ESTILO_MAPA2
    filtros = [
        {"tipo":"select","campo":"localidad","etiqueta":"Localidad","opciones":sorted(locs)},
        {"tipo":"select","campo":"sector","etiqueta":"Sector","opciones":["Oficial","No oficial"]},
        {"tipo":"checkbox-disc","campo":"disc","etiqueta":"Tipo de discapacidad atendida",
         "opciones":[(c, config.DISC_LABELS[c]) for c in disc_cols]},
        {"tipo":"texto","campo":"buscar","etiqueta":"Buscar por nombre o dirección"},
    ]
    tabla = tabla_de_feats(feats, ["Colegio", "Sector", "Localidad", "Dirección"])
    return feats, estilos, filtros, tabla


def build_mapa3():
    gdf = cargar("Oferta_discapacidad")
    disc_cols = list(config.DISC_LABELS)
    feats, temas, entidades = [], set(), set()
    for i, (_, r) in enumerate(gdf.iterrows()):
        tema = nd(r.get("tematica_servicio"))
        cat = tema if tema in config.ESTILO_MAPA3 else "Otra"
        if tema != "No disponible": temas.add(tema)
        ent = nd(r.get("enti_nombre")).replace("\n", " ").strip()
        if ent != "No disponible": entidades.add(ent)
        nombre = nd(r.get("ofer_nombr"))
        p = popup(nombre, ent, [
            ("Temática",     tema),
            ("Discapacidad", disc_texto(r)),
            ("Edades",       nd(r.get("tramo_edad"))),
            ("Descripción",  nd(r.get("descripcion_oferta"))),
            ("Dirección",    nd(r.get("direccion"))),
            ("Teléfono",     tel_link(r.get("telefono"))),
            ("Correo",       mail_link(r.get("correo"))),
            ("Horario",      nd(r.get("horario"))),
        ], latlng=(r.geometry.y, r.geometry.x))
        d = discs_de(r)
        feats.append({"lat": r.geometry.y, "lng": r.geometry.x, "props": {
            "id": i, "cat": cat, "tooltip": nombre, "popup": p,
            "tematica": tema, "entidad": ent,
            "buscar": f"{nombre} {nd(r.get('direccion'))} {ent}", **d,
            "fila": {"Servicio": nombre, "Entidad": ent, "Temática": tema,
                     "Dirección": nd(r.get("direccion"))},
        }})
    # Estilos solo para las temáticas presentes (+ "Otra" si aplica)
    estilos = {t: config.ESTILO_MAPA3[t] for t in config.ESTILO_MAPA3
               if t in temas or t == "Otra"}
    for t in estilos:  # añadir label = nombre temática
        estilos[t] = {**estilos[t], "label": t}
    filtros = [
        {"tipo":"select","campo":"tematica","etiqueta":"Temática","opciones":sorted(temas)},
        {"tipo":"checkbox-disc","campo":"disc","etiqueta":"Tipo de discapacidad atendida",
         "opciones":[(c, config.DISC_LABELS[c]) for c in disc_cols]},
        {"tipo":"select","campo":"entidad","etiqueta":"Entidad responsable","opciones":sorted(entidades)},
        {"tipo":"texto","campo":"buscar","etiqueta":"Buscar por nombre"},
    ]
    tabla = tabla_de_feats(feats, ["Servicio", "Entidad", "Temática", "Dirección"])
    return feats, estilos, filtros, tabla


def build_mapa4():
    serv  = cargar("Servicios_cuidadoras")
    equip = cargar("Equipamiento_ancla")
    feats, locs = [], set()
    idx = 0
    for _, r in serv.iterrows():
        tipo_raw = str(r.get("TIPO_SERVI", "")).strip()
        cat = "Cuidadoras" if "Cuidadora" in tipo_raw else "Familias y comunidad"
        loc = config.norm_localidad(r.get("LOCALIDAD"))
        if loc: locs.add(loc)
        nombre = nd(r.get("SERVICIO"))
        p = popup(nombre, f"Manzana del Cuidado: {nd(r.get('MANZANA'))}", [
            ("Tipo de servicio", tipo_raw or "No disponible"),
            ("Equipamiento",     nd(r.get("EQUIPAMIENTO"))),
            ("Localidad",        loc or "No disponible"),
            ("Dirección",        nd(r.get("direccion"))),
            ("Teléfono",         tel_link(r.get("telefono"))),
            ("Horario",          nd(r.get("horario"))),
        ], latlng=(r.geometry.y, r.geometry.x))
        feats.append({"lat": r.geometry.y, "lng": r.geometry.x, "props": {
            "id": idx, "cat": cat, "tooltip": nombre, "popup": p,
            "localidad": loc or "No disponible", "tipo": cat,
            "buscar": f"{nombre} {nd(r.get('MANZANA'))} {loc or ''}",
            "fila": {"Manzana": nd(r.get("MANZANA")), "Servicio": nombre,
                     "Localidad": loc or "No disponible", "Dirección": nd(r.get("direccion"))},
        }})
        idx += 1
    for _, r in equip.iterrows():
        loc = config.norm_localidad(r.get("Localidad"))
        if loc: locs.add(loc)
        nombre = nd(r.get("Equipamiento"))
        p = popup(nombre, "Equipamiento ancla de la Manzana del Cuidado", [
            ("Localidad", loc or "No disponible"),
            ("Dirección", nd(r.get("Direccion"))),
        ], latlng=(r.geometry.y, r.geometry.x))
        feats.append({"lat": r.geometry.y, "lng": r.geometry.x, "props": {
            "id": idx, "cat": "Equipamiento ancla", "tooltip": nombre, "popup": p,
            "localidad": loc or "No disponible", "tipo": "Equipamiento ancla",
            "buscar": f"{nombre} {loc or ''}",
            "fila": {"Manzana": nombre, "Servicio": "Equipamiento ancla",
                     "Localidad": loc or "No disponible", "Dirección": nd(r.get("Direccion"))},
        }})
        idx += 1
    estilos = config.ESTILO_MAPA4
    filtros = [
        {"tipo":"select","campo":"localidad","etiqueta":"Localidad","opciones":sorted(locs)},
        {"tipo":"select","campo":"tipo","etiqueta":"¿A quién está dirigido?",
         "opciones":["Cuidadoras","Familias y comunidad","Equipamiento ancla"]},
        {"tipo":"texto","campo":"buscar","etiqueta":"Buscar por servicio o manzana"},
    ]
    tabla = tabla_de_feats(feats, ["Manzana", "Servicio", "Localidad", "Dirección"])
    return feats, estilos, filtros, tabla


def tabla_html(df, columnas):
    cols = [c for c in columnas if c in df.columns]
    sub = df[cols].rename(columns=columnas).fillna("No disponible")
    return sub.to_html(index=False, border=0, classes="tabla-servicios",
                       escape=False, na_rep="No disponible")

# ── Cifras de contexto ────────────────────────────────────────────────────────

def calcular_cifras():
    c1 = len(cargar("Cuidados_SDIS"))
    c2 = len(cargar("Educacion_Inclusiva"))
    c3 = len(cargar("Oferta_discapacidad"))
    c4 = len(cargar("Servicios_cuidadoras"))
    c5 = len(cargar("Equipamiento_ancla"))
    return [
        {"valor": "458.000", "icon": "people-fill",        "color": "#5B2B82",
         "etiqueta": "personas con dificultad funcional en Bogotá (DANE 2018)"},
        {"valor": f"{c1}",    "icon": "building-fill",      "color": "#4F7A12",
         "etiqueta": "centros de atención directa de la SDIS"},
        {"valor": f"{c2:,}".replace(",", "."), "icon": "mortarboard-fill", "color": "#E8705B",
         "etiqueta": "colegios con estudiantes con discapacidad"},
        {"valor": f"{c3}",    "icon": "grid-3x3-gap-fill",  "color": "#2E5AAC",
         "etiqueta": "servicios de otras entidades distritales"},
        {"valor": f"{c4}",    "icon": "person-hearts",      "color": "#1F7385",
         "etiqueta": "servicios en Manzanas del Cuidado"},
        {"valor": f"{c5}",    "icon": "house-heart-fill",   "color": "#B5800A",
         "etiqueta": "equipamientos ancla del cuidado"},
    ]

# ── Render ────────────────────────────────────────────────────────────────────

def main():
    print("Limpiando site/…")
    limpiar_sitio()

    env = Environment(loader=FileSystemLoader(HERE / "templates"))
    env.globals["svg_leyenda"] = svg_leyenda
    env.globals["picto"] = picto
    env.globals["picto_ring"] = picto_ring
    tmpl_mapa = env.get_template("mapa.html.j2")

    builders = {"mapa1": build_mapa1, "mapa2": build_mapa2,
                "mapa3": build_mapa3, "mapa4": build_mapa4}

    for cfg in config.TEXTOS["mapas"]:
        mid = cfg["id"]
        print(f"Generando {mid}: {cfg['titulo']}…")
        feats, estilos, filtros, tabla = builders[mid]()
        # Inyectar el pictograma inline en cada estilo (para marcador y leyenda).
        for est in estilos.values():
            est["icon_svg"] = inner_svg(est["icon"])
        html_mapa = tmpl_mapa.render(
            titulo=cfg["titulo"], alt=cfg["alt"],
            filtros=filtros, estilos=estilos,
            usar_cluster=cfg.get("cluster", False),
            features_json=json.dumps(feats, ensure_ascii=False),
            estilos_json=json.dumps(estilos, ensure_ascii=False),
            center_lat=config.BOGOTA_LAT, center_lon=config.BOGOTA_LON, zoom=config.ZOOM_START,
        )
        (MAPAS / f"{mid}.html").write_text(html_mapa, encoding="utf-8")
        cfg["tabla_html"] = tabla
        print(f"  · {len(feats)} puntos")

    print("Calculando cifras…")
    cifras = calcular_cifras()

    print("Generando index.html…")
    tmpl_idx = env.get_template("index.html.j2")
    html_idx = tmpl_idx.render(textos=config.TEXTOS, cifras=cifras,
                               colors=config.COLORS, repo=config.REPO_URL,
                               version=str(int(time.time())))
    (SITE / "index.html").write_text(html_idx, encoding="utf-8")

    print(f"\n✓ Sitio en: {SITE}")
    print("  Local: abrir docs/index.html")
    print("  Publicar: hacer commit y push; GitHub Pages sirve desde /docs")

if __name__ == "__main__":
    main()
