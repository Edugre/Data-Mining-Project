import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Resolve project root (frontend -> src -> project)
project_root = Path(__file__).resolve().parent.parent.parent
src_dir = project_root / "src"

if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from preprocessing.preprocessing_utils import (
    load_transactions,
    load_products_set,
    preprocess_transactions,
    save_to_csv,
)
from algorithms.apriori import apriori, get_items_list
from algorithms.eclat import eclat
from algorithms.association_rules import generate_rules

st.set_page_config(
    page_title="Supermarket Shopping Simulation",
    page_icon=":shopping_trolley:",
    layout="wide",
)

CUSTOM_CSS = """
<style>
:root {
    --amazon-blue: #131921;
    --amazon-dark: #232f3e;
    --amazon-orange: #ff9900;
    --panel-bg: #ffffff;
}
html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
}
[data-testid="stAppViewContainer"] {
    background-color: #f4f5f7;
}
.header-container {
    background: linear-gradient(135deg, var(--amazon-blue), var(--amazon-dark));
    padding: 2rem;
    border-radius: 16px;
    color: #ffffff;
    margin-bottom: 1.5rem;
    box-shadow: 0 12px 24px rgba(0,0,0,0.15);
}
.header-container h1 {
    margin-bottom: 0.4rem;
}
.header-container p {
    margin: 0;
    color: #dcdcdc;
}
.product-card {
    background: var(--panel-bg);
    border-radius: 14px;
    padding: 1rem;
    border: 1px solid #e3e5e8;
    box-shadow: 0 4px 12px rgba(19,25,33,0.08);
    margin-bottom: 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
}
.product-card h4 {
    margin-bottom: 0.25rem;
    color: var(--amazon-blue);
}
.product-card img {
    width: 100%;
    aspect-ratio: 4 / 3;
    border-radius: 12px;
    object-fit: cover;
    display: block;
    box-shadow: inset 0 0 0 1px rgba(0,0,0,0.05);
}
.product-card .card-helper {
    margin: 0;
    font-size: 0.82rem;
    color: #6b6f77;
}
.cart-summary {
    background: var(--panel-bg);
    border-radius: 12px;
    padding: 0.6rem 0.9rem;
    box-shadow: 0 3px 8px rgba(19,25,33,0.12);
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: var(--amazon-blue);
}
.cart-item {
    padding: 0.6rem 0.85rem;
    border-radius: 12px;
    background: var(--panel-bg);
    color: #131921;
    font-weight: 600;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    margin-bottom: 0.45rem;
}
.cart-divider {
    border-top: 1px solid #ececec;
    margin: 0.6rem 0;
}
.stats-card {
    background: var(--panel-bg);
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 3px 8px rgba(19,25,33,0.1);
    text-align: center;
    margin-bottom: 1rem;
}
.stats-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--amazon-blue);
}
.stats-label {
    font-size: 0.95rem;
    color: #6b6f77;
}
.stats-helper {
    font-size: 0.85rem;
    color: #a1a5ad;
}
.info-panel {
    background: var(--panel-bg);
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.08);
}
.info-panel ul {
    padding-left: 1rem;
}
.info-panel li {
    margin-bottom: 0.25rem;
}
.stButton>button {
    border-radius: 32px;
    border: none;
    font-weight: 600;
    padding: 0.45rem 1rem;
    background: var(--amazon-orange);
    color: #131921;
    white-space: nowrap;
    word-break: keep-all;
}
.stButton>button:hover {
    background: #e38c04;
    color: #131921;
}
[data-testid="stSidebar"] {
    background-color: #0f1b2c;
}
[data-testid="stSidebar"] * {
    color: #f4f5f7 !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

STATE_DEFAULTS = {
    "transactions": [],
    "current_cart": [],
    "imported_transactions": [],
    "preprocessing_stats": None,
    "cleaned_transactions": [],
    "transaction_counter": 1,
    "action_message": "",
    "min_support": 0.2,
    "min_confidence": 0.5,
    "apriori_results": None,
    "eclat_results": None,
    "apriori_rules": None,
    "eclat_rules": None,
    "selected_product": None,
    "show_modal": False,
}

for key, default_value in STATE_DEFAULTS.items():
    if key not in st.session_state:
        if isinstance(default_value, list):
            st.session_state[key] = default_value.copy()
        else:
            st.session_state[key] = default_value

PRODUCTS = [
    "Milk",
    "Bread",
    "Eggs",
    "Butter",
    "Cheese",
    "Yogurt",
    "Chicken",
    "Beef",
    "Apples",
    "Bananas",
    "Tomatoes",
    "Lettuce",
    "Rice",
    "Pasta",
    "Coffee",
    "Tea",
    "Sugar",
    "Salt",
    "Cooking Oil",
    "Orange Juice",
]

PRODUCT_IMAGE_URLS = {
    "Milk": "https://i.imgur.com/i6GJnFY.jpeg",
    "Bread": "https://i.imgur.com/CwUTmM5.jpeg",
    "Eggs": "https://i.imgur.com/ElwxpIx.jpeg",
    "Butter": "https://i.imgur.com/gru3MXU.jpeg",
    "Cheese": "https://i.imgur.com/CNotm0n.jpeg",
    "Yogurt": "https://i.imgur.com/BYYp7iI.jpeg",
    "Chicken": "https://i.imgur.com/VdSkKTA.jpeg",
    "Beef": "https://i.imgur.com/y90fE33.jpeg",
    "Apples": "https://i.imgur.com/5j0P2ad.jpeg",
    "Bananas": "https://i.imgur.com/mVg0yTq.jpeg",
    "Tomatoes": "https://i.imgur.com/BZG2Hhu.jpeg",
    "Lettuce": "https://i.imgur.com/q7QvsHd.jpeg",
    "Rice": "https://i.imgur.com/YDlqOBp.jpeg",
    "Pasta": "https://i.imgur.com/gJpU8NT.jpeg",
    "Coffee": "https://i.imgur.com/Gkshypq.jpeg",
    "Tea": "https://i.imgur.com/UzhS4dj.jpeg",
    "Sugar": "https://i.imgur.com/RUtw6z1.jpeg",
    "Salt": "https://i.imgur.com/z6Y3dYj.jpeg",
    "Cooking Oil": "https://i.imgur.com/TLNwBwH.jpeg",
    "Orange Juice": "https://i.imgur.com/XZ8CcEh.jpeg",
}

FALLBACK_IMAGE_URL = "https://i.imgur.com/yourFallbackImage.jpg"


def get_product_image(product_name):
    return PRODUCT_IMAGE_URLS.get(product_name, FALLBACK_IMAGE_URL)


def invalidate_cleaned_results():
    """Clear cleaned data if manual/imported transactions change."""
    st.session_state.cleaned_transactions = []
    st.session_state.preprocessing_stats = None


def normalize_transactions(records):
    """Ensure each transaction dict has clean ids and item lists."""
    normalized = []
    for idx, record in enumerate(records, start=1):
        raw_id = str(record.get("transaction_id", "")).strip()
        transaction_id = raw_id or f"C{idx:03d}"

        raw_items = record.get("items", [])
        if isinstance(raw_items, str):
            item_candidates = raw_items.split(",")
        else:
            item_candidates = raw_items

        cleaned_items = []
        for item in item_candidates:
            text = str(item).strip()
            if text:
                cleaned_items.append(text)

        normalized.append(
            {
                "transaction_id": transaction_id,
                "items": cleaned_items,
            }
        )
    return normalized


def build_transactions_dataframe(transactions):
    if not transactions:
        return pd.DataFrame(columns=["Transaction ID", "Items", "Item Count"])

    rows = []
    for txn in transactions:
        items = txn.get("items", [])
        rows.append(
            {
                "Transaction ID": txn.get("transaction_id", ""),
                "Items": ", ".join(items),
                "Item Count": len(items),
            }
        )
    return pd.DataFrame(rows)


def transaction_stats(transactions):
    total = len(transactions)
    total_items = sum(len(txn.get("items", [])) for txn in transactions)
    unique_items = {item for txn in transactions for item in txn.get("items", [])}
    avg_items = total_items / total if total else 0

    return {
        "total": total,
        "total_items": total_items,
        "unique_items": len(unique_items),
        "avg_items": avg_items,
    }


def render_stats_card(value, label, helper=""):
    st.markdown(
        f"""
        <div class="stats-card">
            <div class="stats-value">{value}</div>
            <div class="stats-label">{label}</div>
            <div class="stats-helper">{helper}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_raw_transactions():
    return st.session_state.transactions + st.session_state.imported_transactions


