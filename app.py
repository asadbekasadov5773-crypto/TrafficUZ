import streamlit as st
import folium
from streamlit_folium import st_folium
from math import sqrt

# =========================
# SOZLAMALAR
# =========================

st.set_page_config(
    page_title="TrafficUZ",
    page_icon="🚦",
    layout="wide"
)

# =========================
# DIZAYN
# =========================

st.markdown("""
<style>
    .stApp {
        background: #07111F;
        color: #F5F9FF;
    }

    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #F5F9FF;
        margin-bottom: 0;
    }

    .subtitle {
        color: #8FA5C0;
        font-size: 16px;
        margin-bottom: 25px;
    }

    .card {
        background: #12233A;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #203A5C;
    }

    .green {
        color: #29D17F;
        font-weight: bold;
    }

    .yellow {
        color: #F6C945;
        font-weight: bold;
    }

    .red {
        color: #FF5B70;
        font-weight: bold;
    }

    .route-title {
        color: #2F80FF;
        font-size: 24px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# SVETOFORLAR
# =========================

traffic_lights = [
    {
        "lat": 41.3111,
        "lon": 69.2797,
        "name": "Amir Temur ko'chasi",
        "status": "YASHIL",
        "time": 18,
        "traffic": "O'rtacha"
    },
    {
        "lat": 41.2995,
        "lon": 69.2401,
        "name": "Toshkent markazi",
        "status": "QIZIL",
        "time": 32,
        "traffic": "Yuqori"
    },
    {
        "lat": 41.3275,
        "lon": 69.2817,
        "name": "Yunusobod",
        "status": "SARIQ",
        "time": 7,
        "traffic": "O'rtacha"
    },
    {
        "lat": 41.2856,
        "lon": 69.2037,
        "name": "Chilonzor",
        "status": "QIZIL",
        "time": 25,
        "traffic": "Yuqori"
    },
    {
        "lat": 41.3120,
        "lon": 69.2350,
        "name": "Shayxontohur",
        "status": "YASHIL",
        "time": 20,
        "traffic": "Past"
    },
    {
        "lat": 41.3110,
        "lon": 69.3340,
        "name": "Mirzo Ulug'bek",
        "status": "YASHIL",
        "time": 15,
        "traffic": "O'rtacha"
    },
    {
        "lat": 41.2260,
        "lon": 69.2230,
        "name": "Sergeli",
        "status": "QIZIL",
        "time": 28,
        "traffic": "Yuqori"
    }
]

# =========================
# XIZMATLAR
# =========================

services = [
    {
        "lat": 41.305,
        "lon": 69.260,
        "name": "Smart Auto Service",
        "type": "🔧 Avtoservis"
    },
    {
        "lat": 41.318,
        "lon": 69.250,
        "name": "Premium Avtoservis",
        "type": "🔧 Avtoservis"
    },
    {
        "lat": 41.290,
        "lon": 69.220,
        "name": "Auto Master",
        "type": "🔧 Avtoservis"
    },
    {
        "lat": 41.300,
        "lon": 69.300,
        "name": "Tezkor Moyka",
        "type": "🧽 Avtomoyka"
    },
    {
        "lat": 41.275,
        "lon": 69.250,
        "name": "Oil Service",
        "type": "⛽ Yoqilg'i"
    }
]

# =========================
# FUNKSIYALAR
# =========================

def normalize(text):
    text = text.lower()

    replacements = {
        "o‘": "o",
        "o'": "o",
        "g‘": "g",
        "g'": "g",
        "ʻ": "'",
        "’": "'"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def find_location(text):
    text = normalize(text)

    for light in traffic_lights:
        name = normalize(light["name"])

        if name in text:
            return light

        # qisqa nom bo'yicha
        first_word = name.split()[0]

        if first_word in text:
            return light

    return None


def route_search(query):
    """
    Masalan:
    Amir Temurdan Yunusobodga
    Amir Temur -> Yunusobod
    Amir Temur - Yunusobod
    """

    q = normalize(query)

    separators = [
        "dan ",
        " -> ",
        " - ",
        " to ",
        "dan",
    ]

    start = None
    end = None

    # "Amir Temurdan Yunusobodga"
    if "dan " in q:
        parts = q.split("dan ", 1)

        if len(parts) == 2:
            start_text = parts[0].strip()
            end_text = parts[1].strip()

            end_text = end_text.replace("ga", "").strip()
            end_text = end_text.replace("gacha", "").strip()

            start = find_location(start_text)
            end = find_location(end_text)

    # "Amir Temur -> Yunusobod"
    if start is None or end is None:
        for sep in [" -> ", " - "]:
            if sep in q:
                parts = q.split(sep, 1)

                start = find_location(parts[0].strip())
                end = find_location(parts[1].strip())

                if start and end:
                    break

    return start, end


def distance_point_to_line(point, start, end):
    """
    Nuqtaning start-end chizig'iga taxminiy masofasi.
    """
    x = point["lat"]
    y = point["lon"]

    x1 = start["lat"]
    y1 = start["lon"]

    x2 = end["lat"]
    y2 = end["lon"]

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        return sqrt((x - x1) ** 2 + (y - y1) ** 2)

    t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)

    t = max(0, min(1, t))

    nearest_x = x1 + t * dx
    nearest_y = y1 + t * dy

    return sqrt(
        (x - nearest_x) ** 2 +
        (y - nearest_y) ** 2
    )


def get_route_lights(start, end):

    result = []

    for light in traffic_lights:

        distance = distance_point_to_line(
            light,
            start,
            end
        )

        # Marshrutga yaqin svetoforlar
        if distance < 0.045:

            # startdan masofasi
            d = sqrt(
                (light["lat"] - start["lat"]) ** 2 +
                (light["lon"] - start["lon"]) ** 2
            )

            result.append((d, light))

    result.sort(key=lambda x: x[0])

    return [item[1] for item in result]


def status_color(status):

    if status == "YASHIL":
        return "green"

    if status == "SARIQ":
        return "yellow"

    return "red"


# =========================
# HEADER
# =========================

st.markdown(
    '<div class="main-title">🚦 TrafficUZ</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">O‘zbekiston uchun aqlli yo‘l va svetofor tizimi</div>',
    unsafe_allow_html=True
)

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.markdown("## 🚦 TrafficUZ")

    st.markdown("---")

    page = st.radio(
        "Menyu",
        [
            "🏠 Bosh sahifa",
            "🚦 Svetoforlar",
            "🔧 Avtoservislar"
        ]
    )

    st.markdown("---")

    st.info(
        "TrafficUZ — haydovchilarga "
        "yo‘l harakatini qulay kuzatishga yordam beruvchi loyiha."
    )

# =========================
# QIDIRUV
# =========================

st.markdown("### 🔎 Marshrut yoki joy qidirish")

query = st.text_input(
    "",
    placeholder="Masalan: Amir Temurdan Yunusobodga",
    label_visibility="collapsed"
)

# =========================
# MARSHRUT QIDIRISH
# =========================

route_start = None
route_end = None
route_lights = []

if query:

    route_start, route_end = route_search(query)

    if route_start and route_end:

        route_lights = get_route_lights(
            route_start,
            route_end
        )

        st.markdown(
            f"""
            <div class="card">
                <div class="route-title">
                    🚗 Marshrut
                </div>
                <h3>
                    {route_start["name"]} → {route_end["name"]}
                </h3>
                <p>
                    Yo‘ldagi svetoforlar: 
                    <b>{len(route_lights)} ta</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        found = find_location(query)

        if found:

            st.success(
                f"🚦 {found['name']} topildi"
            )

        else:

            st.warning(
                "Joy yoki marshrut topilmadi. "
                "Masalan: Amir Temurdan Yunusobodga"
            )

# =========================
# XARITA
# =========================

st.markdown("### 🗺️ Xarita")

if route_start and route_end:

    center_lat = (
        route_start["lat"] +
        route_end["lat"]
    ) / 2

    center_lon = (
        route_start["lon"] +
        route_end["lon"]
    ) / 2

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles="OpenStreetMap"
    )

    # START
    folium.Marker(
        [
            route_start["lat"],
            route_start["lon"]
        ],
        tooltip="Boshlanish",
        popup=f"🟢 {route_start['name']}",
        icon=folium.Icon(
            color="green",
            icon="play"
        )
    ).add_to(m)

    # END
    folium.Marker(
        [
            route_end["lat"],
            route_end["lon"]
        ],
        tooltip="Manzil",
        popup=f"🔴 {route_end['name']}",
        icon=folium.Icon(
            color="red",
            icon="flag"
        )
    ).add_to(m)

    # ROUTE LINE
    folium.PolyLine(
        [
            [
                route_start["lat"],
                route_start["lon"]
            ],
            [
                route_end["lat"],
                route_end["lon"]
            ]
        ],
        color="#2F80FF",
        weight=6,
        opacity=0.8
    ).add_to(m)

    # ROUTE TRAFFIC LIGHTS
    for light in route_lights:

        color = "green"

        if light["status"] == "QIZIL":
            color = "red"

        elif light["status"] == "SARIQ":
            color = "orange"

        folium.Marker(
            [
                light["lat"],
                light["lon"]
            ],
            tooltip=f"🚦 {light['name']}",
            popup=f"""
            🚦 <b>{light['name']}</b><br>
            Holat: {light['status']}<br>
            Vaqt: {light['time']} soniya<br>
            Tirbandlik: {light['traffic']}
            """,
            icon=folium.Icon(
                color=color,
                icon="traffic-light"
            )
        ).add_to(m)

