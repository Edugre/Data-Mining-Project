import time
import tracemalloc
import pandas as pd
from typing import Dict, List, Tuple, Any

from .apriori import apriori, get_items_list as apriori_get_items
from .eclat import eclat
from .association_rules import generate_rules

def measure_algorithm_performance(algorithm_func, transactions, min_support=0.2,min_confidence=0.5, algorithm_name="Algorithm"):

    tracemalloc.start()

    start_time = time.time()

    frequent_itemsets = algorithm_func(transactions, min_support)

    rules = generate_rules(frequent_itemsets, min_confidence)

    end_time = time.time()
    execution_time_ms = (end_time - start_time) * 1000  

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    current_memory_mb = current / (1024 * 1024)
    peak_memory_mb = peak / (1024 * 1024)

    total_frequent_itemsets = sum(len(Lk) for Lk in frequent_itemsets)

    return {
        'algorithm': algorithm_name,
        'execution_time_ms': round(execution_time_ms, 2),
        'num_frequent_itemsets': total_frequent_itemsets,
        'num_rules': len(rules),
        'current_memory_mb': round(current_memory_mb, 3),
        'peak_memory_mb': round(peak_memory_mb, 3),
        'rules': rules,
        'frequent_itemsets': frequent_itemsets
    }


def compare_algorithms(transactions, min_support=0.2, min_confidence=0.5):

    print("Running performance comparison...")
    print(f"Parameters: min_support={min_support}, min_confidence={min_confidence}")
    print(f"Total transactions: {len(transactions)}\n")

    apriori_transactions = apriori_get_items(transactions)

    print("Running Apriori algorithm...")
    apriori_results = measure_algorithm_performance(
        apriori,
        apriori_transactions,
        min_support,
        min_confidence,
        "Apriori"
    )
    print(f"✓ Apriori completed in {apriori_results['execution_time_ms']:.2f}ms")

    print("Running Eclat algorithm...")
    eclat_results = measure_algorithm_performance(
        eclat,
        transactions,
        min_support,
        min_confidence,
        "Eclat"
    )
    print(f"✓ Eclat completed in {eclat_results['execution_time_ms']:.2f}ms\n")

    comparison_df = create_comparison_dataframe(apriori_results, eclat_results)

    return apriori_results, eclat_results, comparison_df


def create_comparison_dataframe(apriori_results, eclat_results):

    comparison_data = {
        'Metric': [
            'Execution Time (ms)',
            'Frequent Itemsets',
            'Association Rules',
            'Current Memory (MB)',
            'Peak Memory (MB)'
        ],
        'Apriori': [
            apriori_results['execution_time_ms'],
            apriori_results['num_frequent_itemsets'],
            apriori_results['num_rules'],
            apriori_results['current_memory_mb'],
            apriori_results['peak_memory_mb']
        ],
        'Eclat': [
            eclat_results['execution_time_ms'],
            eclat_results['num_frequent_itemsets'],
            eclat_results['num_rules'],
            eclat_results['current_memory_mb'],
            eclat_results['peak_memory_mb']
        ]
    }

    df = pd.DataFrame(comparison_data)

    differences = []
    for i, metric in enumerate(comparison_data['Metric']):
        apriori_val = comparison_data['Apriori'][i]
        eclat_val = comparison_data['Eclat'][i]

        if apriori_val == 0:
            diff = "N/A"
        else:
            ratio = eclat_val / apriori_val
            if ratio < 1:
                diff = f"{(1-ratio)*100:.1f}% faster"
            elif ratio > 1:
                diff = f"{(ratio-1)*100:.1f}% slower"
            else:
                diff = "Same"

        differences.append(diff)

    df['Eclat vs Apriori'] = differences

    return df


def print_comparison_summary(comparison_df):

    print("\n" + "="*70)
    print("ALGORITHM PERFORMANCE COMPARISON")
    print("="*70)
    print(comparison_df.to_string(index=False))
    print("="*70 + "\n")


def get_winner(apriori_results, eclat_results):

    time_winner = "Apriori" if apriori_results['execution_time_ms'] < eclat_results['execution_time_ms'] else "Eclat"

    memory_winner = "Apriori" if apriori_results['peak_memory_mb'] < eclat_results['peak_memory_mb'] else "Eclat"

    rules_match = apriori_results['num_rules'] == eclat_results['num_rules']

    summary = f"""
Performance Summary:
-------------------
Faster Algorithm: {time_winner} ({min(apriori_results['execution_time_ms'], eclat_results['execution_time_ms']):.2f}ms)
Lower Memory Usage: {memory_winner} ({min(apriori_results['peak_memory_mb'], eclat_results['peak_memory_mb']):.3f}MB)
Rules Generated Match: {'Yes' if rules_match else 'No'} (Apriori: {apriori_results['num_rules']}, Eclat: {eclat_results['num_rules']})
"""

    return summary

def main():
    from pathlib import Path
    import sys

    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    from src.preprocessing.preprocessing_utils import load_transactions

    transaction_path = project_root / "data" / "cleaned_transactions.csv"

    if not transaction_path.exists():
        print(f"Error: {transaction_path} not found!")
        print("Please run preprocessing first to generate cleaned_transactions.csv")
        return

    transactions = load_transactions(transaction_path)

    apriori_results, eclat_results, comparison_df = compare_algorithms(
        transactions,
        min_support=0.2,
        min_confidence=0.5
    )

    print_comparison_summary(comparison_df)
    print(get_winner(apriori_results, eclat_results))

    print("\nSample Rules from Apriori (first 5):")
    print("-" * 70)
    for i, rule in enumerate(apriori_results['rules'][:5], 1):
        antecedent = ", ".join(sorted(rule['antecedent']))
        consequent = ", ".join(sorted(rule['consequent']))
        print(f"{i}. {antecedent} → {consequent}")
        print(f"   Support: {rule['support']:.3f}, Confidence: {rule['confidence']:.3f}, Lift: {rule['lift']:.3f}")

    print("\nSample Rules from Eclat (first 5):")
    print("-" * 70)
    for i, rule in enumerate(eclat_results['rules'][:5], 1):
        antecedent = ", ".join(sorted(rule['antecedent']))
        consequent = ", ".join(sorted(rule['consequent']))
        print(f"{i}. {antecedent} → {consequent}")
        print(f"   Support: {rule['support']:.3f}, Confidence: {rule['confidence']:.3f}, Lift: {rule['lift']:.3f}")


if __name__ == "__main__":
    main()