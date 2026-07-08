import streamlit as st
import pandas as pd
import pickle


# -------------------------
# Load Data (cached small files only)
# -------------------------
@st.cache_data
def load_small():
    with open("product_features.pkl", "rb") as f:
        product_features = pickle.load(f)

    with open("cluster_product_scores.pkl", "rb") as f:
        cluster_product_scores = pickle.load(f)

    return product_features, cluster_product_scores



def load_users():
    with open("user_features.pkl", "rb") as f:
        user_features = pickle.load(f)

    return user_features


product_features, cluster_product_scores = load_small()
user_features = load_users()

# -------------------------
# UI Setup
# -------------------------
st.set_page_config(
    page_title="Recommendation System",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Recommendation System Dashboard")
   

st.info(
    "Select a recommendation type from the sidebar and enter a User ID or Product ID to get recommendations."
)
# -------------------------
# Sidebar Navigation
# -------------------------
option = st.sidebar.radio(
    "Choose Recommendation Type",
    ["User-Based Recommendation", "Product-Based Recommendation"]
)

# -------------------------
# Sidebar Info Panel
# -------------------------
st.sidebar.title("ℹ️ How it works")

st.sidebar.markdown("""
### 👤 User-Based Recommendation
- Finds user's cluster
- Recommends popular products from same cluster
- Ranked by popularity & rating

---

### 📦 Product-Based Recommendation
- Finds product's cluster
- Recommends similar products in same cluster
- Ranked by rating & popularity

---

### 🧠 Model Used
- K-Means Clustering
- Cluster-based ranking system

---

### ⚡ Optimization
- No heavy dataset loading
- No runtime filtering of millions of rows
- Fully memory safe
""")

# =========================================================
# USER-BASED FUNCTION (CLEAN)
# =========================================================
def recommend_products_user(user_id, top_n=10):

    user_cluster = user_features.loc[
        user_features['userId'] == user_id,
        'cluster'
    ].values[0]

    recs = cluster_product_scores[
        cluster_product_scores['cluster'] == user_cluster
    ]

    recs = recs.sort_values(
        ['count', 'avg_rating'],
        ascending=False
    ).head(top_n)

    recs = recs.rename(columns={
        "productId": "Product ID",
        "cluster": "Cluster",
        "avg_rating": "Average Rating",
        "count": "Total Count"
    })

    return recs[
        ["Product ID", "Cluster", "Average Rating", "Total Count"]
    ]

# =========================================================
# PRODUCT-BASED FUNCTION (UNCHANGED)
# =========================================================
def recommend_similar_products(product_id, top_n=10):

    cluster = product_features.loc[
        product_features['productId'] == product_id,
        'cluster'
    ].values[0]

    recs = product_features[
        (product_features['cluster'] == cluster) &
        (product_features['productId'] != product_id)
    ]

    recs = recs.sort_values(
        ['avg_rating', 'rating_count'],
        ascending=False
    ).head(top_n)

    recs['avg_rating'] = recs['avg_rating'].round(1)

    recs = recs.rename(columns={
        "productId": "Product ID",
        "cluster": "Cluster",
        "avg_rating": "Average Rating",
        "rating_count": "Total Count"
    })

    return recs[
        ["Product ID", "Cluster", "Average Rating", "Total Count"]
    ]

# =========================================================
# USER-BASED UI
# =========================================================
if option == "User-Based Recommendation":

    st.subheader("👤 User-Based Recommendation System")

    user_id = st.text_input("Enter User ID")

    top_n = st.slider("Number of Recommendations", 5, 20, 10)

    # Metrics
    col1, col2, col3 = st.columns(3)

    col1.metric("Users", f"{len(user_features):,}")
    col2.metric("Clusters", user_features["cluster"].nunique())

    if user_id and user_id in user_features["userId"].values:
        cluster = user_features.loc[
            user_features["userId"] == user_id,
            "cluster"
        ].values[0]

        col3.metric("Selected Cluster", cluster)
    else:
        col3.metric("Selected Cluster", "-")

    # Sidebar dynamic info
    if user_id and user_id in user_features['userId'].values:

       selected_user = user_features[user_features['userId'] == user_id].iloc[0]

       st.sidebar.markdown("### 👤 Current Selection")

       st.sidebar.success(f"User ID: {user_id}")
       st.sidebar.info(f"Cluster: {selected_user['cluster']}")

       st.sidebar.write(f"⭐ Average Rating: {selected_user['avg_rating']:.1f}")

       st.sidebar.write(f"📝 Ratings Given: {int(selected_user['rating_count'])}")

    # Recommendation button
    if st.button("Get Recommendations"):

        if not user_id:
            st.warning("Please enter a User ID")

        elif user_id not in user_features['userId'].values:
            st.error("User ID not found")

        else:

            cluster = user_features.loc[
                user_features['userId'] == user_id,
                'cluster'
            ].values[0]

            st.success(f"User belongs to Cluster {cluster}")

            recs = recommend_products_user(user_id, top_n)

            st.dataframe(
                recs.reset_index(drop=True),
                use_container_width=True
            )

# =========================================================
# PRODUCT-BASED UI
# =========================================================
if option == "Product-Based Recommendation":

    st.subheader("📦 Product-Based Recommendation System")

    product_id = st.text_input("Enter Product ID")

    top_n = st.slider("Number of Recommendations", 5, 20, 10)

    # Metrics
    col1, col2, col3 = st.columns(3)

    col1.metric("Products", f"{len(product_features):,}")
    col2.metric("Clusters", product_features["cluster"].nunique())

    if product_id and product_id in product_features["productId"].values:

        cluster = product_features.loc[
            product_features["productId"] == product_id,
            "cluster"
        ].values[0]

        col3.metric("Selected Cluster", cluster)

    else:
        col3.metric("Selected Cluster", "-")

    # Sidebar dynamic info
    if product_id and product_id in product_features['productId'].values:

       selected_product = product_features[product_features['productId'] == product_id].iloc[0]

       st.sidebar.markdown("### 📦 Current Selection")

       st.sidebar.success(f"Product ID: {product_id}")
       st.sidebar.info(f"Cluster: {selected_product['cluster']}")

       st.sidebar.write(f"⭐ Average Rating: {selected_product['avg_rating']:.1f}")

       st.sidebar.write(f"📝 Total Ratings: {int(selected_product['rating_count'])}")

    # Recommendation button
    if st.button("Get Similar Products"):

        if not product_id:
            st.warning("Please enter a Product ID")

        elif product_id not in product_features['productId'].values:
            st.error("Product ID not found")

        else:

            cluster = product_features.loc[
                product_features['productId'] == product_id,
                'cluster'
            ].values[0]

            st.success(f"Product belongs to Cluster {cluster}")

            recs = recommend_similar_products(product_id, top_n)

            st.dataframe(
                recs.reset_index(drop=True),
                use_container_width=True
            )