else:

    m = folium.Map(
        location=[41.3111, 69.2797],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    # Barcha svetoforlar
    for light in traffic_lights:

        color = "green"

        if light["status"] == "QIZIL":
            color = "red"

        elif light["status"] == "SARIQ":
            color = "orange"

        folium.Marker(
            [
                light["lat"],
                light["lon"]
            ],
            tooltip=f"🚦 {light['name']}",
            popup=f"""
            🚦 <b>{light['name']}</b><br>
            Holat: {light['status']}<br>
            Vaqt: {light['time']} soniya<br>
            Tirbandlik: {light['traffic']}
            """,
            icon=folium.Icon(
                color=color,
                icon="traffic-light"
            )
        ).add_to(m)

    # Xizmatlar
    for service in services:

        folium.Marker(
            [
                service["lat"],
                service["lon"]
            ],
            tooltip=service["name"],
            popup=f"""
            {service['type']}<br>
            <b>{service['name']}</b>
            """,
            icon=folium.Icon(
                color="blue",
                icon="wrench"
            )
        ).add_to(m)


st_folium(
    m,
    width=None,
    height=600,
    returned_objects=[]
)

# =========================
# MARSHRUT SVETOFORLARI
# =========================

if route_start and route_end:

    st.markdown("### 🚦 Marshrutdagi svetoforlar")

    if route_lights:

        for i, light in enumerate(route_lights, 1):

            css = status_color(light["status"])

            st.markdown(
                f"""
                <div class="card">
                    <h4>
                        {i}. 🚦 {light["name"]}
                    </h4>

                    <p>
                        Holat:
                        <span class="{css}">
                            {light["status"]}
                        </span>
                    </p>

                    <p>
                        ⏱️ {light["time"]} soniya
                        &nbsp;&nbsp;|&nbsp;&nbsp;
                        🚗 Tirbandlik: {light["traffic"]}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.info(
            "Bu marshrut bo‘yicha demo ma'lumotlarda "
            "svetofor topilmadi."
        )

# =========================
# SVETOFORLAR SAHIFASI
# =========================

if page == "🚦 Svetoforlar":

    st.markdown("## 🚦 Barcha svetoforlar")

    for light in traffic_lights:

        css = status_color(light["status"])

        st.markdown(
            f"""
            <div class="card">
                <h3>🚦 {light["name"]}</h3>

                <p>
                    Holat:
                    <span class="{css}">
                        {light["status"]}
                    </span>
                </p>

                <p>
                    ⏱️ {light["time"]} soniya
                </p>

                <p>
                    🚗 Tirbandlik: {light["traffic"]}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================
# AVTOSERVISLAR
# =========================

if page == "🔧 Avtoservislar":

    st.markdown("## 🔧 Avtomobil xizmatlari")

    for service in services:

        st.markdown(
            f"""
            <div class="card">
                <h3>{service["type"]}</h3>
                <p>{service["name"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )