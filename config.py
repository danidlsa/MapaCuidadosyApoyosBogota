"""
Configuración central del StoryMap demo.
Editar aquí textos, colores, filtros e iconografía antes de correr build.py.

Paleta inspirada en el Sistema Distrital de Cuidado de Bogotá
(morado, verde manzana, salmón). Todos los colores de texto verificados
con contraste >= 4.5:1 sobre blanco (WCAG AA).
"""
from pathlib import Path

# ── Rutas ─────────────────────────────────────────────────────────────────────
GDB = Path(__file__).parent.parent / "datos ideca" / "PNUD.gdb.zip"

# ── Mapa base ─────────────────────────────────────────────────────────────────
TILES       = "CartoDB Positron"
BOGOTA_LAT  = 4.65
BOGOTA_LON  = -74.10
ZOOM_START  = 11
REPO_URL    = "https://github.com/danidlsa/discapacidad_bogota"

# ── Paleta accesible ──────────────────────────────────────────────────────────
COLORS = {
    "morado":      "#5B2B82",   # primario (encabezados, nav)
    "morado_osc":  "#43205F",   # hover
    "verde":       "#4F7A12",   # verde manzana oscuro (texto-safe)
    "verde_claro": "#8DC63F",   # verde manzana (acentos/marcadores)
    "salmon":      "#E8705B",   # acento cálido
    "mostaza":     "#B5800A",
    "teal":        "#1F7385",
    "azul":        "#2E5AAC",
    "rojo":        "#C0392B",
    "gris":        "#8A8A8A",
    "fondo":       "#F6F2F8",
    "texto":       "#211A28",
    "blanco":      "#FFFFFF",
    "borde":       "#D8CEE0",
}

# ── Localidades de Bogotá (código → nombre) ──────────────────────────────────
LOCALIDADES = {
    "01": "Usaquén", "02": "Chapinero", "03": "Santa Fe", "04": "San Cristóbal",
    "05": "Usme", "06": "Tunjuelito", "07": "Bosa", "08": "Kennedy",
    "09": "Fontibón", "10": "Engativá", "11": "Suba", "12": "Barrios Unidos",
    "13": "Teusaquillo", "14": "Los Mártires", "15": "Antonio Nariño",
    "16": "Puente Aranda", "17": "La Candelaria", "18": "Rafael Uribe Uribe",
    "19": "Ciudad Bolívar", "20": "Sumapaz",
}

def norm_localidad(nombre):
    """Normaliza nombre de localidad a Título legible."""
    if not nombre:
        return None
    return str(nombre).strip().title()

# ── Iconografía: pictograma + color por categoría ────────────────────────────
# Cada categoría usa un PICTOGRAMA representativo (Bootstrap Icons, MIT, en
# static/icons/) sobre un círculo de color. El pictograma diferencia las
# categorías sin depender del color (accesibilidad cognitiva y daltonismo).

ESTILO_MAPA1 = {  # por tipo de centro (ModServ)
    "CADIS+":             {"icon": "building-fill",   "color": "#5B2B82", "label": "CADIS+ (atención e inclusión social)"},
    "Centros Crecer":     {"icon": "flower1",         "color": "#4F7A12", "label": "Centros Crecer"},
    "Integrarte Interno": {"icon": "house-door-fill", "color": "#E8705B", "label": "Integrarte · atención interna"},
    "Integrarte Externo": {"icon": "people-fill",     "color": "#B5800A", "label": "Integrarte · atención externa"},
    "Otro":               {"icon": "geo-alt-fill",    "color": "#8A8A8A", "label": "Otro centro"},
}

ESTILO_MAPA2 = {  # por sector
    "Oficial":          {"icon": "mortarboard-fill", "color": "#5B2B82", "label": "Colegio oficial"},
    "No oficial":       {"icon": "book-fill",        "color": "#4F7A12", "label": "Colegio no oficial"},
    "Sin discapacidad": {"icon": "mortarboard-fill", "color": "#B0AAB8", "label": "No reporta estudiantes con discapacidad"},
}

