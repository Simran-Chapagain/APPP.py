import streamlit as st

# Set page config for a clean layout
st.set_page_config(page_title="Customer Reviews & Safety Tracker", page_icon="⭐", layout="centered")

# Initialize an in-memory session state to hold reviews so they persist while the app is open
if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {"username": "Alice", "rating": 5, "comment": "Amazing place, felt incredibly secure!", "safety_vote": True},
        {"username": "Bob", "rating": 3, "comment": "Good food, but lighting outside was poor.", "safety_vote": False},
        {"username": "Charlie", "rating": 4, "comment": "Friendly staff and clean environment.", "safety_vote": True},
    ]

# Title
st.title("⭐ Customer Reviews & Safety Portal")
st.markdown("---")

# 1. METRICS DISPLAY
total_reviews = len(st.session_state.reviews)
if total_reviews > 0:
    safe_votes = sum(1 for r in st.session_state.reviews if r["safety_vote"])
    safety_pct = round((safe_votes / total_reviews) * 100)
else:
    safety_pct = 0

# Display Metrics side-by-side
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Overall Safety Score", value=f"{safety_pct}%")
with col2:
    st.metric(label="Total Reviews", value=total_reviews)

st.markdown("---")

# 2. SUBMIT A NEW REVIEW FORM
st.subheader("✍️ Leave a Review")

with st.form(key="review_form", clear_on_submit=True):
    username = st.text_input("Your Name", placeholder="John Doe")
    rating = st.slider("Rating (1-5 Stars)", min_value=1, max_value=5, value=5)
    safety_input = st.radio("Did you feel safe at this location?", options=["Yes", "No"], index=0)
    comment = st.text_area("Your Review Comments", placeholder="Tell us about your experience...")
    
    submit_button = st.form_submit_button(label="Submit Review")

# Handle Form Submission
if submit_button:
    if username.strip() == "" or comment.strip() == "":
        st.error("Please fill out both your name and comment.")
    else:
        new_review = {
            "username": username,
            "rating": int(rating),
            "comment": comment,
            "safety_vote": True if safety_input == "Yes" else False
        }
        # Add to session state list
        st.session_state.reviews.append(new_review)
        st.success("Review submitted successfully!")
        st.rerun() # Refresh app to update sorting and metrics

st.markdown("---")

# 3. DISPLAY REVIEWS (Sorted by Rating Descending)
st.subheader("📋 User Reviews (Highest Rating First)")

# Sort dynamically
sorted_reviews = sorted(st.session_state.reviews, key=lambda x: x["rating"], reverse=True)

for r in sorted_reviews:
    # Visual card separation using streamlit containers
    with st.container(border=True):
        stars = "⭐" * r["rating"]
        st.markdown(f"**{r['username']}** &nbsp;&nbsp;|&nbsp;&nbsp; <span style='color:#f1c40f'>{stars}</span>", unsafe_allow_html=True)
        st.write(r["comment"])
        
        # Safety indicator tag
        if r["safety_vote"]:
            st.markdown("🟢 *Felt Safe*")
        else:
            st.markdown("🔴 *Felt Unsafe*")