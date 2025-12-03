import streamlit as st
import random

st.set_page_config(page_title="Dummy E-commerce", layout="centered")

# Simulated user login
USER_CREDENTIALS = {"user@example.com": "password123"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "cart" not in st.session_state:
    st.session_state.cart = []

st.title("🛒 Dummy E-commerce Site")

# Login page
if not st.session_state.logged_in:
    st.subheader("Login")
    email = st.text_input("Email",placeholder="Enter email")
    password = st.text_input("Password", type="password", placeholder="Enter password"))
    if st.button("Login"):
        if USER_CREDENTIALS.get(email) == password:
            st.session_state.logged_in = True
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")
else:
    st.success("Welcome back!")

    # Search bar
    st.subheader("Search Products")
    query = st.text_input("Search", placeholder="Type product name...")

    if st.button("Search"):
        st.session_state.results = [
            f"{query.title()} Model {i}" for i in range(1, 6)
        ]
    
    if "results" in st.session_state:
        st.subheader("Search Results")
        for product in st.session_state.results:
            if st.button(product):
                st.session_state.selected_product = product

    # Product details
    if "selected_product" in st.session_state:
        st.subheader("Product Details")
        st.write(f"### {st.session_state.selected_product}")
        if st.button("Add to Cart"):
            st.session_state.cart.append(st.session_state.selected_product)
            st.success("✅ Added to cart!")

    # Cart preview
    if st.session_state.cart:
        st.sidebar.header("🛍️ Cart")
        for item in st.session_state.cart:
            st.sidebar.write(item)
