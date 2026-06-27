import streamlit as st
import sqlite3
import uuid
import base64
import time
import hashlib
import os
from datetime import datetime

# ── PAGE CONFIGURATION ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tourgram",
    page_icon="📷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DATABASE SETUP ─────────────────────────────────────────────────────────────
DB_PATH = "tourgram.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            avatar_url TEXT DEFAULT '',
            bio TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS places (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            district TEXT NOT NULL,
            image TEXT NOT NULL,
            caption TEXT DEFAULT '',
            history TEXT DEFAULT '',
            budget TEXT DEFAULT '',
            safety TEXT DEFAULT '',
            stars INTEGER DEFAULT 5,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id TEXT PRIMARY KEY,
            place_id TEXT NOT NULL,
            author TEXT NOT NULL,
            user_id TEXT,
            text TEXT NOT NULL,
            rating INTEGER DEFAULT 5,
            certified INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(place_id) REFERENCES places(id)
        );
        CREATE TABLE IF NOT EXISTS votes (
            id TEXT PRIMARY KEY,
            place_id TEXT NOT NULL,
            user_id TEXT,
            session_id TEXT,
            vote_type TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    # Seed initial places if empty
    c.execute("SELECT COUNT(*) FROM places")
    if c.fetchone()[0] == 0:
        seed_data = [
            ("p1", "system", "u/rajan_travels", "Phewa Lake", "Kaski",
             "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJkhK2TPskum-I6Uqf5HX3FFO2jMsD7_LNDw&s",
             "The jewel of Pokhara — serene, majestic, unforgettable.",
             "Phewa Lake is the second largest lake in Nepal, located in Pokhara. It has been a hub for travellers for centuries, with the iconic Tal Barahi Temple sitting on a small island at its centre.",
             "Entry free. Boat rides from NPR 500/hr. Rowboats available for self-rowing.",
             "Very safe. Lifeguards present during peak hours. Avoid during heavy rain season.", 5),
            ("p2", "system", "u/anita_explorer", "Pashupatinath Temple", "Kathmandu",
             "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQyHqvQcW5pKYN4X8bFFl7aM9oolY3HTYzyYg&s",
             "Sacred, ancient, deeply spiritual — a must for every visitor to Nepal.",
             "One of the most sacred Hindu temples in the world, dating back to the 5th century. Dedicated to Lord Shiva, it sits on the banks of the Bagmati River.",
             "Foreign nationals: NPR 1000 entry. Locals: free. Best visited early morning.",
             "Safe. Follow dress code rules inside. Non-Hindus cannot enter the main temple.", 5),
            ("p3", "system", "u/bikram_hikes", "Annapurna Base Camp", "Kaski",
             "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTq3B0EGxY6Z2l9nN408GcOY2cN21LvqjNbHQ&s",
             "A 360° amphitheatre of Himalayan giants — nothing on earth compares.",
             "At 4,130m, ABC is one of the most iconic trekking destinations in the world. Surrounded by peaks over 7,000m, it offers a 360° amphitheatre of the Himalayas.",
             "Trek permits: NPR 3000. Guide recommended: NPR 2500/day. 7–12 day round trip.",
             "Altitude sickness risk. Acclimatise properly. Do not rush the ascent.", 5),
            ("p4", "system", "u/sara_wanderer", "Chitwan National Park", "Chitwan",
             "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTuUxpwjHWDBdDhlnJsn1NF4GduMVQ6W_IVXA&s",
             "UNESCO wilderness where rhinos roam free and the jungle breathes.",
             "UNESCO World Heritage Site. Home to one-horned rhinos and Bengal tigers. One of the best wildlife parks in Asia, established in 1973.",
             "Entry: NPR 1500. Jeep safari: NPR 2500. Elephant breeding centre: NPR 500.",
             "Stay with guides at all times. Do not wander alone near the jungle edges.", 5),
            ("p5", "system", "u/deepak_lens", "Boudhanath Stupa", "Kathmandu",
             "https://lp-cms-production.imgix.net/2019-06/813869da84003e9ab623499ae2465723-bodhnath-stupa.jpg?w=1200&auto=format",
             "The all-seeing eyes of Buddha watching over the valley at dusk.",
             "One of the largest stupas in the world and a centre of Tibetan Buddhism in Nepal. The all-seeing eyes of Buddha watch over the valley from every angle.",
             "Entry: NPR 400 for foreigners. Best visited at dawn or dusk for the butter lamp ceremony.",
             "Very safe. Busy tourist area. Watch out for pickpockets in crowd.", 5),
            ("p6", "system", "u/mina_clicks", "Rara Lake", "Mugu",
             "https://highcampadventure.com/uploads/fullbanner/biggest-lake-of-nepal-rara-lake.webp",
             "Nepal's best-kept secret — crystal blue waters hidden in Karnali.",
             "Nepal's largest lake, hidden in the remote Karnali region at 2,990m elevation. Crystal-clear blue waters surrounded by dense forests — one of Nepal's best-kept secrets.",
             "Flight to Talcha: ~NPR 15,000. Trek + permits extra. Very limited accommodation nearby.",
             "Remote area. Go with an experienced guide. Very limited phone signal.", 5),
        ]
        c.executemany("""INSERT INTO places (id,user_id,username,title,district,image,caption,history,budget,safety,stars)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", seed_data)
        seed_reviews = [
            (str(uuid.uuid4()), "p1", "u/sara_wanderer", None, "Best sunrise I've ever seen. The reflection of Machhapuchhre is unreal.", 5, 1),
            (str(uuid.uuid4()), "p1", "Guest123", None, "Absolutely stunning at sunrise!", 5, 0),
            (str(uuid.uuid4()), "p2", "u/deepak_lens", None, "Spiritual and deeply peaceful experience.", 5, 1),
            (str(uuid.uuid4()), "p2", "Guest123", None, "Must visit during Shivaratri — incredible atmosphere.", 5, 0),
            (str(uuid.uuid4()), "p3", "u/bikram_hikes", None, "Life-changing trek. Nothing prepares you for that view.", 5, 1),
            (str(uuid.uuid4()), "p4", "u/mina_clicks", None, "Saw a rhino up close — absolutely incredible!", 5, 1),
            (str(uuid.uuid4()), "p5", "Guest123", None, "Peaceful and majestic. The evening kora is magical.", 4, 0),
            (str(uuid.uuid4()), "p6", "u/rajan_travels", None, "Pure paradise. Worth every rupee and every step.", 5, 1),
        ]
        c.executemany("INSERT INTO reviews (id,place_id,author,user_id,text,rating,certified) VALUES (?,?,?,?,?,?,?)", seed_reviews)
    conn.commit()
    conn.close()

init_db()

# ── DB HELPERS ─────────────────────────────────────────────────────────────────
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_user_by_username(username):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(uid):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(username, password):
    uid = str(uuid.uuid4())
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (id,username,password_hash) VALUES (?,?,?)",
                     (uid, username, hash_pw(password)))
        conn.commit()
        conn.close()
        return uid
    except sqlite3.IntegrityError:
        conn.close()
        return None

def update_user_profile(uid, avatar_url, bio):
    conn = get_db()
    conn.execute("UPDATE users SET avatar_url=?, bio=? WHERE id=?", (avatar_url, bio, uid))
    conn.commit()
    conn.close()

def get_all_places():
    conn = get_db()
    rows = conn.execute("SELECT * FROM places ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_place_by_id(pid):
    conn = get_db()
    row = conn.execute("SELECT * FROM places WHERE id=?", (pid,)).fetchone()
    conn.close()
    return dict(row) if row else None

def insert_place(data):
    conn = get_db()
    conn.execute("""INSERT INTO places (id,user_id,username,title,district,image,caption,history,budget,safety,stars)
                    VALUES (:id,:user_id,:username,:title,:district,:image,:caption,:history,:budget,:safety,:stars)""", data)
    conn.commit()
    conn.close()

def get_reviews(place_id):
    conn = get_db()
    rows = conn.execute("SELECT * FROM reviews WHERE place_id=? ORDER BY created_at DESC", (place_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_review(place_id, author, user_id, text, rating, certified):
    rid = str(uuid.uuid4())
    conn = get_db()
    conn.execute("INSERT INTO reviews (id,place_id,author,user_id,text,rating,certified) VALUES (?,?,?,?,?,?,?)",
                 (rid, place_id, author, user_id, text, rating, certified))
    conn.commit()
    conn.close()

def get_vote_counts(place_id):
    conn = get_db()
    up = conn.execute("SELECT COUNT(*) FROM votes WHERE place_id=? AND vote_type='up'", (place_id,)).fetchone()[0]
    dn = conn.execute("SELECT COUNT(*) FROM votes WHERE place_id=? AND vote_type='down'", (place_id,)).fetchone()[0]
    conn.close()
    return up, dn

def get_user_vote(place_id, user_id=None, session_id=None):
    conn = get_db()
    if user_id:
        row = conn.execute("SELECT vote_type FROM votes WHERE place_id=? AND user_id=?", (place_id, user_id)).fetchone()
    else:
        row = conn.execute("SELECT vote_type FROM votes WHERE place_id=? AND session_id=?", (place_id, session_id)).fetchone()
    conn.close()
    return row[0] if row else None

def cast_vote(place_id, vote_type, user_id=None, session_id=None):
    conn = get_db()
    existing = get_user_vote(place_id, user_id, session_id)
    if existing == vote_type:
        if user_id:
            conn.execute("DELETE FROM votes WHERE place_id=? AND user_id=?", (place_id, user_id))
        else:
            conn.execute("DELETE FROM votes WHERE place_id=? AND session_id=?", (place_id, session_id))
    elif existing:
        if user_id:
            conn.execute("UPDATE votes SET vote_type=? WHERE place_id=? AND user_id=?", (vote_type, place_id, user_id))
        else:
            conn.execute("UPDATE votes SET vote_type=? WHERE place_id=? AND session_id=?", (vote_type, place_id, session_id))
    else:
        conn.execute("INSERT INTO votes (id,place_id,user_id,session_id,vote_type) VALUES (?,?,?,?,?)",
                     (str(uuid.uuid4()), place_id, user_id, session_id, vote_type))
    conn.commit()
    conn.close()

# ── AVATAR HELPER ──────────────────────────────────────────────────────────────
def get_initials_avatar(name, size=42):
    initials = "".join([w[0].upper() for w in name.split("_") if w])[:2]
    colors = ["#0d9488","#0891b2","#7c3aed","#db2777","#ea580c","#16a34a","#dc2626"]
    color = colors[hash(name) % len(colors)]
    svg = f"""<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
      <circle cx="{size//2}" cy="{size//2}" r="{size//2}" fill="{color}"/>
      <text x="50%" y="50%" dominant-baseline="central" text-anchor="middle"
            font-family="Inter,sans-serif" font-size="{size//2.5}" font-weight="700" fill="white">{initials}</text>
    </svg>"""
    b64 = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{b64}"

def avatar_html(username, avatar_url="", size=42):
    src = avatar_url if avatar_url and avatar_url.startswith("http") else get_initials_avatar(username, size)
    return f'<img src="{src}" style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;border:2px solid #14b8a6;box-shadow:0 2px 8px rgba(20,184,166,0.2);">'

# ── INIT SESSION ───────────────────────────────────────────────────────────────
def init():
    defaults = {
        "page": "home",
        "selected_place": None,
        "selected_district": None,
        "logged_in": False,
        "username": "",
        "user_id": None,
        "session_id": str(uuid.uuid4()),
        "auth_tab": "login",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

def go(page, place=None, district=None):
    st.session_state.page = page
    st.session_state.selected_place = place
    st.session_state.selected_district = district
    st.rerun()

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*, html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp, body { background: #f0fafa !important; }
#MainMenu, footer, header { visibility: hidden !important; }
div[data-testid="stDecoration"], div[data-testid="stToolbar"] { display: none !important; }
button[data-testid="collapsedControl"],
button[data-testid="baseButton-headerNoPadding"],
[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] button[kind="header"],
.st-emotion-cache-1rs6os, .st-emotion-cache-czk5ss { display:none!important; visibility:hidden!important; pointer-events:none!important; }

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 2px solid #b2dfdb !important;
    min-width: 230px !important; max-width: 230px !important;
}
section[data-testid="stSidebar"] .stButton > button {
    width:100%!important; text-align:left!important; background:transparent!important;
    border:none!important; border-left:3px solid transparent!important;
    border-radius:0 8px 8px 0!important; color:#1a2e2e!important;
    font-size:15px!important; font-weight:500!important;
    padding:11px 18px!important; margin-bottom:2px!important; box-shadow:none!important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background:#e0f2f1!important; border-left-color:#00897b!important; color:#00796b!important;
}
.block-container { padding:0!important; max-width:100%!important; }

/* TOPBAR */
.tg-topbar { display:flex; align-items:center; gap:12px; background:#ffffff; border-bottom:1.5px solid #b2dfdb; padding:13px 28px; box-shadow:0 1px 6px rgba(0,128,128,0.08); }
.tg-brand { font-size:20px; font-weight:700; color:#00796b; flex:1; }
.tg-userbadge { font-size:13px; font-weight:600; color:#00796b; background:#e0f2f1; padding:5px 14px; border-radius:20px; }

/* PAGE WRAPPER */
.tg-page { padding:20px 28px 60px; }

/* SECTION */
.tg-section-title { font-size:16px; font-weight:700; color:#00796b; margin:22px 0 12px; }
.tg-card-img { width:100%; height:130px; object-fit:cover; border-radius:10px 10px 0 0; display:block; }
.tg-card-wrap { background:#fff; border:1px solid #e0f2f1; border-radius:12px; overflow:hidden; box-shadow:0 1px 6px rgba(0,128,128,0.06); margin-bottom:4px; }

/* PLACE CARD — side by side */
.place-card {
    background:#fff; border:1px solid #e0f2f1; border-radius:16px;
    overflow:hidden; margin-bottom:24px;
    box-shadow:0 2px 12px rgba(0,128,128,0.07);
    display:flex; flex-direction:row;
}
.place-card-img-wrap { position:relative; width:42%; min-width:280px; flex-shrink:0; }
.place-card-img-wrap img { width:100%; height:100%; object-fit:cover; display:block; min-height:340px; }
.place-card-details { flex:1; padding:22px 24px; display:flex; flex-direction:column; gap:4px; overflow:hidden; }
.place-card-author { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.place-card-author-name { font-size:14px; font-weight:700; color:#0f766e; }
.place-card-author-sub { font-size:11px; color:#64748b; }
.place-card-title { font-size:22px; font-weight:800; color:#1a2e2e; margin:0 0 4px; }
.place-card-district { font-size:12px; color:#0d9488; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:10px; }
.place-card-caption { font-size:14px; color:#475569; font-style:italic; margin-bottom:10px; padding:10px 14px; background:#f0fdfa; border-radius:8px; border-left:3px solid #14b8a6; }
.info-label { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:#0d9488; margin:0 0 3px; }
.info-text { font-size:13px; color:#334155; line-height:1.65; margin:0 0 10px; }
.rating-badge { display:inline-flex; align-items:center; gap:4px; background:#fef9c3; color:#92400e; font-size:12px; font-weight:700; padding:3px 10px; border-radius:20px; margin-bottom:8px; border:1px solid #fde68a; }
.review-bubble { background:#f0fdfa; padding:10px 14px; border-radius:10px; margin-bottom:8px; border-left:3px solid #14b8a6; }
.review-author { font-size:12px; font-weight:700; color:#0f766e; }
.review-text { font-size:13px; color:#1e293b; margin:2px 0 0; }
.badge-cert { background:#d1fae5; color:#065f46; font-size:10px; font-weight:700; padding:2px 7px; border-radius:10px; margin-left:5px; }
.badge-guest { background:#f1f5f9; color:#64748b; font-size:10px; font-weight:600; padding:2px 7px; border-radius:10px; margin-left:5px; }
.vote-row { display:flex; align-items:center; gap:10px; margin-top:auto; padding-top:10px; border-top:1px solid #e0f2f1; }
.vote-pill { font-size:13px; font-weight:700; padding:5px 14px; border-radius:20px; border:1.5px solid; cursor:pointer; }
.vote-up { color:#0f766e; border-color:#99f6e4; background:#f0fdfa; }
.vote-dn { color:#c62828; border-color:#fecaca; background:#fff5f5; }

/* AUTH PAGE */
.auth-box { max-width:440px; margin:40px auto; background:#fff; border:1px solid #e0f2f1; border-radius:20px; padding:36px 32px; box-shadow:0 4px 24px rgba(0,128,128,0.09); }
.auth-tabs { display:flex; gap:0; border:1.5px solid #b2dfdb; border-radius:12px; overflow:hidden; margin-bottom:28px; }
.auth-tab { flex:1; text-align:center; padding:11px 0; font-size:15px; font-weight:600; cursor:pointer; background:#f0fafa; color:#607d8b; transition:all .15s; }
.auth-tab.active { background:#0d9488; color:#fff; }

/* PROFILE */
.profile-header { display:flex; align-items:center; gap:20px; background:#fff; border:1px solid #e0f2f1; border-radius:16px; padding:24px; margin-bottom:20px; }
.profile-stats { display:flex; gap:28px; margin-top:12px; }
.profile-stat { text-align:center; }
.profile-stat-num { font-size:20px; font-weight:800; color:#0d9488; }
.profile-stat-label { font-size:11px; color:#64748b; font-weight:600; }

/* DISTRICT */
.tg-district-card { background:#fff; border:1px solid #e0f2f1; border-radius:12px; padding:20px 16px; text-align:center; box-shadow:0 1px 6px rgba(0,128,128,0.06); margin-bottom:4px; }

/* BUTTONS */
.stButton > button { border-radius:8px!important; font-size:13px!important; font-weight:600!important; transition:all .15s!important; }
.btn-primary .stButton > button { background:#0d9488!important; color:#fff!important; border:none!important; }
.btn-primary .stButton > button:hover { background:#0f766e!important; }
.btn-back .stButton > button { background:#fff!important; border:1px solid #b2dfdb!important; color:#00796b!important; }
.btn-danger .stButton > button { background:#fff!important; border:1px solid #fca5a5!important; color:#c62828!important; }

/* POST FORM */
.post-section-card { background:#f8fffe; border:1px solid #e0f2f1; border-radius:12px; padding:18px; margin-bottom:16px; }
.post-step-label { font-size:13px; font-weight:700; color:#0d9488; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px; }

/* TITLE BANNER */
.title-banner { background:linear-gradient(135deg,#ccfbf1 0%,#f0fdfa 100%); padding:28px; border-radius:18px; text-align:center; margin-bottom:28px; border:1px solid #99f6e4; }
.title-banner h2 { color:#0f766e!important; font-weight:800; margin:0; font-size:2rem; }

hr { border:none; border-top:1px solid #e0f2f1; margin:18px 0; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;padding:18px 18px 14px;border-bottom:1px solid #e0f2f1;">
        <span style="font-size:22px;">📷</span>
        <span style="font-size:18px;font-weight:700;color:#00796b;">Tourgram</span>
    </div>""", unsafe_allow_html=True)

    if st.session_state.logged_in:
        user = get_user_by_id(st.session_state.user_id)
        av = avatar_html(st.session_state.username, user.get("avatar_url","") if user else "", 36)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:12px 18px;border-bottom:1px solid #e0f2f1;">
            {av}
            <div>
                <div style="font-size:13px;font-weight:700;color:#0f766e;">@{st.session_state.username}</div>
                <div style="font-size:11px;color:#64748b;">✓ Certified</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    if st.button("🏠  Home", key="nav_home"): go("home")
    if st.button("🗺️  Districts", key="nav_dist"): go("district")
    if st.button("📷  Post a Place", key="nav_post"): go("post" if st.session_state.logged_in else "auth")
    if st.session_state.logged_in:
        if st.button("👤  My Profile", key="nav_profile"): go("profile")
        if st.button("🚪  Logout", key="nav_logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_id = None
            go("home")
    else:
        if st.button("👤  Login / Sign Up", key="nav_login"): go("auth")

    st.markdown("<div style='margin-top:40px;padding:0 18px;font-size:12px;color:#90a4ae;'>Discover Nepal's hidden gems 🇳🇵</div>", unsafe_allow_html=True)

# ── TOPBAR ─────────────────────────────────────────────────────────────────────
user_html = f'<span class="tg-userbadge">👤 {st.session_state.username} ✓</span>' if st.session_state.logged_in else ""
st.markdown(f"""
<div class="tg-topbar">
    <div class="tg-brand">📷 Tourgram</div>
    {user_html}
</div>""", unsafe_allow_html=True)

# ── PLACE CARD RENDERER ────────────────────────────────────────────────────────
def render_place_card(place, show_back=False):
    pid = place["id"]
    reviews = get_reviews(pid)
    up, dn = get_vote_counts(pid)
    avg_rating = sum(r["rating"] for r in reviews) / len(reviews) if reviews else 0
    stars_html = "⭐" * int(round(avg_rating))

    uname = place["username"].lstrip("u/")
    user_obj = get_user_by_username(uname)
    av_url = user_obj.get("avatar_url","") if user_obj else ""
    av_html = avatar_html(uname, av_url, 40)

    if show_back:
        st.markdown('<div class="btn-back">', unsafe_allow_html=True)
        if st.button("← Back", key=f"back_{pid}"):
            st.session_state.selected_place = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="place-card">
      <div class="place-card-img-wrap">
        <img src="{place['image']}" alt="{place['title']}">
      </div>
      <div class="place-card-details">
        <div class="place-card-author">
          {av_html}
          <div>
            <div class="place-card-author-name">@{uname}</div>
            <div class="place-card-author-sub">📍 {place['district']}</div>
          </div>
        </div>
        <div class="place-card-title">{place['title']}</div>
        {"<div class='place-card-caption'>" + place['caption'] + "</div>" if place.get('caption') else ""}
        {"<div class='rating-badge'>" + stars_html + f" {avg_rating:.1f} / 5 ({len(reviews)} reviews)</div>" if reviews else ""}
        <div class="info-label">📜 History</div>
        <div class="info-text">{place.get('history','—')}</div>
        <div class="info-label">💰 Budget</div>
        <div class="info-text">{place.get('budget','—')}</div>
        <div class="info-label">🛡️ Safety</div>
        <div class="info-text">{place.get('safety','—')}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Votes (below card, inline)
    user_vote = get_user_vote(pid, st.session_state.user_id, st.session_state.session_id)
    vc1, vc2, vc3 = st.columns([1, 1, 4])
    with vc1:
        up_label = f"▲ {up}" + (" ✓" if user_vote=="up" else "")
        if st.button(up_label, key=f"up_{pid}", help="Upvote"):
            cast_vote(pid, "up", st.session_state.user_id, st.session_state.session_id)
            st.rerun()
    with vc2:
        dn_label = f"▼ {dn}" + (" ✓" if user_vote=="down" else "")
        if st.button(dn_label, key=f"dn_{pid}", help="Downvote"):
            cast_vote(pid, "down", st.session_state.user_id, st.session_state.session_id)
            st.rerun()

    # Reviews
    st.markdown("<div style='margin-top:12px;'><div class='info-label'>⭐ Reviews</div></div>", unsafe_allow_html=True)
    for r in reviews[:4]:
        badge = '<span class="badge-cert">✓ Certified</span>' if r["certified"] else '<span class="badge-guest">Guest</span>'
        st.markdown(f"""
        <div class="review-bubble">
          <span class="review-author">{r['author']}</span>{badge}
          <p class="review-text">{r['text']}</p>
        </div>""", unsafe_allow_html=True)

    # Add review
    if show_back:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form(key=f"review_form_{pid}", clear_on_submit=True):
            col_r1, col_r2 = st.columns([3, 1])
            with col_r1:
                new_text = st.text_input("Write a review", placeholder="Share your experience…", label_visibility="collapsed")
            with col_r2:
                new_rating = st.selectbox("Rating", [5,4,3,2,1], label_visibility="collapsed")
            submitted = st.form_submit_button("Post Review →")
            if submitted:
                if new_text.strip():
                    author = f"@{st.session_state.username}" if st.session_state.logged_in else "Guest123"
                    certified = st.session_state.logged_in
                    insert_review(pid, author, st.session_state.user_id, new_text.strip(), new_rating, 1 if certified else 0)
                    st.success("Review posted!")
                    st.rerun()
                else:
                    st.warning("Please write something first.")
        if not st.session_state.logged_in:
            st.caption("💡 Posting as Guest. Log in to earn the ✓ Certified badge.")


# ── HOME PAGE ──────────────────────────────────────────────────────────────────
def show_home():
    if st.session_state.selected_place:
        place = get_place_by_id(st.session_state.selected_place)
        if place:
            st.markdown('<div class="tg-page">', unsafe_allow_html=True)
            render_place_card(place, show_back=True)
            st.markdown('</div>', unsafe_allow_html=True)
            return

    places = get_all_places()
    by_id = {p["id"]: p for p in places}

    SECTIONS = [
        ("✨ Recommended for You", ["p1","p2","p3"]),
        ("🔥 Popular Right Now", ["p2","p3","p4","p5"]),
        ("📍 Must Visit", ["p3","p4","p5","p6"]),
        ("⭐ Highest Rated", ["p4","p5","p6","p1"]),
    ]

    st.markdown('<div class="tg-page">', unsafe_allow_html=True)
    for sec_title, ids in SECTIONS:
        avail = [by_id[i] for i in ids if i in by_id]
        if not avail: continue
        st.markdown(f'<div class="tg-section-title">{sec_title}</div>', unsafe_allow_html=True)
        cols = st.columns(len(avail))
        for i, post in enumerate(avail):
            uname = post["username"].lstrip("u/")
            user_obj = get_user_by_username(uname)
            av_url = user_obj.get("avatar_url","") if user_obj else ""
            with cols[i]:
                st.markdown(f"""
                <div class="tg-card-wrap">
                  <img class="tg-card-img" src="{post['image']}">
                  <div style="display:flex;align-items:center;gap:7px;padding:8px 10px 2px;">
                    {avatar_html(uname, av_url, 26)}
                    <span style="font-size:12px;font-weight:700;color:#0f766e;">@{uname}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
                if st.button(post["title"], key=f"card_{sec_title[:3]}_{post['id']}"):
                    st.session_state.selected_place = post["id"]
                    st.rerun()
        st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div style="font-size:18px;font-weight:700;color:#1a2e2e;margin:24px 0 18px;padding-bottom:10px;border-bottom:2px solid #b2dfdb;">📸 Community Posts</div>', unsafe_allow_html=True)
    for place in places:
        render_place_card(place)
        if st.button(f"View full details →", key=f"view_{place['id']}"):
            st.session_state.selected_place = place["id"]
            st.rerun()
        st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── AUTH PAGE ──────────────────────────────────────────────────────────────────
def show_auth():
    st.markdown('<div class="tg-page">', unsafe_allow_html=True)
    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("← Back", key="auth_back"): go("home")
    st.markdown('</div>', unsafe_allow_html=True)

    tab = st.session_state.get("auth_tab", "login")

    st.markdown(f"""
    <div class="auth-box">
      <div style="text-align:center;margin-bottom:20px;">
        <span style="font-size:36px;">📷</span>
        <div style="font-size:22px;font-weight:800;color:#0f766e;margin-top:4px;">Tourgram</div>
        <div style="font-size:13px;color:#64748b;">Discover & share Nepal's hidden gems</div>
      </div>
      <div class="auth-tabs">
        <div class="auth-tab {'active' if tab=='login' else ''}">Login</div>
        <div class="auth-tab {'active' if tab=='signup' else ''}">Sign Up</div>
      </div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑  Login", key="tab_login", use_container_width=True):
            st.session_state.auth_tab = "login"
            st.rerun()
    with col2:
        if st.button("✨  Sign Up", key="tab_signup", use_container_width=True):
            st.session_state.auth_tab = "signup"
            st.rerun()

    st.markdown("<div style='max-width:440px;margin:0 auto;'>", unsafe_allow_html=True)

    if tab == "login":
        st.markdown("### 👋 Welcome back")
        uname = st.text_input("Username", placeholder="your_username", key="login_uname")
        pw = st.text_input("Password", type="password", placeholder="••••••••", key="login_pw")
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("Log In →", key="login_submit", use_container_width=True):
            user = get_user_by_username(uname.strip())
            if user and user["password_hash"] == hash_pw(pw):
                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.user_id = user["id"]
                st.success("Welcome back!")
                time.sleep(0.5)
                go("home")
            else:
                st.error("Invalid username or password.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='text-align:center;margin-top:12px;font-size:13px;color:#64748b;'>Don't have an account? Click <b>Sign Up</b> above.</div>", unsafe_allow_html=True)

    else:
        st.markdown("### 🚀 Create your account")
        new_uname = st.text_input("Choose a username", placeholder="e.g. rajan_travels", key="signup_uname")
        new_pw = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_pw")
        new_pw2 = st.text_input("Confirm password", type="password", placeholder="Repeat your password", key="signup_pw2")
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("Create Account →", key="signup_submit", use_container_width=True):
            if not new_uname.strip():
                st.error("Please choose a username.")
            elif len(new_pw) < 6:
                st.error("Password must be at least 6 characters.")
            elif new_pw != new_pw2:
                st.error("Passwords do not match.")
            else:
                uid = create_user(new_uname.strip(), new_pw)
                if uid:
                    st.session_state.logged_in = True
                    st.session_state.username = new_uname.strip()
                    st.session_state.user_id = uid
                    st.success("Account created! Welcome to Tourgram 🎉")
                    time.sleep(0.6)
                    go("home")
                else:
                    st.error("That username is already taken. Try another.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='text-align:center;margin-top:12px;font-size:13px;color:#64748b;'>Already have an account? Click <b>Login</b> above.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── PROFILE PAGE ───────────────────────────────────────────────────────────────
def show_profile():
    if not st.session_state.logged_in:
        go("auth")
        return

    user = get_user_by_id(st.session_state.user_id)
    uname = st.session_state.username
    all_places = get_all_places()
    my_places = [p for p in all_places if p["username"].lstrip("u/") == uname]

    st.markdown('<div class="tg-page">', unsafe_allow_html=True)
    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("← Back", key="profile_back"): go("home")
    st.markdown('</div>', unsafe_allow_html=True)

    av_url = user.get("avatar_url","") if user else ""
    av_html = avatar_html(uname, av_url, 80)

    st.markdown(f"""
    <div class="profile-header">
      {av_html}
      <div>
        <div style="font-size:22px;font-weight:800;color:#0f766e;">@{uname}</div>
        <div style="font-size:13px;color:#475569;margin-top:4px;">{user.get('bio','No bio yet.') if user else ''}</div>
        <div class="profile-stats">
          <div class="profile-stat">
            <div class="profile-stat-num">{len(my_places)}</div>
            <div class="profile-stat-label">Posts</div>
          </div>
          <div class="profile-stat">
            <div class="profile-stat-num">✓</div>
            <div class="profile-stat-label">Certified</div>
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    with st.expander("✏️ Edit Profile", expanded=False):
        new_av = st.text_input("Profile photo URL (paste a link)", value=av_url, placeholder="https://...", key="prof_av")
        new_bio = st.text_area("Bio", value=user.get("bio","") if user else "", placeholder="Tell us about yourself…", key="prof_bio", height=80)
        if new_av.strip():
            st.image(new_av.strip(), width=80, caption="Preview")
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("Save Profile", key="save_profile"):
            update_user_profile(st.session_state.user_id, new_av.strip(), new_bio.strip())
            st.success("Profile updated!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Leave the URL blank to keep your auto-generated avatar.")

    st.markdown(f"<div class='tg-section-title'>📸 My Posts ({len(my_places)})</div>", unsafe_allow_html=True)
    if my_places:
        for place in my_places:
            render_place_card(place)
            st.markdown("<hr>", unsafe_allow_html=True)
    else:
        st.info("You haven't posted any places yet. Use 'Post a Place' to get started!")

    st.markdown('</div>', unsafe_allow_html=True)


# ── POST PAGE ──────────────────────────────────────────────────────────────────
def show_post():
    if not st.session_state.logged_in:
        show_auth()
        return

    st.markdown('<div class="tg-page">', unsafe_allow_html=True)
    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("← Back to Home", key="post_back"): go("home")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="title-banner">
      <h2>📷 Share a Place</h2>
      <div style="color:#0d9488;font-size:14px;margin-top:4px;">Your post will appear in the community feed</div>
    </div>""", unsafe_allow_html=True)

    form_col, preview_col = st.columns([3, 2], gap="large")

    with form_col:
        st.markdown('<div class="post-step-label">① Photo</div>', unsafe_allow_html=True)
        st.markdown('<div class="post-section-card">', unsafe_allow_html=True)
        photo_mode = st.radio("", ["Upload a file","Paste a URL"], horizontal=True, key="post_photo_mode")
        uploaded_file = None
        image_url = ""
        if photo_mode == "Upload a file":
            uploaded_file = st.file_uploader("", type=["jpg","jpeg","png","webp"], key="post_upload")
            if uploaded_file:
                st.image(uploaded_file, use_container_width=True)
                img_bytes = uploaded_file.getvalue()
                b64 = base64.b64encode(img_bytes).decode()
                ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
                mime = "image/jpeg" if ext in ("jpg","jpeg") else f"image/{ext}"
                image_url = f"data:{mime};base64,{b64}"
        else:
            image_url = st.text_input("Image URL", placeholder="https://example.com/photo.jpg", key="post_img_url", label_visibility="collapsed")
            if image_url.strip(): st.image(image_url.strip(), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="post-step-label">② Place Details</div>', unsafe_allow_html=True)
        st.markdown('<div class="post-section-card">', unsafe_allow_html=True)
        title = st.text_input("Place name *", placeholder="e.g. Gosaikunda Lake", key="post_title")
        district = st.text_input("District *", placeholder="e.g. Rasuwa", key="post_district")
        caption = st.text_area("Caption", placeholder="Describe what makes this place special…", key="post_caption", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="post-step-label">③ Traveller Info</div>', unsafe_allow_html=True)
        st.markdown('<div class="post-section-card">', unsafe_allow_html=True)
        history = st.text_area("📜 History & background", placeholder="Tell other travellers the story…", key="post_history", height=80)
        budget = st.text_area("💰 Budget tips", placeholder="Entry fees, transport, accommodation…", key="post_budget", height=80)
        safety = st.text_area("🛡️ Safety info", placeholder="Is it safe? Best season? Any warnings?", key="post_safety", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="post-step-label">④ Your Initial Review</div>', unsafe_allow_html=True)
        st.markdown('<div class="post-section-card">', unsafe_allow_html=True)
        star_map = {"⭐⭐⭐⭐⭐ Excellent (5)":5,"⭐⭐⭐⭐ Great (4)":4,"⭐⭐⭐ Good (3)":3,"⭐⭐ Fair (2)":2,"⭐ Poor (1)":1}
        star_choice = st.selectbox("Rating", list(star_map.keys()), key="post_stars")
        star_value = star_map[star_choice]
        review_text = st.text_area("Your experience", placeholder="Share your personal experience…", key="post_review_text", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

        final_image = image_url.strip() if image_url.strip() else "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Himalaya_annotated.jpg/1280px-Himalaya_annotated.jpg"

        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("Publish Post ✓", key="publish_btn", use_container_width=True):
            errors = []
            if not title.strip(): errors.append("Place name is required.")
            if not district.strip(): errors.append("District is required.")
            if errors:
                for e in errors: st.error(e)
            else:
                new_id = "p" + str(uuid.uuid4())[:8]
                insert_place({
                    "id": new_id,
                    "user_id": st.session_state.user_id,
                    "username": f"u/{st.session_state.username}",
                    "title": title.strip(),
                    "district": district.strip(),
                    "image": final_image,
                    "caption": caption.strip(),
                    "history": history.strip() or "No history provided.",
                    "budget": budget.strip() or "No budget info provided.",
                    "safety": safety.strip() or "No safety info provided.",
                    "stars": star_value,
                })
                if review_text.strip():
                    insert_review(new_id, f"@{st.session_state.username}", st.session_state.user_id,
                                  review_text.strip(), star_value, 1)
                st.success("🎉 Post published!")
                st.balloons()
                time.sleep(0.5)
                go("home")
        st.markdown('</div>', unsafe_allow_html=True)

    with preview_col:
        st.markdown('<div class="post-step-label">Live Preview</div>', unsafe_allow_html=True)
        preview_title = st.session_state.get("post_title","").strip() or "Place Name"
        preview_district = st.session_state.get("post_district","").strip() or "District"
        preview_caption = st.session_state.get("post_caption","").strip()
        user = get_user_by_id(st.session_state.user_id)
        av_url = user.get("avatar_url","") if user else ""
        av_html_str = avatar_html(st.session_state.username, av_url, 38)
        preview_img = final_image if 'final_image' in dir() else "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Himalaya_annotated.jpg/1280px-Himalaya_annotated.jpg"

        st.markdown(f"""
        <div style="background:#fff;border:1px solid #e0f2f1;border-radius:14px;overflow:hidden;box-shadow:0 2px 12px rgba(0,128,128,0.07);">
          <img src="{preview_img}" style="width:100%;height:200px;object-fit:cover;display:block;">
          <div style="padding:14px 16px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
              {av_html_str}
              <div>
                <div style="font-size:13px;font-weight:700;color:#0f766e;">@{st.session_state.username}</div>
                <div style="font-size:11px;color:#64748b;">📍 {preview_district}</div>
              </div>
            </div>
            <div style="font-size:16px;font-weight:800;color:#1a2e2e;">{preview_title}</div>
            {"<div style='font-size:13px;color:#475569;font-style:italic;margin-top:6px;'>" + preview_caption + "</div>" if preview_caption else ""}
            <div style="font-size:12px;color:#94a3b8;margin-top:10px;">Fill in the form to update preview →</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ── DISTRICT PAGE ──────────────────────────────────────────────────────────────
def show_district():
    places = get_all_places()
    EMOJIS = {"Kaski":"🏔️","Kathmandu":"🕌","Chitwan":"🦏","Mugu":"🌊"}
    districts = sorted(set(p["district"] for p in places))

    if st.session_state.selected_district:
        d = st.session_state.selected_district
        dist_places = [p for p in places if p["district"] == d]
        st.markdown('<div class="tg-page">', unsafe_allow_html=True)
        st.markdown('<div class="btn-back">', unsafe_allow_html=True)
        if st.button("← Back to Districts", key="dist_inner_back"):
            st.session_state.selected_district = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="title-banner">
          <h2>{EMOJIS.get(d,'📍')} {d}</h2>
          <div style="color:#0d9488;font-size:14px;">{len(dist_places)} place{'s' if len(dist_places)!=1 else ''} found</div>
        </div>""", unsafe_allow_html=True)
        for place in dist_places:
            render_place_card(place)
            if st.button(f"View details →", key=f"dist_view_{place['id']}"):
                st.session_state.selected_place = place["id"]
                go("home")
            st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="tg-page">', unsafe_allow_html=True)
    st.markdown('<div class="btn-back">', unsafe_allow_html=True)
    if st.button("← Back", key="dist_back"): go("home")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#00796b;margin-top:0;">🗺️ Districts</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#607d8b;font-size:14px;margin-bottom:20px;">Browse tourist spots by district.</p>', unsafe_allow_html=True)

    cols = st.columns(4)
    for i, d in enumerate(districts):
        count = sum(1 for p in places if p["district"] == d)
        with cols[i % 4]:
            st.markdown(f"""
            <div class="tg-district-card">
              <div style="font-size:36px;">{EMOJIS.get(d,'📍')}</div>
              <div style="font-size:15px;font-weight:700;color:#00796b;margin-top:8px;">{d}</div>
              <div style="font-size:12px;color:#607d8b;margin-top:4px;">{count} place{'s' if count!=1 else ''}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Explore {d} →", key=f"btn_explore_{d}"):
                st.session_state.selected_district = d
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ── ROUTER ─────────────────────────────────────────────────────────────────────
page = st.session_state.page
if page == "home":      show_home()
elif page == "auth":    show_auth()
elif page == "post":    show_post()
elif page == "district": show_district()
elif page == "profile": show_profile()