ESTILO_MAPA3 = {  # por temática (8)
    "Bienestar y autonomía":                    {"icon": "emoji-smile-fill",  "color": "#5B2B82"},
    "Cultura, Recreación y Deporte":            {"icon": "trophy-fill",       "color": "#E8705B"},
    "Derechos humanos con enfoque diferencial": {"icon": "person-wheelchair", "color": "#1F7385"},
    "Desarrollo Económico, Industria y Turismo":{"icon": "briefcase-fill",    "color": "#B5800A"},
    "Hábitat":                                  {"icon": "house-fill",        "color": "#4F7A12"},
    "Movilidad":                                {"icon": "bus-front-fill",    "color": "#2E5AAC"},
    "Reconocimiento y apoyo a cuidadoras":      {"icon": "person-hearts",     "color": "#C0392B"},
    "Salud":                                    {"icon": "heart-pulse-fill",  "color": "#157A6E"},
    "Otra":                                     {"icon": "geo-alt-fill",      "color": "#8A8A8A"},
}

ESTILO_MAPA4 = {  # por población destinataria + equipamiento
    "Cuidadoras":            {"icon": "person-hearts",    "color": "#5B2B82", "label": "Servicio para personas cuidadoras"},
    "Familias y comunidad":  {"icon": "people-fill",      "color": "#4F7A12", "label": "Servicio para familias y comunidad"},
    "Equipamiento ancla":    {"icon": "house-heart-fill", "color": "#E8705B", "label": "Equipamiento de la Manzana del Cuidado"},
}

# ── Etiquetas de discapacidad (columnas dicotómicas) ─────────────────────────
DISC_LABELS = {
    "disc_visual":      "Visual",
    "disc_auditiva":    "Auditiva",
    "disc_fisica":      "Física",
    "disc_intelectual": "Intelectual",
    "disc_psicosocial": "Psicosocial",
    "disc_multiple":    "Múltiple",
}

