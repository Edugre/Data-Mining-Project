import streamlit as st
import pandas as pd
from pathlib import Path

def render_page(): 
    st.title("📁 Data Import")
    st.markdown("Import transaction data from CSV files to expand your dataset.")

    # Two import options
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📂 Upload CSV File")
        st.markdown("Upload your own transaction CSV file with the format: `transaction_id,items`")

        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'], key="csv_uploader")

        if uploaded_file is not None:
            try:
                # Read the uploaded file
                df = pd.read_csv(uploaded_file)

                # Validate format
                if 'transaction_id' not in df.columns or 'items' not in df.columns:
                    st.error("Invalid CSV format! File must contain 'transaction_id' and 'items' columns.")
                else:
                    st.success(f"File loaded successfully! Found {len(df)} transactions.")

                    # Preview
                    st.markdown("#### Preview (first 5 rows)")
                    st.dataframe(df.head(), use_container_width=True)

                    # Import button
                    if st.button("Import Transactions", key="import_uploaded", type="primary"):
                        imported_count = 0
                        for _, row in df.iterrows():
                            # Parse items (comma-separated string)
                            items_str = str(row['items'])
                            items_list = [item.strip() for item in items_str.split(',')]

                            transaction = {
                                'transaction_id': row['transaction_id'],
                                'items': items_list
                            }
                            st.session_state.imported_transactions.append(transaction)
                            imported_count += 1

                        st.success(f"Successfully imported {imported_count} transactions!")
                        st.rerun()

            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.info("Please ensure your CSV file is properly formatted with 'transaction_id' and 'items' columns.")

    with col2:
        st.markdown("### 📊 Load Sample Data")
        st.markdown("Load the sample transaction dataset from `sample_transactions.csv`")

        sample_file_path = Path("data/sample_transactions.csv")

        if sample_file_path.exists():
            try:
                # Read sample file
                df_sample = pd.read_csv(sample_file_path)

                st.info(f"Sample dataset contains {len(df_sample)} transactions")

                # Preview
                st.markdown("#### Preview (first 5 rows)")
                st.dataframe(df_sample.head(), use_container_width=True)

                # Load button
                if st.button("Load Sample Data", key="load_sample", type="primary"):
                    imported_count = 0
                    for _, row in df_sample.iterrows():
                        # Parse items (comma-separated string)
                        items_str = str(row['items'])
                        items_list = [item.strip() for item in items_str.split(',')]

                        transaction = {
                            'transaction_id': row['transaction_id'],
                            'items': items_list
                        }
                        st.session_state.imported_transactions.append(transaction)
                        imported_count += 1

                    st.success(f"Successfully loaded {imported_count} sample transactions!")
                    st.rerun()

            except Exception as e:
                st.error(f"Error reading sample file: {str(e)}")
        else:
            st.warning(f"Sample file not found at: {sample_file_path}")

    # Current imported data status
    st.markdown("---")
    st.markdown("### 📈 Import Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Imported Transactions", len(st.session_state.imported_transactions))

    with col2:
        st.metric("Manual Transactions", len(st.session_state.transactions))

    with col3:
        total = len(st.session_state.imported_transactions) + len(st.session_state.transactions)
        st.metric("Total Transactions", total)

    # Clear imported data option
    if len(st.session_state.imported_transactions) > 0:
        st.markdown("---")
        if st.button("Clear All Imported Data", type="secondary"):
            st.session_state.imported_transactions = []
            st.success("All imported transactions have been cleared.")
            st.rerun()