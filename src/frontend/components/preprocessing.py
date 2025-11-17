import streamlit as st
import pandas as pd
from pathlib import Path
from preprocessing.preprocessing_utils import preprocess_transactions, load_products_set

def render_page():
    st.title("🔧 Data Preprocessing")
    st.markdown("Clean and standardize your transaction data to prepare it for analysis.")

    # Combine all transactions
    all_transactions = st.session_state.transactions + st.session_state.imported_transactions

    if len(all_transactions) == 0:
        st.warning("No transactions available for preprocessing. Please create or import transactions first.")
        st.info("Visit the **Shopping** page to create transactions or the **Data Import** page to load data.")
    else:
        # Overview section
        st.markdown("### 📋 Preprocessing Overview")
        st.markdown("""
        This tool will automatically clean your transaction data by:
        - **Standardizing product names** (converting to lowercase, removing extra spaces)
        - **Removing duplicate items** within each transaction
        - **Removing invalid products** (items not in the official product catalog)
        - **Filtering empty transactions** (transactions with no items after cleaning)
        - **Filtering single-item transactions** (transactions with only one item have no association value)
        """)

        st.markdown("---")

        # Before Preprocessing Section
        st.markdown("### 📊 Current Data Status")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Transactions", len(all_transactions))

        with col2:
            total_items = sum(len(txn['items']) for txn in all_transactions)
            st.metric("Total Items", total_items)

        with col3:
            all_items = set()
            for txn in all_transactions:
                all_items.update(txn.get('items', []))
            st.metric("Unique Items", len(all_items))

        # Preview before preprocessing
        st.markdown("#### Sample Transactions (Before Cleaning)")
        preview_transactions = all_transactions[:10]
        preview_data = []
        for txn in preview_transactions:
            preview_data.append({
                'Transaction ID': txn['transaction_id'],
                'Items': ', '.join(txn['items']),
                'Item Count': len(txn['items'])
            })
        df_preview = pd.DataFrame(preview_data)
        st.dataframe(df_preview, use_container_width=True)

        st.markdown("---")

        # Preprocessing Action
        st.markdown("### ⚙️ Run Preprocessing")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.info("Click the button below to clean and standardize your transaction data. The preprocessing report will show you what changes were made.")

        with col2:
            if st.button("🚀 Run Preprocessing", type="primary", use_container_width=True):
                # Load valid products from products.csv
                products_path = Path("data/products.csv")

                if products_path.exists():
                    try:
                        # Load valid products
                        valid_products = load_products_set(str(products_path))

                        # Run preprocessing
                        cleaned_txns, stats = preprocess_transactions(all_transactions, valid_products)

                        # Store results in session state
                        st.session_state.cleaned_transactions = cleaned_txns
                        st.session_state.preprocessing_stats = stats

                        st.success("Preprocessing completed successfully!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error during preprocessing: {str(e)}")
                else:
                    st.error("products.csv file not found. Cannot validate product names.")

        # Display preprocessing results if available
        if st.session_state.preprocessing_stats is not None:
            st.markdown("---")
            st.markdown("### 📈 Preprocessing Report")

            stats = st.session_state.preprocessing_stats

            # Before Cleaning Section
            st.markdown("#### Before Cleaning")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Transactions", stats['first_total'])

            with col2:
                st.metric("Empty Transactions", stats['empty'],
                         help="Transactions with no items")

            with col3:
                st.metric("Single-Item Transactions", stats['single'],
                         help="Transactions with only one item (removed for association mining)")

            with col4:
                issues_found = stats['duplicates'] + stats['invalid']
                st.metric("Issues Found", issues_found,
                         help="Total duplicate and invalid items found")

            # Issues Breakdown
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Data Quality Issues:**")
                st.write(f"- Duplicate items found: **{stats['duplicates']}** instances")
                st.write(f"- Invalid items found: **{stats['invalid']}** instances")

            with col2:
                removed_txns = stats['empty'] + stats['single']
                st.markdown("**Transactions Removed:**")
                st.write(f"- Empty transactions: **{stats['empty']}**")
                st.write(f"- Single-item transactions: **{stats['single']}**")
                st.write(f"- **Total removed: {removed_txns}**")

            st.markdown("---")

            # After Cleaning Section
            st.markdown("#### After Cleaning")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Valid Transactions", stats['valid_transactions'],
                         delta=stats['valid_transactions'] - stats['first_total'],
                         delta_color="normal")

            with col2:
                st.metric("Total Items", stats['total_items'])

            with col3:
                st.metric("Unique Products", stats['uniques'])

            # Preview cleaned data - side by side comparison
            st.markdown("---")
            st.markdown("#### Before & After Comparison")

            if len(st.session_state.cleaned_transactions) > 0:
                # Get the first 10 transaction IDs from cleaned data
                cleaned_ids = [txn['transaction_id'] for txn in st.session_state.cleaned_transactions]

                # Find corresponding original transactions
                original_preview = [txn for txn in all_transactions if txn['transaction_id'] in cleaned_ids]
                cleaned_preview = st.session_state.cleaned_transactions

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Before Cleaning**")
                    before_data = []
                    for txn in original_preview:
                        before_data.append({
                            'Transaction ID': txn['transaction_id'],
                            'Items': ', '.join(txn['items']),
                            'Count': len(txn['items'])
                        })
                    df_before = pd.DataFrame(before_data)
                    st.dataframe(df_before, use_container_width=True, height=400)

                with col2:
                    st.markdown("**After Cleaning**")
                    after_data = []
                    for txn in cleaned_preview:
                        after_data.append({
                            'Transaction ID': txn['transaction_id'],
                            'Items': ', '.join(txn['items']),
                            'Count': len(txn['items'])
                        })
                    df_after = pd.DataFrame(after_data)
                    st.dataframe(df_after, use_container_width=True, height=400)
            else:
                st.warning("No valid transactions remain after preprocessing.")

            st.markdown("---")

            # Apply cleaned data
            st.markdown("---")
            st.markdown("### ✅ Apply Cleaned Data")

            st.info("**Important:** Applying cleaned data will replace your current transactions with the cleaned versions. This action cannot be undone unless you have exported your original data.")

            col1, col2 = st.columns([1, 2])

            with col1:
                if len(st.session_state.cleaned_transactions) > 0:
                    if st.button("Apply Cleaned Transactions", use_container_width=True, type="primary"):
                        # Replace all transactions with cleaned ones
                        st.session_state.transactions = []
                        st.session_state.imported_transactions = st.session_state.cleaned_transactions.copy()

                        # Clear preprocessing results
                        st.session_state.preprocessing_stats = None
                        st.session_state.cleaned_transactions = []

                        st.success(f"Successfully applied {len(st.session_state.imported_transactions)} cleaned transactions!")
                        st.info("Your transaction data has been updated. Visit the 'View Transactions' page to see the changes.")
                        st.rerun()

            with col2:
                st.markdown("""
                **What happens when you apply:**
                - All current transactions (manual + imported) will be replaced
                - Cleaned transactions will be stored as imported transactions
                - Manual transactions will be cleared
                - Preprocessing results will be reset
                """)

            # Export cleaned data
            st.markdown("---")
            st.markdown("### 💾 Export Cleaned Data")

            col1, col2, col3 = st.columns(3)

            with col1:
                if len(st.session_state.cleaned_transactions) > 0:
                    if st.button("Export Cleaned Transactions", use_container_width=True):
                        # Prepare data for export
                        export_data = []
                        for txn in st.session_state.cleaned_transactions:
                            export_data.append({
                                'transaction_id': txn['transaction_id'],
                                'items': ','.join(txn['items'])
                            })
                        df_export = pd.DataFrame(export_data)
                        csv_export = df_export.to_csv(index=False)

                        st.download_button(
                            label="Download Cleaned CSV",
                            data=csv_export,
                            file_name="cleaned_transactions.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

            with col2:
                if st.button("Export Preprocessing Report", use_container_width=True):
                    # Create report text
                    report = f"""Preprocessing Report
-------------------
Before Cleaning:
- Total transactions: {stats['first_total']}
- Empty transactions: {stats['empty']}
- Single-item transactions: {stats['single']}
- Duplicate items found: {stats['duplicates']} instances
- Invalid items found: {stats['invalid']} instances

After Cleaning:
- Valid transactions: {stats['valid_transactions']}
- Total items: {stats['total_items']}
- Unique products: {stats['uniques']}
"""

                    st.download_button(
                        label="Download Report",
                        data=report,
                        file_name="preprocessing_report.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

            with col3:
                if st.button("Reset Preprocessing", use_container_width=True, type="secondary"):
                    st.session_state.preprocessing_stats = None
                    st.session_state.cleaned_transactions = []
                    st.success("Preprocessing results have been cleared.")
                    st.rerun()