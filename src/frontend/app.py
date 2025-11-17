import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from preprocessing.preprocessing_utils import preprocess_transactions, load_products_set
from algorithms.performance_comparison import compare_algorithms

# Import page modules
from components import (
    home,
    shopping,
    data_import,
    preprocessing,
    mining,
    transactions
)

# Page configuration
st.set_page_config(
    page_title="Supermarket Shopping System",
    page_icon=":shopping_cart:",
    layout="wide",
)

# Custom CSS for styling
CUSTOM_CSS = """
<style>
.main-header {
    background: linear-gradient(135deg, #81C784 0%, #2E7D32 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.feature-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid #2E7D32;
    margin-bottom: 1rem;
    color: rgb(49, 51, 63);
}
.feature-card h3 {
    color: #2E7D32;
    margin-top: 0;
}
.workflow-step {
    background-color: #e7f3ff;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 4px solid #2E7D32;
    color: rgb(49, 51, 63);
}
.stats-box {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    color: rgb(49, 51, 63);
}
.product-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    background-color: white;
    transition: transform 0.2s, box-shadow 0.2s;
    height: 100%;
}
.product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.product-card img {
    border-radius: 8px;
    width: 100%;
    height: 200px;
    object-fit: contain;
    margin-bottom: 0.5rem;
    background-color: #f8f9fa;
}
.product-card h4 {
    color: #333;
    margin: 0.5rem 0;
}
.product-card .category {
    color: #2E7D32;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
}
.cart-item {
    background-color: #f8f9fa;
    padding: 0.75rem;
    border-radius: 6px;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: rgb(49, 51, 63);
}
/* Primary button styling - all variations */
.stButton > button[kind="primary"],
.stButton > button[data-testid*="primary"],
button[kind="primary"],
div[data-testid="stButton"] button[kind="primary"] {
    background-color: #FFC947 !important;
    border-color: #FFC947 !important;
    color: rgb(49, 51, 63) !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid*="primary"]:hover,
button[kind="primary"]:hover,
div[data-testid="stButton"] button[kind="primary"]:hover {
    background-color: #FFB300 !important;
    border-color: #FFB300 !important;
}
.stButton > button[kind="primary"]:active,
.stButton > button[kind="primary"]:focus,
button[kind="primary"]:active,
button[kind="primary"]:focus {
    background-color: #FFB300 !important;
    border-color: #FFB300 !important;
    box-shadow: 0 0 0 0.2rem rgba(255, 201, 71, 0.5) !important;
}
/* Secondary button styling */
.stButton > button[kind="secondary"],
.stButton > button[data-testid*="secondary"],
button[kind="secondary"],
div[data-testid="stButton"] button[kind="secondary"] {
    background-color: white !important;
    border-color: #FF7043 !important;
    color: rgb(49, 51, 63) !important;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid*="secondary"]:hover,
button[kind="secondary"]:hover,
div[data-testid="stButton"] button[kind="secondary"]:hover {
    background-color: #FF7043 !important;
    border-color: #FF7043 !important;
    color: rgb(49, 51, 63) !important;
}
/* Default buttons without type specified */
.stButton > button:not([kind]),
div[data-testid="stButton"] button:not([kind]),
button:not([kind="primary"]):not([kind="secondary"]) {
    background-color: white !important;
    border: 2px solid #FF7043 !important;
    color: #FF7043 !important;
}
.stButton > button:not([kind]):hover,
div[data-testid="stButton"] button:not([kind]):hover {
    background-color: #FF7043 !important;
    color: white !important;
}
/* Force all streamlit buttons to use the color scheme */
div[data-testid="stButton"] button {
    background-color: #FFC947 !important;
    border-color: #FFC947 !important;
    color: white !important;
}
div[data-testid="stButton"] button:hover {
    background-color: #FFB300 !important;
    border-color: #FFB300 !important;
}
/* Download button styling */
.stDownloadButton > button {
    background-color: #FFC947 !important;
    border-color: #FFC947 !important;
    color: white !important;
}
.stDownloadButton > button:hover {
    background-color: #FFB300 !important;
    border-color: #FFB300 !important;
}
/* Slider styling */
.stSlider > div > div > div > div {
    background-color: #2E7D32 !important;
}
.stSlider > div > div > div > div > div {
    background-color: #2E7D32 !important;
}
.stSlider [role="slider"] {
    background-color: #2E7D32 !important;
}
.stSlider [data-baseweb="slider"] > div > div {
    background-color: #2E7D32 !important;
}
.stSlider [data-baseweb="slider"] [role="slider"] {
    background-color: #2E7D32 !important;
}
/* Slider thumb */
.stSlider [data-baseweb="slider"] [role="slider"]:focus {
    box-shadow: 0 0 0 0.2rem rgba(46, 125, 50, 0.5) !important;
}
/* Slider value labels */
.stSlider [data-baseweb="slider"] div[data-testid] {
    color: #2E7D32 !important;
}
.stSlider div[role="presentation"] {
    color: #2E7D32 !important;
}
/* Input field focus styling */
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > div:focus-within,
.stNumberInput > div > div > input:focus {
    border-color: #2E7D32 !important;
    box-shadow: 0 0 0 0.2rem rgba(46, 125, 50, 0.25) !important;
}
/* Selectbox dropdown styling */
.stSelectbox [data-baseweb="select"] > div {
    border-color: #e0e0e0;
}
.stSelectbox [data-baseweb="select"] > div:focus-within {
    border-color: #2E7D32 !important;
    box-shadow: 0 0 0 0.2rem rgba(46, 125, 50, 0.25) !important;
}
.stSelectbox [data-baseweb="select"] svg {
    fill: #2E7D32 !important;
}
/* Dropdown menu items */
[data-baseweb="popover"] [role="option"]:hover {
    background-color: rgba(46, 125, 50, 0.1) !important;
}
[data-baseweb="popover"] [role="option"][aria-selected="true"] {
    background-color: rgba(46, 125, 50, 0.2) !important;
}
/* Radio button styling */
.stRadio > div > label > div[data-checked="true"] {
    background-color: #2E7D32;
    border-color: #2E7D32;
}
.stRadio > div > label:hover > div[data-checked="true"] {
    background-color: #1B5E20;
    border-color: #1B5E20;
}
/* Checkbox styling */
.stCheckbox > label > div[data-checked="true"] {
    background-color: #2E7D32;
    border-color: #2E7D32;
}
.stCheckbox > label:hover > div[data-checked="true"] {
    background-color: #1B5E20;
    border-color: #1B5E20;
}
/* File uploader styling */
.stFileUploader > div > button {
    border-color: #2E7D32;
    color: #2E7D32;
}
.stFileUploader > div > button:hover {
    background-color: rgba(46, 125, 50, 0.1);
    border-color: #1B5E20;
    color: #1B5E20;
}
/* Tabs styling */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    border-bottom-color: #2E7D32;
    color: #2E7D32;
}
.stTabs [data-baseweb="tab-list"] button:hover {
    color: #2E7D32;
}
/* Expander styling */
.streamlit-expanderHeader:hover {
    color: #2E7D32;
}
/* Link styling */
a, a:visited {
    color: #2E7D32;
}
a:hover {
    color: #1B5E20;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Session state initialization
if 'current_cart' not in st.session_state:
    st.session_state.current_cart = []
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'imported_transactions' not in st.session_state:
    st.session_state.imported_transactions = []
if 'transaction_counter' not in st.session_state:
    st.session_state.transaction_counter = 1
if 'preprocessing_stats' not in st.session_state:
    st.session_state.preprocessing_stats = None
if 'cleaned_transactions' not in st.session_state:
    st.session_state.cleaned_transactions = []
if 'mining_results' not in st.session_state:
    st.session_state.mining_results = None
if 'comparison_df' not in st.session_state:
    st.session_state.comparison_df = None

# Sidebar Navigation
st.sidebar.title("Navigation")

# Check if there's a navigation override from quick actions
if 'nav_page' in st.session_state and st.session_state.nav_page is not None:
    default_page = st.session_state.nav_page
    st.session_state.nav_page = None  # Clear after use
else:
    default_page = "Home"

# Get the index of the default page
pages_list = ["Home", "Shopping", "Data Import", "Data Preprocessing", "Association Rules Mining", "View Transactions"]
try:
    default_index = pages_list.index(default_page)
except ValueError:
    default_index = 0

page = st.sidebar.radio(
    "Go to",
    pages_list,
    index=default_index
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")
st.sidebar.metric("Manual Transactions", len(st.session_state.transactions))
st.sidebar.metric("Imported Transactions", len(st.session_state.imported_transactions))
st.sidebar.metric("Items in Cart", len(st.session_state.current_cart))

# Route to appropriate page
if page == "Home":
    home.render_page()
elif page == "Shopping":
    shopping.render_page()
elif page == "Data Import":
    data_import.render_page()
elif page == "Data Preprocessing":
    preprocessing.render_page()
elif page == "Association Rules Mining":
    mining.render_page()
elif page == "View Transactions":
    transactions.render_page()