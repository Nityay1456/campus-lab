import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime
from PIL import Image
import matplotlib.pyplot as plt

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Campus Living Lab AI",
    page_icon="🧭",
    layout="wide"
)

# ================== POWER BI DARK THEME ==================
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: #e6e6e6; }
h1, h2, h3 { color: #ffffff; font-weight: 600; }

[data-testid="metric-container"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    padding: 18px;
    border-radius: 12px;
}

[data-testid="stDataFrame"] {
    background-color: #161b22;
    border-radius: 12px;
}

section[data-testid="stSidebar"] {
    background-color: #0b0f14;
    border-right: 1px solid #30363d;
}

.stButton>button {
    background: linear-gradient(135deg,#2563eb,#1d4ed8);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.6rem 1rem;
    font-weight: 600;
}
hr { border-color: #30363d; }
</style>
""", unsafe_allow_html=True)

# ================== USERS ==================
USERS = {
    "admin": {"password": "admin123"},
    "viewer": {"password": "viewer123"}
}

# ================== SESSION ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "prev_counts" not in st.session_state:
    st.session_state.prev_counts = {}

# ================== LOGIN PAGE ==================
def login_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("## 🧭 Campus Living Lab AI")
        st.caption("Power BI–Style Campus Traffic Dashboard")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("🔐 Sign In", use_container_width=True):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.caption("Demo login: admin / viewer")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ================== LOGOUT ==================
def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    auto_refresh = st.toggle("Auto Refresh", True)
    refresh_interval = st.slider("Refresh Interval (sec)", 5, 30, 6)
    st.divider()
    st.markdown(f"👤 **{st.session_state.user}**")
    st.button("Logout", on_click=logout)

# ================== DATA CONFIG ==================
HIGH = 260
MEDIUM = 150

ZONES = [
    "Main Gate", "Secondary Gate",
    "Hostel Block A", "Hostel Block B",
    "Academic Block 1", "Academic Block 2",
    "Library", "Cafeteria",
    "Auditorium", "Sports Complex"
]

ZONE_COORDS = {
    "Main Gate": (0.18, 0.88),
    "Secondary Gate": (0.78, 0.88),

    "Hostel Block A": (0.33, 0.46),
    "Hostel Block B": (0.18, 0.40),

    "Library": (0.36, 0.18),

    "Academic Block 1": (0.50, 0.28),
    "Academic Block 2": (0.62, 0.28),

    "Cafeteria": (0.38, 0.52),

    "Auditorium": (0.60, 0.50),

    "Sports Complex": (0.75, 0.22),
}


# ================== HELPERS ==================
def get_trend(current, previous):
    if previous is None:
        return "Stable"
    if current > previous:
        return "Increasing"
    if current < previous:
        return "Decreasing"
    return "Stable"

def ai_recommendation(level, trend, zone):
    if level == "High" and trend == "Increasing":
        return "Immediate crowd control required"
    if level == "High":
        return "Monitor closely and manage entry"
    if level == "Medium" and trend == "Increasing":
        return "Prepare for congestion"
    if level == "Medium":
        return "Monitor traffic flow"
    return "Normal operations"

# ================== HEADER ==================
st.markdown("# 🧭 Campus Living Lab AI")
st.caption("Power BI–Style Campus Traffic Monitoring")
st.divider()

# ================== DATA ==================
rows = []

for z in ZONES:
    count = random.randint(40, 350)

    level = "High" if count > HIGH else "Medium" if count > MEDIUM else "Low"
    prev = st.session_state.prev_counts.get(z)
    trend = get_trend(count, prev)

    rows.append({
        "Zone": z,
        "People Count": count,
        "Traffic Level": level,
        "Trend": trend,
        "AI Recommendation": ai_recommendation(level, trend, z)
    })

    st.session_state.prev_counts[z] = count

df = pd.DataFrame(rows)

# ================== METRICS ==================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Zones", len(ZONES))
c2.metric("Low Congestion", (df["Traffic Level"] == "Low").sum())
c3.metric("Medium Congestion", (df["Traffic Level"] == "Medium").sum())
c4.metric("High Congestion", (df["Traffic Level"] == "High").sum())

st.caption(f"⏱ Last updated: {datetime.now().strftime('%H:%M:%S')}")
st.divider()

# ================== UPPER SECTION ==================
st.markdown("### 📊 Live Campus Traffic Data")
st.dataframe(df, use_container_width=True)
st.divider()

# ================== BOTTOM SECTION ==================
st.markdown("### 🗺️ Campus Traffic Map")

plt.rcParams["figure.facecolor"] = "#0e1117"
plt.rcParams["axes.facecolor"] = "#0e1117"

campus_map = Image.open("new map.jpg.jpeg")
fig, ax = plt.subplots(figsize=(14, 9))
ax.imshow(campus_map)
ax.axis("off")

for _, r in df.iterrows():
    x, y = ZONE_COORDS[r["Zone"]]
    x *= campus_map.size[0]
    y *= campus_map.size[1]

    color = "green" if r["Traffic Level"] == "Low" else \
            "orange" if r["Traffic Level"] == "Medium" else "red"

    ax.scatter(x, y, s=130, c=color)
    ax.text(
        x + 8, y - 8,
        f'{r["Zone"]}\n{r["People Count"]}',
        fontsize=9,
        color="white",
        bbox=dict(facecolor="black", alpha=0.6, pad=2)
    )

st.pyplot(fig)

st.markdown("**Legend:** 🟢 Low 🟡 Medium 🔴 High")

# ================== AUTO REFRESH ==================
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