# ── Textos narrativos (tomados del docx, español de Colombia, forma "usted") ──
TEXTOS = {
    "titulo":    "Mapa de cuidados y apoyos a personas con discapacidad en Bogotá",
    "subtitulo": "Explore la oferta pública de servicios cerca de usted.",
    "autoria":   "PNUD · IDECA · Alcaldía Mayor de Bogotá",

    "bienvenida": [
        "Bogotá cuenta con una red de servicios públicos para personas con "
        "discapacidad y para quienes las cuidan.",
        "Aquí la encuentra reunida y ubicada en el mapa.",
    ],

    "como_usar": {
        "titulo": "Cómo usar este sitio",
        "intro":  "Explore y encuentre los servicios que necesita en cuatro pasos:",
        "pasos": [
            ("map-fill",        "#5B2B82", "Elija un mapa",          "Seleccione uno de los cuatro mapas disponibles."),
            ("funnel-fill",     "#4F7A12", "Filtre o busque",        "Use los filtros o el buscador para encontrar lo que necesita."),
            ("hand-index-fill", "#E8705B", "Seleccione un punto",    "Haga clic sobre el servicio que le interese."),
            ("card-list",       "#2E5AAC", "Consulte la información","Revise dirección, teléfono, horarios y a quién atiende."),
        ],
        "consejo": "Puede acercarse a su localidad o su barrio para ver qué servicios hay cerca de usted.",
        "video_titulo": "Video en Lengua de Señas Colombiana (LSC)",
        "video_desc":   "Mire un video corto que explica cómo navegar los mapas.",
        "video_nota":   "Incluirá subtítulos en español, transcripción y controles de "
                        "reproducción. No se reproducirá automáticamente.",
    },

    "menu": {
        "titulo": "¿Qué está buscando?",
        "intro":  "Elija el mapa que más se acerque a lo que necesita. "
                  "Puede regresar a este menú en cualquier momento.",
    },

    "mapas": [
        {
            "id": "mapa1",
            "capa": "Cuidados_SDIS",
            "menu_icon": "building-fill", "menu_color": "#5B2B82",
            "menu_decision": "Si busca atención especializada, servicios de cuidado, apoyo y acompañamiento.",
            "menu_titulo": "Centros de atención directa",
            "menu_desc": "Centros públicos donde personas con discapacidad reciben "
                         "atención, formación y acompañamiento: CADIS, Crecer, "
                         "Renacer e Integrarte. Si está buscando un lugar al que "
                         "asistir o donde solicitar orientación, comience por aquí.",
            "titulo": "Centros distritales de atención directa",
            "intro":  "La Secretaría Distrital de Integración Social cuenta en Bogotá "
                      "con una red de centros donde las personas con discapacidad "
                      "reciben atención y apoyo cotidiano. Cada centro atiende distintas "
                      "edades y tipos de discapacidad.",
            "intro_facil": "Lugares para recibir atención y apoyo.",
            "alt": "Mapa de Bogotá con la ubicación de los centros de atención directa "
                   "de la Secretaría Distrital de Integración Social. Cada forma "
                   "representa un tipo de centro: CADIS, Crecer e Integrarte.",
        },
        {
            "id": "mapa2",
            "capa": "Educacion_Inclusiva",
            "cluster": True,   # 1.519 colegios: se agrupan para verse mejor
            "menu_icon": "mortarboard-fill", "menu_color": "#4F7A12",
            "menu_decision": "Si busca opciones educativas inclusivas.",
            "menu_titulo": "Educación inclusiva",
            "menu_desc": "Colegios oficiales y no oficiales que actualmente reciben "
                         "estudiantes con discapacidad. Si está buscando opciones "
                         "educativas para usted, para su hijo o hija, o para alguien a "
                         "quien acompaña o cuida, este mapa muestra el tipo de "
                         "discapacidades atendidas en los colegios actualmente.",
            "titulo": "Educación inclusiva",
            "intro":  "Este mapa muestra qué colegios oficiales y no oficiales de "
                      "Bogotá tienen actualmente matrícula de estudiantes con "
                      "discapacidad, y qué tipos de discapacidad atienden. No "
                      "constituye una garantía de cupo, pero sí ofrece una primera "
                      "orientación sobre dónde acercarse a consultar.",
            "intro_facil": "Colegios que reciben estudiantes con discapacidad.",
            "alt": "Mapa de Bogotá con los colegios que reportan estudiantes con "
                   "discapacidad. Los círculos son colegios oficiales y los triángulos "
                   "no oficiales; en gris, los que no reportan estudiantes con "
                   "discapacidad.",
        },
        {
            "id": "mapa3",
            "capa": "Oferta_discapacidad",
            "menu_icon": "grid-3x3-gap-fill", "menu_color": "#E8705B",
            "menu_decision": "Si quiere explorar actividades culturales y otros servicios.",
            "menu_titulo": "Otra oferta para personas con discapacidad",
            "menu_desc": "Talleres, programas culturales, deporte adaptado, asesorías "
                         "y otros servicios que ofrecen distintas entidades del "
                         "Distrito. Una vista amplia para descubrir oportunidades "
                         "menos conocidas.",
            "titulo": "Más allá de cuidados y educación",
            "intro":  "Bogotá ofrece mucha más oferta de la que se aprecia a primera "
                      "vista: talleres culturales, deporte adaptado, asesorías "
                      "jurídicas, programas de salud, espacios comunitarios. Esta "
                      "sección reúne servicios distritales que no aparecen en los "
                      "mapas anteriores.",
            "intro_facil": "Otras actividades y servicios en la ciudad.",
            "alt": "Mapa de Bogotá con servicios de distintas entidades del Distrito "
                   "para personas con discapacidad, agrupados por temática. Cada "
                   "temática tiene una forma y un color distintos.",
        },
        {
            "id": "mapa4",
            "capa": "Servicios_cuidadoras",
            "capa2": "Equipamiento_ancla",
            "menu_icon": "person-hearts", "menu_color": "#1F7385",
            "menu_decision": "Si usted cuida a una persona con discapacidad.",
            "menu_titulo": "Apoyo a personas cuidadoras",
            "menu_desc": "Si usted cuida a una persona con discapacidad, aquí "
                         "encontrará los servicios pensados para personas cuidadoras "
                         "en las Manzanas del Cuidado y en otros espacios distritales: "
                         "formación, descanso, asesoría jurídica, atención "
                         "psicosocial, actividades culturales.",
            "titulo": "Cuidar a quien cuida",
            "intro":  "Las Manzanas del Cuidado son espacios donde todas las personas "
                      "cuidadoras pueden acceder a formación, asesoría jurídica, "
                      "atención psicosocial, actividades culturales y tiempo para sí "
                      "mismas, mientras servicios complementarios atienden a las "
                      "personas a su cargo.",
            "intro_facil": "Apoyo para las personas que cuidan.",
            "alt": "Mapa de Bogotá con los servicios de las Manzanas del Cuidado "
                   "dirigidos a personas cuidadoras, sus familias y la comunidad, y "
                   "los equipamientos ancla. Los servicios se agrupan por cercanía; "
                   "toque un grupo para separarlos.",
        },
    ],

    "contexto": {
        "titulo": "Lo que hay detrás de este mapa",
        "parrafos": [
            ("La población",
             "En Bogotá viven alrededor de 458.000 personas con alguna dificultad "
             "funcional, según el Censo Nacional de Población y Vivienda de 2018 del "
             "DANE. Esto equivale a una de cada quince personas que caminan, "
             "estudian, trabajan, juegan o cuidan en la ciudad."),
            ("Las personas cuidadoras",
             "Detrás de muchas de esas personas hay alguien que cuida o brinda apoyos "
             "cotidianos. La mayoría son mujeres, y la mayoría lo hacen sin "
             "remuneración. Bogotá fue una de las primeras ciudades de la región en "
             "reconocer ese trabajo, a través del Sistema Distrital de Cuidado y de "
             "las Manzanas del Cuidado."),
            ("De dónde provienen estos datos",
             "Este mapa reúne información de cuatro fuentes oficiales: la Secretaría "
             "Distrital de Integración Social, la Secretaría Distrital de la Mujer, la "
             "Secretaría Distrital de Educación y la Secretaría General de la Alcaldía "
             "Mayor. Los datos se procesaron mediante un flujo abierto y documentado, "
             "desarrollado por el PNUD junto a IDECA."),
            ("Lo que falta",
             "Este mapa muestra la oferta institucional que está documentada. El "
             "territorio, sin embargo, sabe más. Las personas con discapacidad y las "
             "personas cuidadoras conocen servicios comunitarios, redes de apoyo, "
             "errores en las direcciones y horarios que han cambiado. Por eso, en el "
             "siguiente momento se les invita a participar."),
        ],
    },

    "creditos": {
        "titulo": "Este mapa también lo construye usted",
        "invitacion": "Si encontró un error, si conoce un servicio que no aparece, "
                      "si quiere sumar algo desde su experiencia o desde su "
                      "organización, escríbanos.",
        "aportes": [
            ("exclamation-triangle-fill", "#E8705B", "Reportar un error en un servicio",
             "Una dirección que cambió, un horario incorrecto, un servicio que ya no existe."),
            ("plus-circle-fill", "#4F7A12", "Sugerir un servicio que falta",
             "Un programa distrital, comunitario o de organización social que debería figurar."),
            ("universal-access-circle", "#2E5AAC", "Mejorar la accesibilidad de este sitio",
             "Mejoras que permitan que personas con distintas dificultades puedan hacer "
             "mejor uso de estos mapas."),
        ],
        "fuentes": "Datos: Secretaría Distrital de Integración Social, Secretaría "
                   "Distrital de la Mujer, Secretaría Distrital de Educación, "
                   "Secretaría General de la Alcaldía Mayor de Bogotá.",
        "procesamiento": "Procesamiento de datos: PNUD. Repositorio público con código "
                         "y documentación disponible.",
        "publicacion": "Publicación y mantenimiento: IDECA — Infraestructura de Datos "
                        "Espaciales para el Distrito Capital.",
        "programa": "Producto del Programa Conjunto en Colombia: Cuidados no "
                    "remunerados, discapacidad y enfoque de género transformador.",
    },
}