def get_display_transactions():
    if st.session_state.cleaned_transactions:
        return st.session_state.cleaned_transactions
    return get_raw_transactions()


def display_action_message():
    if st.session_state.action_message:
        st.success(st.session_state.action_message)
        st.session_state.action_message = ""


def render_shopping_page():
    st.header("Manual Transaction Builder")
    st.caption("Tap the featured items to simulate a shopping trip and save it as a transaction.")

    col_products, col_cart = st.columns([2, 1])

    with col_products:
        st.markdown("#### Featured products")
        items_per_row = 4
        for start_idx in range(0, len(PRODUCTS), items_per_row):
            row_cols = st.columns(items_per_row)
            for offset in range(items_per_row):
                idx = start_idx + offset
                if idx >= len(PRODUCTS):
                    continue
                product = PRODUCTS[idx]
                with row_cols[offset]:
                    st.markdown(
                        f"""
                        <div class="product-card">
                            <img src="{get_product_image(product)}" alt="{product}" />
                            <h4>{product}</h4>
                            <p class="card-helper">Add this item to the current cart.</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Add to cart", key=f"product_{idx}", use_container_width=True):
                        st.session_state.current_cart.append(product)
                        st.session_state.action_message = f"{product} added to cart."

    with col_cart:
        st.markdown("#### Current cart")

        if st.session_state.current_cart:
            st.markdown(
                f"<div class='cart-summary'><span>{len(st.session_state.current_cart)} item(s)</span> selected</div>",
                unsafe_allow_html=True,
            )

            for idx, item in enumerate(st.session_state.current_cart):
                item_cols = st.columns([3, 1])

                item_cols[0].markdown(f"<div class='cart-item'>{item}</div>", unsafe_allow_html=True)
                if item_cols[1].button("Remove", key=f"remove_{idx}", use_container_width=True):
                    st.session_state.current_cart.pop(idx)
                    st.session_state.action_message = f"{item} removed from cart."
                    break

            st.markdown("<div class='cart-divider'></div>", unsafe_allow_html=True)

            action_cols = st.columns(2)
            if action_cols[0].button("Complete transaction", use_container_width=True):
                transaction_id = f"M{st.session_state.transaction_counter:03d}"
                st.session_state.transaction_counter += 1
                st.session_state.transactions.append(
                    {"transaction_id": transaction_id, "items": st.session_state.current_cart.copy()}
                )
                invalidate_cleaned_results()
                st.session_state.current_cart = []
                st.session_state.action_message = f"Transaction {transaction_id} saved."

            if action_cols[1].button("Clear cart", use_container_width=True):
                st.session_state.current_cart = []
                st.session_state.action_message = "Cart cleared."
        else:
            st.info("Start building a cart by clicking any product card.")

    display_action_message()

    if st.session_state.transactions:
        st.markdown("---")
        st.subheader("Saved manual transactions")
        manual_df = build_transactions_dataframe(st.session_state.transactions)
        st.dataframe(manual_df, hide_index=True, use_container_width=True)
    else:
        st.caption("No manual transactions saved yet.")


def render_data_import_page():
    st.header("CSV Data Import")
    st.caption("Import the provided dataset or upload your own transaction history.")

    if st.session_state.imported_transactions:
        st.markdown("##### Current imported transactions")
        stats = transaction_stats(st.session_state.imported_transactions)
        stat_cols = st.columns(3)
        with stat_cols[0]:
            render_stats_card(stats["total"], "Transactions", "")
        with stat_cols[1]:
            render_stats_card(stats["total_items"], "Items", f"{stats['unique_items']} unique products")
        with stat_cols[2]:
            render_stats_card(f"{stats['avg_items']:.1f}", "Avg items / transaction", "")

    col_upload, col_sample = st.columns([2, 1])

    with col_upload:
        st.subheader("Upload a CSV file")
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
            except Exception as exc:
                st.error(f"Unable to read file: {exc}")
            else:
                required_columns = {"transaction_id", "items"}
                if not required_columns.issubset(set(df.columns)):
                    st.error("CSV must include both 'transaction_id' and 'items' columns.")
                else:
                    df["items"] = df["items"].fillna("").apply(
                        lambda value: [item.strip() for item in str(value).split(",") if item.strip()]
                    )
                    imported_data = normalize_transactions(df.to_dict("records"))

                    st.success(f"Parsed {len(imported_data)} transactions from the uploaded file.")
                    preview_df = df.copy()
                    preview_df["items"] = preview_df["items"].apply(lambda lst: ", ".join(lst))
                    st.markdown("##### Preview")
                    st.dataframe(preview_df, hide_index=True, use_container_width=True)

                    if st.button("Add to current transactions", use_container_width=True):
                        st.session_state.imported_transactions = imported_data
                        invalidate_cleaned_results()
                        st.session_state.action_message = f"{len(imported_data)} imported transactions added."

    with col_sample:
        st.subheader("Provided sample data")
        st.write("Load the prepared dataset stored at `data/sample_transactions.csv`.")
        st.code("transaction_id,items\nT001,Milk,Bread,Eggs\nT002,Cheese,Butter", language="text")

        if st.button("Load sample_transactions.csv", use_container_width=True):
            sample_path = project_root / "data" / "sample_transactions.csv"
            try:
                sample_records = load_transactions(str(sample_path))
            except FileNotFoundError:
                st.error("Could not find data/sample_transactions.csv.")
            else:
                normalized = normalize_transactions(sample_records)
                st.session_state.imported_transactions = normalized
                invalidate_cleaned_results()
                st.session_state.action_message = (
                    f"Loaded {len(normalized)} transactions from sample_transactions.csv."
                )

    st.markdown("---")
    st.markdown(
        """
        <div class="info-panel">
            <strong>CSV requirements</strong>
            <ul>
                <li><code>transaction_id</code>: identifier for each basket</li>
                <li><code>items</code>: comma-separated list of purchased products</li>
                <li>Only CSV files are accepted and errors are reported inline</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    display_action_message()


def render_transactions_page():
    st.header("Transaction overview")

    combined = get_display_transactions()
    if not combined:
        st.info("No transactions available yet. Create a cart or import a CSV file first.")
        return

    if st.session_state.cleaned_transactions:
        st.caption("Displaying the cleaned dataset produced by the latest preprocessing run.")
    else:
        st.caption("Displaying the current manual + imported transactions.")

    stats = transaction_stats(combined)
    manual_count = len(st.session_state.transactions)
    imported_count = len(st.session_state.imported_transactions)

    stat_cols = st.columns(4)
    with stat_cols[0]:
        dataset_label = "Cleaned dataset" if st.session_state.cleaned_transactions else "Manual + imported"
        render_stats_card(stats["total"], "Total transactions", dataset_label)
    with stat_cols[1]:
        render_stats_card(stats["total_items"], "Total items", f"{stats['unique_items']} unique products")
    with stat_cols[2]:
        render_stats_card(f"{stats['avg_items']:.1f}", "Avg items / transaction", "")
    with stat_cols[3]:
        render_stats_card(manual_count, "Manual entries", f"{imported_count} imported")

    st.markdown("---")
    st.subheader("Transaction table")
    df = build_transactions_dataframe(combined)
    st.dataframe(df, hide_index=True, use_container_width=True)


def render_preprocessing_page():
    st.header("Data preprocessing")

    raw_transactions = get_raw_transactions()
    if not raw_transactions:
        st.warning("Add manual transactions or import CSV data before running preprocessing.")
        return

    st.caption(
        "Cleaning removes empty baskets, single-item transactions, duplicates, and products not in the official list."
    )

    products_path = project_root / "data" / "products.csv"

    try:
        products_set = load_products_set(str(products_path))
    except FileNotFoundError:
        st.error("Could not find data/products.csv.")
        return

    st.info(f"{len(products_set)} valid products loaded for validation.")

    if st.button("Run preprocessing", use_container_width=True):
        with st.spinner("Cleaning transactions..."):
            cleaned_transactions, stats = preprocess_transactions(raw_transactions, products_set)
            st.session_state.preprocessing_stats = stats
            st.session_state.cleaned_transactions = cleaned_transactions

            cleaned_path = project_root / "data" / "cleaned_transactions.csv"
            save_to_csv(cleaned_transactions, str(cleaned_path))
            st.session_state.action_message = (
                f"Preprocessing finished. {len(cleaned_transactions)} transactions saved to data/cleaned_transactions.csv."
            )

    if st.session_state.preprocessing_stats:
        stats = st.session_state.preprocessing_stats
        st.markdown("---")
        st.subheader("Preprocessing report")

        col_before, col_after = st.columns(2)

        with col_before:
            st.markdown("##### Before cleaning")
            st.metric("Total transactions", stats["first_total"])
            st.metric("Empty transactions", stats["empty"])
            st.metric("Single-item transactions", stats["single"])
            st.metric("Duplicate items", stats["duplicates"])
            st.metric("Invalid items", stats["invalid"])

        with col_after:
            st.markdown("##### After cleaning")
            st.metric("Valid transactions", stats["valid_transactions"])
            st.metric("Total items", stats["total_items"])
            st.metric("Unique products", stats["uniques"])
            removed = stats["first_total"] - stats["valid_transactions"]
            pct_removed = (removed / stats["first_total"] * 100) if stats["first_total"] else 0
            st.metric("Transactions removed", f"{removed} ({pct_removed:.1f}%)")

        if st.session_state.cleaned_transactions:
            st.markdown("##### Transactions before and after cleaning")
            preview_cols = st.columns(2)
            before_df = build_transactions_dataframe(raw_transactions)
            cleaned_df = build_transactions_dataframe(st.session_state.cleaned_transactions)

            with preview_cols[0]:
                st.markdown("###### Before preprocessing")
                st.dataframe(before_df, hide_index=True, use_container_width=True)

            with preview_cols[1]:
                st.markdown("###### After preprocessing")
                st.dataframe(cleaned_df, hide_index=True, use_container_width=True)

            st.info("The View Transactions page now displays these cleaned totals and rows.")

    display_action_message()


def run_mining_algorithms():
    """Run both Apriori and Eclat algorithms with current settings."""
    transactions = get_display_transactions()
    if not transactions:
        return False, "No transactions available. Please add data first."

    items_list = get_items_list(transactions)

    try:
        # Run Apriori
        apriori_freq = apriori(items_list, st.session_state.min_support)
        st.session_state.apriori_results = apriori_freq
        st.session_state.apriori_rules = generate_rules(apriori_freq, st.session_state.min_confidence)

        # Run Eclat
        eclat_freq = eclat(transactions, st.session_state.min_support)
        st.session_state.eclat_results = eclat_freq
        st.session_state.eclat_rules = generate_rules(eclat_freq, st.session_state.min_confidence)

        return True, f"Mining complete! Found {len(st.session_state.apriori_rules)} Apriori rules and {len(st.session_state.eclat_rules)} Eclat rules."
    except Exception as e:
        return False, f"Error running mining algorithms: {str(e)}"


def get_recommendations_for_product(product_name, algorithm="apriori"):
    """Get product recommendations based on association rules."""
    rules = st.session_state.apriori_rules if algorithm == "apriori" else st.session_state.eclat_rules

    if not rules:
        return []

    recommendations = []
    for rule in rules:
        # Check if product is in antecedent (left side)
        if product_name in rule['antecedent'] and len(rule['antecedent']) == 1:
            # Get consequent items
            for item in rule['consequent']:
                recommendations.append({
                    'item': item,
                    'confidence': rule['confidence'],
                    'support': rule['support'],
                    'lift': rule['lift']
                })

    # Sort by confidence (descending)
    recommendations.sort(key=lambda x: x['confidence'], reverse=True)

    # Remove duplicates, keeping highest confidence
    seen = set()
    unique_recommendations = []
    for rec in recommendations:
        if rec['item'] not in seen:
            seen.add(rec['item'])
            unique_recommendations.append(rec)

    return unique_recommendations


def get_strength_label(confidence):
    """Return strength label based on confidence value."""
    if confidence >= 0.7:
        return "Strong", "#28a745"
    elif confidence >= 0.5:
        return "Moderate", "#ffc107"
    else:
        return "Weak", "#6c757d"


def render_progress_bar(percentage, color="#ff9900"):
    """Render a visual progress bar."""
    filled_blocks = int(percentage / 100 * 20)
    empty_blocks = 20 - filled_blocks
    bar = "█" * filled_blocks + "░" * empty_blocks
    return f'<span style="color: {color}; font-family: monospace;">{bar}</span>'


def render_recommendation_modal(product_name, algorithm="apriori", show_technical=False):
    """Render the recommendation modal for a product."""
    st.markdown(f"### Recommendations for: {product_name}")

    recommendations = get_recommendations_for_product(product_name, algorithm)

    if not recommendations:
        st.info(f"No strong associations found for {product_name}. Try adjusting the confidence threshold in Settings.")
        return

    st.markdown(f"**Customers who bought {product_name} also bought:**")
    st.markdown("---")

    # Display recommendations
    for rec in recommendations[:10]:  # Show top 10
        item = rec['item']
        confidence = rec['confidence']
        percentage = int(confidence * 100)
        strength_label, strength_color = get_strength_label(confidence)

        # Progress bar
        progress_bar = render_progress_bar(percentage, strength_color)

        # Main display
        st.markdown(
            f"""
            <div style="margin-bottom: 1rem; padding: 0.75rem; background: white; border-radius: 8px; border-left: 4px solid {strength_color};">
                <strong style="font-size: 1.1rem;">{item}</strong>: {percentage}% of the time
                <br>
                {progress_bar}
                <span style="color: {strength_color}; font-weight: 600; margin-left: 0.5rem;">({strength_label})</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Technical details (if enabled)
        if show_technical:
            st.markdown(
                f"""
                <div style="margin-left: 1rem; margin-top: -0.5rem; margin-bottom: 1rem; font-size: 0.85rem; color: #6c757d;">
                    📊 Confidence: {confidence:.3f} | Support: {rec['support']:.3f} | Lift: {rec['lift']:.3f}
                </div>
                """,
                unsafe_allow_html=True
            )

    # Business recommendations
    st.markdown("---")
    st.markdown("### 💡 Business Recommendations")

    if recommendations:
        top_item = recommendations[0]['item']

        st.markdown(
            f"""
            <div style="background: #e7f3ff; padding: 1rem; border-radius: 8px; border-left: 4px solid #0066cc;">
                <strong>Store Layout Suggestion:</strong><br>
                Consider placing <strong>{top_item}</strong> near <strong>{product_name}</strong> in store layout.
                <br><br>
                <strong>Potential Bundle:</strong><br>
                {product_name} + {top_item}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Create bundle suggestion with top 3 items
        if len(recommendations) >= 2:
            bundle_items = [product_name, recommendations[0]['item'], recommendations[1]['item']]
            st.markdown(
                f"""
                <div style="background: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107; margin-top: 1rem;">
                    <strong>Combo Deal Opportunity:</strong><br>
                    {' + '.join(bundle_items)}
                </div>
                """,
                unsafe_allow_html=True
            )


def has_associations(product_name, algorithm="apriori"):
    """Check if a product has any association rules."""
    rules = st.session_state.apriori_rules if algorithm == "apriori" else st.session_state.eclat_rules

    if not rules:
        return False

    for rule in rules:
        if product_name in rule['antecedent'] and len(rule['antecedent']) == 1:
            return True
    return False


def render_mining_page():
    """Render the association rule mining page."""
    st.header("Association Rule Mining")
    st.caption("Discover product associations and get personalized recommendations.")

    # Check if we have data
    transactions = get_display_transactions()
    if not transactions:
        st.warning("No transaction data available. Please add data in the Shopping or Data Import pages.")
        return

    # Mining controls
    col1, col2 = st.columns([3, 1])

    with col1:
        st.info(f"📊 Current settings: Min Support = {st.session_state.min_support}, Min Confidence = {st.session_state.min_confidence}")

    with col2:
        if st.button("⚙️ Run Mining", use_container_width=True, type="primary"):
            with st.spinner("Running mining algorithms..."):
                success, message = run_mining_algorithms()
                if success:
                    st.success(message)
                else:
                    st.error(message)

    # Check if mining has been run
    if not st.session_state.apriori_rules and not st.session_state.eclat_rules:
        st.info("👆 Click 'Run Mining' to generate association rules.")
        return

    # Algorithm selector
    algorithm = st.radio(
        "Select algorithm:",
        options=["apriori", "eclat"],
        format_func=lambda x: "Apriori" if x == "apriori" else "Eclat",
        horizontal=True
    )

    # Show technical details toggle
    show_technical = st.checkbox("Show technical details (confidence, support, lift)", value=False)

    st.markdown("---")

    # Product selection
    st.subheader("🔍 Select a product to view recommendations")

    # Get unique products from transactions
    all_products = set()
    for txn in transactions:
        all_products.update(txn.get('items', []))

    # Sort products: those with associations first, then alphabetically within each group
    products_with_assoc = []
    products_without_assoc = []

    for product in all_products:
        if has_associations(product, algorithm):
            products_with_assoc.append(product)
        else:
            products_without_assoc.append(product)

    products_with_assoc.sort()
    products_without_assoc.sort()
    all_products = products_with_assoc + products_without_assoc

    # Search bar
    col_search, col_clear = st.columns([4, 1])
    with col_search:
        search_query = st.text_input(
            "Search for a product",
            placeholder="Type to search products...",
            label_visibility="collapsed"
        )
    with col_clear:
        if st.button("Clear", key="clear_search", use_container_width=True):
            search_query = ""
            st.session_state.selected_product = None

    # Filter products based on search query
    if search_query:
        filtered_products = [p for p in all_products if search_query.lower() in p.lower()]
        if filtered_products:
            st.caption(f"Found {len(filtered_products)} product(s) matching '{search_query}'")
        else:
            st.warning(f"No products found matching '{search_query}'")
    else:
        filtered_products = all_products
        products_with_count = len(products_with_assoc)
        st.caption(f"Showing all {len(all_products)} products ({products_with_count} with associations)")

    # Create a grid of product buttons
    st.markdown("Click on any product to see what customers typically buy with it:")

    # Add CSS to style primary and secondary buttons differently
    st.markdown("""
        <style>
        /* Override primary button style for products with associations */
        .stButton > button[kind="primary"] {
            background-color: #ff9900 !important;
            color: #131921 !important;
            font-weight: 600 !important;
            border: none !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #e38c00 !important;
        }

        /* Override secondary button style for products without associations */
        .stButton > button[kind="secondary"] {
            background-color: #e0e0e0 !important;
            color: #9e9e9e !important;
            opacity: 0.5 !important;
            border: none !important;
        }
        .stButton > button[kind="secondary"]:hover {
            opacity: 0.7 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if filtered_products:
        cols_per_row = 5
        for start_idx in range(0, len(filtered_products), cols_per_row):
            cols = st.columns(cols_per_row)
            for offset in range(cols_per_row):
                idx = start_idx + offset
                if idx >= len(filtered_products):
                    break

                product = filtered_products[idx]
                has_assoc = has_associations(product, algorithm)

                with cols[offset]:
                    # Use different button types based on association status
                    button_type = "primary" if has_assoc else "secondary"
                    if st.button(product, key=f"product_mining_{idx}", use_container_width=True, type=button_type):
                        st.session_state.selected_product = product

    # Display recommendations for selected product
    if st.session_state.selected_product:
        st.markdown("---")
        with st.container():
            render_recommendation_modal(
                st.session_state.selected_product,
                algorithm=algorithm,
                show_technical=show_technical
            )


def render_settings_page():
    """Render the settings page for mining parameters."""
    st.header("⚙️ Mining Settings")
    st.caption("Adjust the parameters for association rule mining algorithms.")

    st.markdown("---")

    # Support threshold
    st.subheader("Minimum Support")
    st.markdown(
        """
        <div class="info-panel">
            <strong>What is Support?</strong><br>
            Support measures how frequently an itemset appears in transactions.
            Higher values = more common patterns, but fewer rules.
        </div>
        """,
        unsafe_allow_html=True
    )

    min_support = st.slider(
        "Minimum Support Threshold",
        min_value=0.05,
        max_value=0.5,
        value=st.session_state.min_support,
        step=0.05,
        help="Minimum frequency required for an itemset to be considered frequent"
    )

    st.markdown("---")

    # Confidence threshold
    st.subheader("Minimum Confidence")
    st.markdown(
        """
        <div class="info-panel">
            <strong>What is Confidence?</strong><br>
            Confidence measures how often items in Y appear in transactions that contain X.
            Higher values = stronger rules, but fewer recommendations.
        </div>
        """,
        unsafe_allow_html=True
    )

    min_confidence = st.slider(
        "Minimum Confidence Threshold",
        min_value=0.1,
        max_value=0.9,
        value=st.session_state.min_confidence,
        step=0.05,
        help="Minimum confidence required for a rule to be generated"
    )

    st.markdown("---")

    # Save button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("💾 Save Settings", use_container_width=True, type="primary"):
            st.session_state.min_support = min_support
            st.session_state.min_confidence = min_confidence
            # Clear cached results to force re-mining
            st.session_state.apriori_results = None
            st.session_state.eclat_results = None
            st.session_state.apriori_rules = None
            st.session_state.eclat_rules = None
            st.success("Settings saved! Please re-run mining on the Mining page.")

    # Current settings summary
    st.markdown("---")
    st.subheader("Current Settings Summary")

    col1, col2 = st.columns(2)
    with col1:
        render_stats_card(f"{st.session_state.min_support * 100:.0f}%", "Minimum Support", "")
    with col2:
        render_stats_card(f"{st.session_state.min_confidence * 100:.0f}%", "Minimum Confidence", "")

    # Impact explanation
    st.markdown(
        """
        <div class="info-panel" style="margin-top: 1rem;">
            <strong>💡 Tips:</strong>
            <ul>
                <li>Lower support = more rules, but may include rare patterns</li>
                <li>Higher support = fewer rules, but more reliable patterns</li>
                <li>Lower confidence = more recommendations, but weaker associations</li>
                <li>Higher confidence = fewer recommendations, but stronger associations</li>
                <li>Recommended starting point: Support 0.2, Confidence 0.5</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    """
    <div class="header-container">
        <h1>PrimeMart Shopping Studio</h1>
        <p>Simulate a supermarket journey, import datasets, and prepare them for association rule mining.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Jump to",
    options=["Shopping", "Data Import", "View Transactions", "Preprocessing", "Mining", "Settings"],
)

st.sidebar.markdown("### Workflow")
st.sidebar.markdown("1. Build manual baskets\n2. Import CSV data\n3. Review transactions\n4. Run preprocessing\n5. Configure settings\n6. Run mining")
st.sidebar.markdown("---")
st.sidebar.metric("Manual transactions", len(st.session_state.transactions))
st.sidebar.metric("Imported transactions", len(st.session_state.imported_transactions))
if st.session_state.preprocessing_stats:
    st.sidebar.metric("Cleaned transactions", st.session_state.preprocessing_stats["valid_transactions"])
else:
    st.sidebar.metric("Cleaned transactions", len(st.session_state.cleaned_transactions))

if page == "Shopping":
    render_shopping_page()
elif page == "Data Import":
    render_data_import_page()
elif page == "View Transactions":
    render_transactions_page()
elif page == "Preprocessing":
    render_preprocessing_page()
elif page == "Mining":
    render_mining_page()
elif page == "Settings":
    render_settings_page()
