import streamlit as st
from collections import Counter


# Product Catalog 
PRODUCTS = [
    {"id": 1, "name": "milk", "category": "dairy", "image": "https://i.imgur.com/6jQCJef.jpeg"},
    {"id": 2, "name": "bread", "category": "bakery", "image": "https://i.imgur.com/ecXRhkz.jpeg"},
    {"id": 3, "name": "butter", "category": "dairy", "image": "https://i.imgur.com/bBzPCY6.jpeg"},
    {"id": 4, "name": "eggs", "category": "dairy", "image": "https://i.imgur.com/7cWhxhq.jpeg"},
    {"id": 5, "name": "cheese", "category": "dairy", "image": "https://i.imgur.com/KpALgKq.jpeg"},
    {"id": 6, "name": "yogurt", "category": "dairy", "image": "https://i.imgur.com/QjYr6tP.jpeg"},
    {"id": 7, "name": "apple", "category": "produce", "image": "https://i.imgur.com/SFHPYCf.jpeg"},
    {"id": 8, "name": "banana", "category": "produce", "image": "https://i.imgur.com/De37SbX.jpeg"},
    {"id": 9, "name": "orange", "category": "produce", "image": "https://i.imgur.com/cpgPKqU.jpeg"},
    {"id": 10, "name": "grape", "category": "produce", "image": "https://i.imgur.com/NSK1kqs.jpeg"},
    {"id": 11, "name": "tomato", "category": "produce", "image": "https://i.imgur.com/dp5xOnr.jpeg"},
    {"id": 12, "name": "potato", "category": "produce", "image": "https://i.imgur.com/kvY3jsY.jpeg"},
    {"id": 13, "name": "onion", "category": "produce", "image": "https://i.imgur.com/xGw7Cel.jpeg"},
    {"id": 14, "name": "garlic", "category": "produce", "image": "https://i.imgur.com/9E68qUB.jpeg"},
    {"id": 15, "name": "pepper", "category": "produce", "image": "https://i.imgur.com/5T0hJqP.jpeg"},
    {"id": 16, "name": "chicken", "category": "meat", "image": "https://i.imgur.com/G3IN1QH.jpeg"},
    {"id": 17, "name": "beef", "category": "meat", "image": "https://i.imgur.com/tuKqSuK.jpeg"},
    {"id": 18, "name": "pork", "category": "meat", "image": "https://i.imgur.com/wf6Wc0U.jpeg"},
    {"id": 19, "name": "rice", "category": "grains", "image": "https://i.imgur.com/taniRDT.jpeg"},
    {"id": 20, "name": "pasta", "category": "grains", "image": "https://i.imgur.com/gNa2SQ5.jpeg"},
    {"id": 21, "name": "noodles", "category": "grains", "image": "https://i.imgur.com/IqpykrK.jpeg"},
    {"id": 22, "name": "coffee", "category": "beverages", "image": "https://i.imgur.com/YWbqEPc.jpeg"},
    {"id": 23, "name": "tea", "category": "beverages", "image": "https://i.imgur.com/Ew5dak7.jpeg"},
    {"id": 24, "name": "juice", "category": "beverages", "image": "https://i.imgur.com/NkO7hb5.jpeg"},
    {"id": 25, "name": "soda", "category": "beverages", "image": "https://i.imgur.com/eRLJhPZ.jpeg"},
    {"id": 26, "name": "water", "category": "beverages", "image": "https://i.imgur.com/QGC4ez7.jpeg"},
    {"id": 27, "name": "jam", "category": "condiments", "image": "https://i.imgur.com/eiOqRgv.jpeg"},
    {"id": 28, "name": "honey", "category": "condiments", "image": "https://i.imgur.com/bBKYMux.jpeg"},
    {"id": 29, "name": "sauce", "category": "condiments", "image": "https://i.imgur.com/rJGx0Yb.jpeg"},
    {"id": 30, "name": "vegetables", "category": "produce", "image": "https://i.imgur.com/XiiHDlJ.jpeg"},
]


def render_page():
    st.title("🛍️ Shopping")
    st.markdown("Browse our products and add items to your cart to create a transaction.")

    # Category filter
    categories = ["All"] + sorted({p["category"] for p in PRODUCTS})
    selected_category = st.selectbox("Filter by Category:", categories)

    # Filter products
    filtered_products = PRODUCTS if selected_category == "All" else [p for p in PRODUCTS if p["category"] == selected_category]

    st.markdown("---")
    st.markdown("### Available Products")

    # Display products in a grid (3 columns)
    cols_per_row = 3
    for i in range(0, len(filtered_products), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(filtered_products):
                product = filtered_products[i + j]
                with col:
                    st.markdown(f"""
                    <div class="product-card">
                        <img src="{product['image']}" alt="{product['name']}">
                        <div class="category">{product['category']}</div>
                        <h4>{product['name']}</h4>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("Add to Cart", key=f"add_{product['id']}", use_container_width=True):
                        st.session_state.current_cart.append(product['name'])
                        st.rerun()

    st.markdown("---")

    # Shopping Cart Section
    st.markdown("### 🛒 Your Cart")

    if len(st.session_state.current_cart) == 0:
        st.info("Your cart is empty. Add some products to get started!")
    else:
        # Count items in cart
        cart_counter = Counter(st.session_state.current_cart)

        # Display cart items with counts
        for item, count in cart_counter.items():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""
                <div class="cart-item">
                    <strong>{item}</strong>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="cart-item">
                    Qty: {count}
                </div>
                """, unsafe_allow_html=True)
            with col3:
                if st.button("Remove", key=f"remove_{item}", use_container_width=True):
                    # Remove one instance of the item
                    st.session_state.current_cart.remove(item)
                    st.rerun()

        st.markdown("---")

        # Cart actions
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.metric("Total Items", len(st.session_state.current_cart))

        with col2:
            if st.button("Clear Cart", use_container_width=True, type="secondary"):
                st.session_state.current_cart = []
                st.rerun()

        with col3:
            if st.button("Complete Transaction", use_container_width=True, type="primary"):
                # Create transaction
                transaction = {
                    'transaction_id': st.session_state.transaction_counter,
                    'items': st.session_state.current_cart.copy()
                }
                st.session_state.transactions.append(transaction)
                st.session_state.transaction_counter += 1
                st.session_state.current_cart = []
                st.success(f"Transaction #{transaction['transaction_id']} completed successfully!")
                st.rerun()

    # Show recent transactions
    if len(st.session_state.transactions) > 0:
        st.markdown("---")
        st.markdown("### Recent Transactions")

        # Show last 5 transactions
        recent = st.session_state.transactions[-5:][::-1]  # Last 5, reversed

        for txn in recent:
            with st.expander(f"Transaction #{txn['transaction_id']} - {len(txn['items'])} items"):
                item_counter = Counter(txn['items'])

                for item, count in item_counter.items():
                    st.write(f"- {item} (x{count})")
