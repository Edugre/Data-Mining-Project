import streamlit as st
import pandas as pd

def render_page():
    st.title("📊 View Transactions")
    st.markdown("View and analyze all your transaction data in one place.")

    # Combine all transactions
    all_transactions = st.session_state.transactions + st.session_state.imported_transactions

    if len(all_transactions) == 0:
        st.info("No transactions found. Create transactions in the Shopping page or import data from the Data Import page.")
    else:
        # Statistics Section
        st.markdown("### 📈 Transaction Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Transactions", len(all_transactions))

        with col2:
            st.metric("Manual Transactions", len(st.session_state.transactions))

        with col3:
            st.metric("Imported Transactions", len(st.session_state.imported_transactions))

        with col4:
            # Calculate total items across all transactions
            total_items = sum(len(txn['items']) for txn in all_transactions)
            st.metric("Total Items Purchased", total_items)

        st.markdown("---")

        # Item Frequency Analysis
        st.markdown("### 🔝 Most Popular Items")

        from collections import Counter

        # Count all items
        all_items = []
        for txn in all_transactions:
            all_items.extend(txn['items'])

        item_counts = Counter(all_items)
        most_common = item_counts.most_common(10)

        if most_common:
            # Create DataFrame for display
            df_popular = pd.DataFrame(most_common, columns=['Item', 'Frequency'])
            df_popular.index = range(1, len(df_popular) + 1)

            col1, col2 = st.columns([2, 1])

            with col1:
                st.dataframe(df_popular, use_container_width=True)

            with col2:
                st.markdown("#### Quick Stats")
                st.metric("Unique Items", len(item_counts))
                if most_common:
                    st.metric("Most Popular Item", most_common[0][0])
                    st.metric("Times Purchased", most_common[0][1])

        st.markdown("---")

        # Transaction Data Table
        st.markdown("### 📋 All Transactions")

        # Create DataFrame from transactions
        transaction_data = []
        for txn in all_transactions:
            transaction_data.append({
                'Transaction ID': txn['transaction_id'],
                'Items': ', '.join(txn['items']),
                'Item Count': len(txn['items']),
                'Source': 'Manual' if txn in st.session_state.transactions else 'Imported'
            })

        df_transactions = pd.DataFrame(transaction_data)

        # Filter options
        col1, col2 = st.columns([1, 3])

        with col1:
            source_filter = st.selectbox("Filter by Source:", ["All", "Manual", "Imported"])

        with col2:
            search_item = st.text_input("Search for item:", placeholder="Enter item name...")

        # Apply filters
        df_filtered = df_transactions.copy()

        if source_filter != "All":
            df_filtered = df_filtered[df_filtered['Source'] == source_filter]

        if search_item:
            df_filtered = df_filtered[df_filtered['Items'].str.contains(search_item, case=False, na=False)]

        st.markdown(f"Showing **{len(df_filtered)}** of **{len(df_transactions)}** transactions")
        st.dataframe(df_filtered, use_container_width=True, height=400)

        st.markdown("---")

        # Export Section
        st.markdown("### 💾 Export Data")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Export all transactions to CSV
            if st.button("Export All Transactions", use_container_width=True):
                csv = df_transactions.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="all_transactions.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with col2:
            # Export manual transactions only
            if len(st.session_state.transactions) > 0:
                if st.button("Export Manual Only", use_container_width=True):
                    manual_data = []
                    for txn in st.session_state.transactions:
                        manual_data.append({
                            'transaction_id': txn['transaction_id'],
                            'items': ','.join(txn['items'])
                        })
                    df_manual = pd.DataFrame(manual_data)
                    csv_manual = df_manual.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_manual,
                        file_name="manual_transactions.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

        with col3:
            # Export item frequency analysis
            if st.button("Export Item Frequencies", use_container_width=True):
                df_freq = pd.DataFrame(item_counts.items(), columns=['Item', 'Frequency'])
                df_freq = df_freq.sort_values('Frequency', ascending=False)
                csv_freq = df_freq.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_freq,
                    file_name="item_frequencies.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        # Clear all data option
        st.markdown("---")
        st.markdown("### ⚠️ Danger Zone")

        if st.button("Clear All Transactions", type="secondary"):
            st.session_state.transactions = []
            st.session_state.imported_transactions = []
            st.session_state.transaction_counter = 1
            st.success("All transactions have been cleared.")
            st.rerun()