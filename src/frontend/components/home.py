import streamlit as st

def render_page():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛒 GrocerIQ</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Turning shopping carts into knowledge
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Introduction
    st.markdown("## Welcome!")
    st.markdown("""
    This application helps you create, manage, and analyze supermarket shopping transactions.
    Whether you want to manually create transactions or import existing data, our system
    provides a user-friendly interface for all your needs.
    """)

    # Features Section
    st.markdown("## ✨ Key Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🛍️ Manual Shopping</h3>
            <p>Create transactions by selecting from a variety of products in an intuitive shopping interface.</p>
            <ul>
                <li>Browse 30 common products</li>
                <li>Add items to your cart</li>
                <li>Category filtering</li>
                <li>View purchase history</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h3>📁 CSV Import</h3>
            <p>Import transaction data from CSV files for bulk processing.</p>
            <ul>
                <li>Upload custom CSV files</li>
                <li>Load sample dataset (100 transactions)</li>
                <li>Automatic data parsing</li>
                <li>Format validation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h3>🔧 Data Preprocessing</h3>
            <p>Clean and standardize your data for accurate analysis.</p>
            <ul>
                <li>Remove duplicates & invalid items</li>
                <li>Standardize product names</li>
                <li>Filter empty/single-item transactions</li>
                <li>Before/after comparison view</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🔍 Association Rules Mining</h3>
            <p>Discover shopping patterns using advanced data mining algorithms.</p>
            <ul>
                <li>Apriori & Eclat algorithms</li>
                <li>Performance comparison metrics</li>
                <li>Interactive product recommendations</li>
                <li>Business insights & suggestions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Product Recommendations</h3>
            <p>Get intelligent product suggestions based on association rules.</p>
            <ul>
                <li>Visual confidence indicators</li>
                <li>Strength-based rankings</li>
                <li>Bundle suggestions</li>
                <li>Store layout recommendations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h3>📊 Data Visualization</h3>
            <p>View and analyze your transaction data with comprehensive statistics.</p>
            <ul>
                <li>Transaction summaries</li>
                <li>Item frequency analysis</li>
                <li>Interactive filtering & search</li>
                <li>Multiple export formats</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Workflow Section
    st.markdown("## 📋 Complete Data Mining Workflow")

    st.markdown("""
    <div class="workflow-step">
        <strong>Step 1: Create or Import Transactions</strong><br>
        Go to the <strong>Shopping</strong> page to manually create transactions with our 30-product catalog,
        or use the <strong>Data Import</strong> page to load existing data (custom CSV or 100-transaction sample dataset).
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="workflow-step">
        <strong>Step 2: View & Explore Your Data</strong><br>
        Visit the <strong>View Transactions</strong> page to review all transactions,
        analyze item frequencies, filter by source, and export data in multiple formats.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="workflow-step">
        <strong>Step 3: Clean & Preprocess</strong><br>
        Use the <strong>Data Preprocessing</strong> page to standardize product names, remove duplicates,
        filter invalid items, and prepare clean data for mining with before/after comparison.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="workflow-step">
        <strong>Step 4: Mine Association Rules</strong><br>
        Head to <strong>Association Rules Mining</strong> to discover shopping patterns using Apriori & Eclat algorithms.
        Compare performance metrics and get actionable business insights.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="workflow-step">
        <strong>Step 5: Get Product Recommendations</strong><br>
        Query any product to see what customers frequently buy together, visualize confidence levels,
        and receive bundle suggestions and store layout recommendations.
    </div>
    """, unsafe_allow_html=True)

    # Current Status
    st.markdown("## 📈 Current Status")

    col1, col2, col3 = st.columns(3)

    total_transactions = len(st.session_state.transactions) + len(st.session_state.imported_transactions)

    with col1:
        st.markdown(f"""
        <div class="stats-box">
            <h2 style="color: #2E7D32; margin: 0;">{total_transactions}</h2>
            <p style="margin: 0.5rem 0 0 0;">Total Transactions</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stats-box">
            <h2 style="color: #2E7D32; margin: 0;">{len(st.session_state.current_cart)}</h2>
            <p style="margin: 0.5rem 0 0 0;">Items in Cart</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # Calculate unique items
        all_items = set()
        for txn in st.session_state.transactions + st.session_state.imported_transactions:
            all_items.update(txn.get('items', []))

        st.markdown(f"""
        <div class="stats-box">
            <h2 style="color: #2E7D32; margin: 0;">{len(all_items)}</h2>
            <p style="margin: 0.5rem 0 0 0;">Unique Products</p>
        </div>
        """, unsafe_allow_html=True)

    # Quick Actions
    st.markdown("## 🚀 Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🛍️ Start Shopping", use_container_width=True):
            st.session_state.nav_page = "Shopping"
            st.rerun()

    with col2:
        if st.button("📁 Import Data", use_container_width=True):
            st.session_state.nav_page = "Data Import"
            st.rerun()

    with col3:
        if st.button("📊 View Transactions", use_container_width=True):
            st.session_state.nav_page = "View Transactions"
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>💡 <strong>Tip:</strong> Use the sidebar to navigate between different sections of the application.</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">Supermarket Shopping System v1.0</p>
    </div>
    """, unsafe_allow_html=True)