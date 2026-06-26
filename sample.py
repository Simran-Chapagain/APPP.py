import streamlit as st
from PIL import Image

# ==========================================
# 1. PAGE CONFIGURATION & TEAL THEME
# ==========================================
st.set_page_config(
    page_title="Tourgram Nepal",
    page_icon="📸",
    layout="wide"
)

# Custom Styling to match your teal logo and create Instagram-style post boxes
st.markdown("""
    <style>
    .teal-title { color: #40B5AD; font-size: 42px; font-weight: bold; margin-bottom: 0px; }
    .signal-box { background-color: #E0F7FA; padding: 12px; border-radius: 10px; border-left: 5px solid #40B5AD; margin-bottom: 25px; }
    .instagram-post { background-color: #FFFFFF; border: 1px solid #E1E8ED; border-radius: 12px; padding: 20px; margin-bottom: 30px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05); }
    .post-header { font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #2C3E50; }
    .like-counter { font-size: 16px; font-weight: bold; color: #E0245E; margin-left: 8px; vertical-align: middle; }
    .certified-badge { color: #40B5AD; font-weight: bold; font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INITIALIZE GLOBAL DATA (Likes & Reviews)
# ==========================================
if "likes" not in st.session_state:
    st.session_state.likes = {"Pokhara": 142, "Kathmandu": 89, "Chitwan": 64}

if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {"place": "Pokhara", "user": "Anjali Sharma ✅ Certified", "type": "Certified", "rating": 5, "comment": "Absolutely magical! The boat ride on Phewa Lake during sunset is a must-do."},
        {"place": "Pokhara", "user": "Rohan Das", "type": "Normal", "rating": 4, "comment": "Great views, but it gets a bit crowded near Lakeside in the evening."},
        {"place": "Kathmandu", "user": "Suresh Kumar ✅ Certified", "type": "Certified", "rating": 5, "comment": "The ancient architecture here is visually unparalleled."},
        {"place": "Chitwan", "user": "Dr. Rita Thapa ✅ Certified", "type": "Certified", "rating": 5, "comment": "Incredible jungle safari! Spotted two rhinos close up."},
    ]

# ==========================================
# 3. SLIDE-OUT DASHBOARD (Sidebar Navigation)
# ==========================================
st.sidebar.markdown("<h2 style='color: #40B5AD;'>📊 Dashboard</h2>", unsafe_allow_html=True)

# Search Engine in Sidebar
search_query = st.sidebar.text_input("🔍 Search Destinations...", placeholder="e.g., Pokhara").strip().lower()

# Explore Filters
st.sidebar.markdown("### 🗺️ Explore Based On:")
explore_budget = st.sidebar.selectbox("Budget Level", ["All Budgets", "Budget Friendly", "Mid-Range", "Luxury"])
explore_review = st.sidebar.selectbox("Review Rating", ["All Ratings", "4.5+ Stars"])
explore_transport = st.sidebar.selectbox("Transportation Availability", ["All Available", "Flight Connected", "Bus / Offroad"])

# ==========================================
# 4. SITE HEADER (Google-style Logo Alignment)
# ==========================================
head_col1, head_col2 = st.columns([1, 8])
with head_col1:
    try:
        logo_img = Image.open("logo.png")
        st.image(logo_img, width=75)
    except:
        st.markdown("<h1 style='font-size: 55px; margin: 0;'>🏔️</h1>", unsafe_allow_html=True)

with head_col2:
    st.markdown("<p class='teal-title'>Tourgram</p>", unsafe_allow_html=True)
    st.write("Your Instagram-style Community Travel Guide")

# Dashboard Signal Bar
st.markdown("""
    <div class='signal-box'>
        <strong>📡 Live Feed Signal:</strong> 🟢 Connected | 🌤️ Clear Skies Across Main Trails | 🗺️ Filtering active via Sidebar Dashboard
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 5. DESTINATION RAW DATA FEED
# ==========================================
feed_items = [
    {
        "name": "Pokhara",
        "author": "u/nepal_wanderer",
        "image": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=800&q=80",
        "caption": "Waking up to the beautiful Annapurna mountain range reflecting perfectly off Phewa Lake this morning! 🏔️✨",
        "history": "Historically a crucial trade route node between India and Tibet, Pokhara grew in the late 20th century into Nepal's ultimate adventure tourism gateway destination.",
        "women_safety": "98%",
        "animal_safety": "92%",
        "budget": "Mid-Range",
        "transport": "Flight Connected",
        "rating": 4.8
    },
    {
        "name": "Kathmandu",
        "author": "u/history_buff",
        "image": "https://images.unsplash.com/photo-1541544602621-e0e6488d5119?auto=format&fit=crop&w=800&q=80",
        "caption": "Standing in the middle of ancient heritage architecture. The woodwork detail at Durbar Square is pure art. 🏛️",
        "history": "The ancient seat of the Malla and Shah dynasties, this UNESCO World Heritage public square preserves Newari design and architecture from as early as the 12th century.",
        "women_safety": "94%",
        "animal_safety": "85% (Urban street monkeys present)",
        "budget": "Budget Friendly",
        "transport": "Flight Connected",
        "rating": 4.6
    },
    {
        "name": "Chitwan",
        "author": "u/safari_sam",
        "image": "https://images.unsplash.com/photo-1581888227599-779811939961?auto=format&fit=crop&w=800&q=80",
        "caption": "An early morning canoe ride down the Rapti River. Spotting rare wildlife out here hits different! 🦏🐆",
        "history": "Established in 1973 as Nepal's very first national park, it serves as a global success benchmark for saving the endangered One-horned Rhinoceros and Bengal Tiger.",
        "women_safety": "95%",
        "animal_safety": "60% (Wild safari rules strictly apply)",
        "budget": "Luxury",
        "transport": "Bus / Offroad",
        "rating": 4.4
    }
]

# ==========================================
# 6. INSTAGRAM FILTER LOGIC
# ==========================================
filtered_feed = []
for item in feed_items:
    # Text Search Filter
    if search_query and search_query not in item["name"].lower() and search_query not in item["caption"].lower():
        continue
    # Budget Filter
    if explore_budget != "All Budgets" and item["budget"] != explore_budget:
        continue
    # Transportation Filter
    if explore_transport != "All Available" and item["transport"] != explore_transport:
        continue
    # Rating Filter
    if explore_review == "4.5+ Stars" and item["rating"] < 4.5:
        continue
        
    filtered_feed.append(item)

# ==========================================
# 7. THE SINGLE VERTICAL INSTAGRAM STREAM
# ==========================================
if not filtered_feed:
    st.info("No Tourgram posts match your current dashboard filter criteria. Try adjusting your sidebar settings!")
else:
    # Center the Instagram feed layout columns
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        for index, item in enumerate(filtered_feed):
            place_name = item["name"]
            
            # Start of HTML Post Frame
            st.markdown(f"""
                <div class="instagram-post">
                    <div class="post-header">👤 {item['author']} • <span style="color: #40B5AD;">📍 {place_name}</span></div>
                </div>
            """, unsafe_allow_html=True)
            
            # 1. Main Media Photo
            st.image(item["image"], use_container_width=True)
            
            # 2. Instagram Like Layout Row
            like_col1, like_col2 = st.columns([1, 4])
            with like_col1:
                # Unique key identifier for every specific like button
                if st.button(f"❤️ Like", key=f"like_btn_{place_name}_{index}"):
                    st.session_state.likes[place_name] += 1
                    st.rerun()
            with like_col2:
                st.markdown(f"<p class='like-counter'>{st.session_state.likes[place_name]} likes</p>", unsafe_allow_html=True)
            
            # 3. User Caption Description
            st.markdown(f"**{item['author']}** {item['caption']}")
            st.write("")
            
            # 4. THE EXPANDEABLE HUBS (History, Safety, Reviews all packed inside!)
            with st.expander(f"👇 View Hub Details, Safety Indices & Reviews for {place_name}"):
                
                # Split layout inside the expander
                exp_col1, exp_col2 = st.columns(2)
                with exp_col1:
                    st.subheader("📖 History & Culture")
                    st.write(item["history"])
                with exp_col2:
                    st.subheader("🛡️ Safety Scorecards")
                    st.metric("👩‍🦰 Female Solo Traveler Safety", item["women_safety"])
                    st.metric("🐾 Animal / Environment Safety", item["animal_safety"])
                
                st.write("---")
                
                # Render Community Reviews inside Expander
                st.subheader("💬 Community Reviews")
                place_reviews = [r for r in st.session_state.reviews if r["place"] == place_name]
                
                # Sort: Certified users stay on top, normal users below
                sorted_reviews = sorted(place_reviews, key=lambda x: x["type"] == "Normal")
                
                for rev in sorted_reviews:
                    if rev["type"] == "Certified":
                        st.markdown(f"🏅 **{rev['user']}** | ⭐ {rev['rating']}/5")
                        st.markdown(f"<i style='color: #00796B;'>'{rev['comment']}'</i>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"👤 **{rev['user']}** | ⭐ {rev['rating']}/5")
                        st.write(f"'{rev['comment']}'")
                    st.write("")
                
                st.write("---")
                
                # User Review Form Submission
                st.markdown("##### ✍️ Share Your Feedback")
                with st.form(key=f"form_{place_name}_{index}", clear_on_submit=True):
                    rev_name = st.text_input("Your Name:", key=f"name_{place_name}_{index}")
                    rev_rating = st.slider("Rating:", 1, 5, 5, key=f"rate_{place_name}_{index}")
                    rev_comment = st.text_area("Your Experience Comments:", key=f"comm_{place_name}_{index}")
                    
                    submit_review = st.form_submit_button("Submit Review")
                    if submit_review and rev_name and rev_comment:
                        st.session_state.reviews.append({
                            "place": place_name,
                            "user": rev_name,
                            "type": "Normal",
                            "rating": rev_rating,
                            "comment": rev_comment
                        })
                        st.success("✨ Experience posted successfully! Close and reopen this expander box to view your post.")
                        st.rerun()

            # Space separator between feed posts
            st.markdown("<br><br>", unsafe_allow_html=True)