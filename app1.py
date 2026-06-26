import streamlit as st

st.title("📸 Tourgram Nepal")
st.write("Welcome to the community-driven tourism portal.")

# Dropdown selection for places
place = st.selectbox("Explore a destination:", ["Kathmandu Heritage", "Pokhara Lakes", "Ghandruk Homestay"])

st.subheader(f"What travelers say about {place}")

# Text input for review
review_text = st.text_area("Write your honest review or safety update:")

# Photo uploader
uploaded_img = st.file_uploader("Upload a live photo:", type=["jpg", "png", "jpeg"])

# Booking Shortcut
if st.button("Submit Review & Photo"):
    if review_text:
        st.success("Thank you for helping fellow travelers stay safe!")
        st.write(f"📝 {review_text}")
    if uploaded_img:
        st.image(uploaded_img, caption="User Uploaded View")

st.markdown("---")
if st.button(f"🔗 Request Booking for {place}"):
    st.info("Booking request form opened! (Simulated backend contact logic)")
    name = st.text_input("Your Name:")
    phone = st.text_input("Your Phone Number:")
    if st.button("Confirm Request"):
        st.success("Host notified successfully!")
