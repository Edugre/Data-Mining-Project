import streamlit as st
import pandas as pd
from algorithms.performance_comparison import compare_algorithms

def render_page(): 
    st.title("🔍 Association Rules Mining")
    st.markdown("Discover patterns in shopping behavior using Apriori and Eclat algorithms.")

    # Combine all transactions
    all_transactions = st.session_state.transactions + st.session_state.imported_transactions

    if len(all_transactions) == 0:
        st.warning("No transactions available for mining. Please create or import transactions first.")
        st.info("Visit the **Shopping** page to create transactions or the **Data Import** page to load data.")
    else:
        # Algorithm Configuration Section
        st.markdown("### ⚙️ Mining Parameters")

        col1, col2, col3 = st.columns(3)

        with col1:
            min_support = st.slider(
                "Minimum Support",
                min_value=0.01,
                max_value=1.0,
                value=0.2,
                step=0.01,
                help="Minimum frequency for an itemset to be considered frequent (e.g., 0.2 = appears in 20% of transactions)"
            )

        with col2:
            min_confidence = st.slider(
                "Minimum Confidence",
                min_value=0.01,
                max_value=1.0,
                value=0.5,
                step=0.01,
                help="Minimum confidence for a rule to be included (e.g., 0.5 = 50% confidence)"
            )

        with col3:
            st.metric("Total Transactions", len(all_transactions))
            if st.button("🚀 Run Mining Algorithms", type="primary", use_container_width=True):
                try:
                    with st.spinner("Running Apriori and Eclat algorithms..."):
                        # Run both algorithms
                        apriori_results, eclat_results, comparison_df = compare_algorithms(
                            all_transactions,
                            min_support=min_support,
                            min_confidence=min_confidence
                        )

                        # Store in session state
                        st.session_state.mining_results = {
                            'apriori': apriori_results,
                            'eclat': eclat_results,
                            'min_support': min_support,
                            'min_confidence': min_confidence
                        }
                        st.session_state.comparison_df = comparison_df

                    st.success("Mining completed successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error during mining: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

        # Display results if available
        if st.session_state.mining_results is not None:
            results = st.session_state.mining_results
            apriori_res = results['apriori']
            eclat_res = results['eclat']

            st.markdown("---")

            # Performance Comparison
            st.markdown("### 📊 Algorithm Performance Comparison")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Apriori Time",
                    f"{apriori_res['execution_time_ms']:.2f} ms"
                )

            with col2:
                st.metric(
                    "Eclat Time",
                    f"{eclat_res['execution_time_ms']:.2f} ms"
                )

            with col3:
                faster = "Apriori" if apriori_res['execution_time_ms'] < eclat_res['execution_time_ms'] else "Eclat"
                st.metric("Faster Algorithm", faster)

            with col4:
                st.metric("Rules Generated", apriori_res['num_rules'])

            # Detailed comparison table
            if st.session_state.comparison_df is not None:
                with st.expander("📈 Detailed Performance Metrics", expanded=False):
                    st.dataframe(st.session_state.comparison_df, use_container_width=True)

            st.markdown("---")

            # Product Recommendation System
            st.markdown("### 🎯 Product Recommendation System")
            st.markdown("Select a product to see what customers frequently buy together with it.")

            # Get all unique products from transactions
            all_items = set()
            for txn in all_transactions:
                all_items.update(txn['items'])

            # Sort products by those with association rules first
            products_with_rules = set()
            products_without_rules = set()

            for item in all_items:
                has_rules = False
                for rule in apriori_res['rules']:
                    if item in rule['antecedent']:
                        has_rules = True
                        break

                if has_rules:
                    products_with_rules.add(item)
                else:
                    products_without_rules.add(item)

            # Create sorted list: products with rules first (alphabetically), then products without rules (alphabetically)
            product_names = sorted(list(products_with_rules)) + sorted(list(products_without_rules))

            col1, col2 = st.columns([2, 1])

            with col1:
                selected_product = st.selectbox(
                    "Query Product:",
                    options=product_names,
                    help="Select a product to find association rules",
                    format_func=lambda x: f"✓ {x.title()}" if x in products_with_rules else f"  {x.title()}"
                )

            with col2:
                st.markdown("**Display Options:**")
                show_technical = st.checkbox("Show technical details", value=False)

            if selected_product:
                st.markdown(f"### Customers who bought **{selected_product.title()}** also bought:")

                # Filter rules where selected product is in antecedent
                relevant_rules = []
                for rule in apriori_res['rules']:
                    if selected_product in rule['antecedent']:
                        relevant_rules.append(rule)

                if len(relevant_rules) == 0:
                    st.info(f"No significant associations found for **{selected_product}** with current support/confidence thresholds.")
                    st.markdown("Try lowering the minimum support or confidence values to discover more patterns.")
                else:
                    # Sort by confidence
                    relevant_rules.sort(key=lambda x: x['confidence'], reverse=True)

                    # Display top recommendations
                    for i, rule in enumerate(relevant_rules[:10], 1):
                        consequent_items = sorted(list(rule['consequent']))
                        confidence_pct = rule['confidence'] * 100
                        support_pct = rule['support'] * 100
                        lift = rule['lift']

                        # Determine strength
                        if confidence_pct >= 70:
                            strength = "Strong"
                            strength_color = "#28a745"
                        elif confidence_pct >= 50:
                            strength = "Moderate"
                            strength_color = "#ffc107"
                        else:
                            strength = "Weak"
                            strength_color = "#6c757d"

                        # Create visual bar
                        bar_length = int(confidence_pct / 5)  # Scale to ~20 chars max
                        bar = "█" * bar_length

                        # Display recommendation
                        consequent_str = ", ".join([item.title() for item in consequent_items])

                        st.markdown(f"""
                        <div style="background-color: #f8f9fa; color: rgb(49, 51, 63); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {strength_color};">
                            <strong>{i}. {consequent_str}</strong>: {confidence_pct:.1f}% of the time
                            <div style="color: {strength_color}; font-family: monospace; font-size: 1.2rem; margin: 0.5rem 0;">
                                {bar}
                            </div>
                            <span style="color: {strength_color}; font-weight: bold;">({strength})</span>
                        </div>
                        """, unsafe_allow_html=True)

                        if show_technical:
                            st.markdown(f"   - **Support**: {support_pct:.1f}% | **Confidence**: {confidence_pct:.1f}% | **Lift**: {lift:.2f}")

                    st.markdown("---")

                    # Business Recommendations
                    st.markdown("### 💡 Business Recommendations")

                    if len(relevant_rules) > 0:
                        top_rule = relevant_rules[0]
                        top_items = ", ".join([item.title() for item in sorted(list(top_rule['consequent']))])

                        st.success(f"**Placement Strategy:** Consider placing **{top_items}** near **{selected_product.title()}** in store layout.")

                        # Find bundle opportunity (top 3 items)
                        bundle_items = [selected_product]
                        for rule in relevant_rules[:3]:
                            bundle_items.extend(list(rule['consequent']))

                        unique_bundle = list(set(bundle_items))[:4]  # Max 4 items
                        bundle_str = " + ".join([item.title() for item in unique_bundle])

                        st.info(f"**Potential Bundle:** {bundle_str}")

                        # Cross-sell opportunity
                        if top_rule['confidence'] >= 0.6:
                            st.warning(f"**Cross-Sell Opportunity:** {top_rule['confidence']*100:.0f}% of customers who buy **{selected_product.title()}** also purchase **{top_items}**. Consider promotional offers.")

            st.markdown("---")

            # All Rules View
            with st.expander("📋 View All Association Rules", expanded=False):
                st.markdown(f"**Total Rules Found:** {apriori_res['num_rules']}")

                if apriori_res['num_rules'] > 0:
                    # Create DataFrame of all rules
                    rules_data = []
                    for rule in apriori_res['rules']:
                        antecedent_str = ", ".join(sorted(list(rule['antecedent'])))
                        consequent_str = ", ".join(sorted(list(rule['consequent'])))

                        rules_data.append({
                            'Antecedent (If)': antecedent_str,
                            'Consequent (Then)': consequent_str,
                            'Support': f"{rule['support']*100:.1f}%",
                            'Confidence': f"{rule['confidence']*100:.1f}%",
                            'Lift': f"{rule['lift']:.2f}"
                        })

                    df_rules = pd.DataFrame(rules_data)

                    # Filtering options
                    col1, col2 = st.columns(2)

                    with col1:
                        search_antecedent = st.text_input("Filter by antecedent:", placeholder="e.g., milk")

                    with col2:
                        search_consequent = st.text_input("Filter by consequent:", placeholder="e.g., bread")

                    # Apply filters
                    df_filtered = df_rules.copy()

                    if search_antecedent:
                        df_filtered = df_filtered[df_filtered['Antecedent (If)'].str.contains(search_antecedent, case=False, na=False)]

                    if search_consequent:
                        df_filtered = df_filtered[df_filtered['Consequent (Then)'].str.contains(search_consequent, case=False, na=False)]

                    st.markdown(f"Showing **{len(df_filtered)}** of **{len(df_rules)}** rules")
                    st.dataframe(df_filtered, use_container_width=True, height=400)

                    # Export rules
                    if st.button("Export All Rules to CSV"):
                        csv_rules = df_rules.to_csv(index=False)
                        st.download_button(
                            label="Download Rules CSV",
                            data=csv_rules,
                            file_name=f"association_rules_sup{results['min_support']}_conf{results['min_confidence']}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                else:
                    st.warning("No rules found with current parameters. Try lowering the minimum support or confidence.")