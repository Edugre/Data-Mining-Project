import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from urllib.parse import quote

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
    height: 120px;
    border-radius: 12px;
    object-fit: cover;
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

PRODUCT_IMAGE_TAGS = {
    "Milk": "milk",
    "Bread": "fresh bread",
    "Eggs": "eggs",
    "Butter": "butter",
    "Cheese": "cheese",
    "Yogurt": "yogurt",
    "Chicken": "raw chicken",
    "Beef": "steak",
    "Apples": "apples",
    "Bananas": "bananas",
    "Tomatoes": "tomatoes",
    "Lettuce": "lettuce",
    "Rice": "rice grains",
    "Pasta": "pasta",
    "Coffee": "coffee beans",
    "Tea": "tea cup",
    "Sugar": "sugar",
    "Salt": "salt shaker",
    "Cooking Oil": "cooking oil",
    "Orange Juice": "orange juice",
}

FALLBACK_IMAGE_TAG = "grocery store"


def get_product_image(product_name):
    tag = PRODUCT_IMAGE_TAGS.get(product_name, FALLBACK_IMAGE_TAG)
    formatted = tag.lower().replace(" ", ",")
    slug = quote(formatted, safe=",")
    return f"https://loremflickr.com/320/240/{slug}"


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
                item_cols = st.columns([4, 1])

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
            st.markdown("##### Cleaned transactions preview")
            cleaned_df = build_transactions_dataframe(st.session_state.cleaned_transactions)
            st.dataframe(cleaned_df, hide_index=True, use_container_width=True)
            st.info("The View Transactions page now displays these cleaned totals and rows.")

    display_action_message()


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
    options=["Shopping", "Data Import", "View Transactions", "Preprocessing"],
)

st.sidebar.markdown("### Workflow")
st.sidebar.markdown("1. Build manual baskets\n2. Import CSV data\n3. Review transactions\n4. Run preprocessing")
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
else:
    render_preprocessing_page()
