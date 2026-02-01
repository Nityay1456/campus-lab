# Campus Living Lab AI – Smart Overview Dashboard
# Author: NoCode | AMD Slingshot

import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime
from PIL import Image
import matplotlib.pyplot as plt

# ---------------- APP CONFIG ----------------
APP_NAME = "Campus Living Lab AI"
APP_TAGLINE = "Smart Campus Command Dashboard"
APP_VERSION = "v1.0"

# ---------------- ZONES ----------------
ZONES = [
    "Main Gate", "Secondary Gate",
    "Hostel Block A", "Hostel Block B",
    "Academic Block 1", "Academic Block 2",
    "Library", "Cafeteria",
    "Auditorium", "Sports Complex"
]

# ✅ FIXED coordinates aligned to your campus map image
ZONE_COORDS = {
    # Gates (bottom road)
    "Main Gate": (0.18, 0.88),
    "Secondary Gate": (0.82, 0.88),

    # Hostel & Cafeteria (left side)
    "Hostel Block A": (0.25, 0.55),
    "Cafeteria": (0.36, 0.62),

    # Library (top-left)
    "Library": (0.34, 0.28),

    # Academic blocks (center-top)
    "Academic Block 1": (0.56, 0.76),
    "Academic Block 2": (0.44, 0.74),

    # Sports & Auditorium (right side)
    "Sports Complex": (0.78, 0.33),
    "Auditorium": (0.73, 0.46),

    # Hostel Block B (center-bottom)
    "Hostel Block B": (0.50, 0.58),
}


HIGH_TRAFFIC = 260
MEDIUM_TRAFFIC = 150

USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "viewer": {"password": "viewer123", "role": "Viewer"}
}

# ---------------- PAGE ----------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧭",
    layout="wide"
)

# ---------------- SESSION DEFAULTS ----------------
defaults = {
    "logged_in": False,
    "username": None,
    "user_role": None,
    "notifications": [],
    "auto_refresh": True,
    "refresh_interval": 6,
    "demo_mode": False,
    "notify_enabled": True
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- LOGIN ----------------
def login():
    st.markdown(f"## 🧭 {APP_NAME}")
    st.caption(APP_TAGLINE)

    st.markdown(
        f"**Version:** {APP_VERSION}  \n"
        f"**Event:** AMD Slingshot – Campus as a Living Lab"
    )

    st.divider()

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("### 🔐 Sign In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Sign in", use_container_width=True):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_role = USERS[username]["role"]
            else:
                st.error("Invalid username or password")

        st.caption("Roles supported: Admin • Viewer")

if not st.session_state.logged_in:
    login()
    st.stop()

def logout():
    st.session_state.logged_in = False

# ---------------- SIDEBAR SETTINGS ----------------
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    st.session_state.auto_refresh = st.toggle(
        "Auto refresh", value=st.session_state.auto_refresh
    )

    st.session_state.refresh_interval = st.slider(
        "Refresh interval (seconds)",
        3, 20, st.session_state.refresh_interval,
        disabled=not st.session_state.auto_refresh
    )

    st.session_state.demo_mode = st.toggle(
        "Demo mode (freeze data)", value=st.session_state.demo_mode
    )

    st.session_state.notify_enabled = st.toggle(
        "Enable notifications", value=st.session_state.notify_enabled
    )

    st.divider()
    st.caption(f"👤 {st.session_state.username}")
    st.button("Logout", on_click=logout)

# ---------------- HEADER ----------------
st.markdown(f"# 🧭 {APP_NAME}")
st.caption(APP_TAGLINE)

# ---------------- DATA LOGIC ----------------
def add_notification(zone, level):
    if not st.session_state.notify_enabled:
        return
    ts = datetime.now().strftime("%H:%M:%S")
    msg = f"[{ts}] {zone} — {level}"
    if msg not in st.session_state.notifications:
        st.session_state.notifications.insert(0, msg)

def generate_data():
    rows = []
    alert_count = 0

    for zone in ZONES:
        people = random.randint(40, 350)

        if people > HIGH_TRAFFIC:
            level = "High Traffic"
            alert_count += 1
            add_notification(zone, level)
        elif people > MEDIUM_TRAFFIC:
            level = "Medium Traffic"
            alert_count += 1
            add_notification(zone, level)
        else:
            level = "Low Traffic"

        rows.append({
            "Zone": zone,
            "No. of People": people,
            "Traffic Level": level
        })

    return pd.DataFrame(rows), alert_count

if st.session_state.demo_mode and "demo_data" in st.session_state:
    data, campus_alert = st.session_state.demo_data
else:
    data, campus_alert = generate_data()
    if st.session_state.demo_mode:
        st.session_state.demo_data = (data, campus_alert)

# ---------------- METRICS ----------------
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("People on Campus", data["No. of People"].sum())
with c2:
    st.metric("Zones in Alert", campus_alert)
with c3:
    st.metric("System Status", "LIVE")

st.divider()

# ---------------- MAIN LAYOUT ----------------
left, right = st.columns([2.2, 1])

with left:
    st.subheader("📊 Live Campus Traffic")
    st.dataframe(data, use_container_width=True)

    # -------- CAMPUS MAP --------
    st.subheader("🗺️ Campus Map (Zone Awareness)")

    campus_map = Image.open("campus_map.png")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(campus_map)
    ax.axis("off")

    for _, row in data.iterrows():
        zone = row["Zone"]
        people = row["No. of People"]
        level = row["Traffic Level"]

        x, y = ZONE_COORDS.get(zone, (0.5, 0.5))
        x_img = x * campus_map.size[0]
        y_img = y * campus_map.size[1]

        color = "green"
        if level == "Medium Traffic":
            color = "orange"
        elif level == "High Traffic":
            color = "red"

        ax.scatter(x_img, y_img, c=color, s=120, edgecolors="black")
        ax.text(
            x_img + 6, y_img - 6,
            f"{zone}\n{people} ppl",
            fontsize=8,
            color="white",
            bbox=dict(facecolor="black", alpha=0.6, pad=2)
        )

    st.pyplot(fig)

with right:
    st.subheader("🔔 Notifications")
    if st.session_state.notifications:
        for note in st.session_state.notifications[:6]:
            st.info(note)
    else:
        st.caption("No active alerts")

    st.divider()

    st.subheader("🎯 Action Center")
    if campus_alert > 0:
        st.warning(f"Campus Alert Level: {campus_alert} zones affected")
    else:
        st.success("Campus operating normally")

# ---------------- AUTO REFRESH ----------------
if st.session_state.auto_refresh and not st.session_state.demo_mode:
    time.sleep(st.session_state.refresh_interval)
    st.rerun()
