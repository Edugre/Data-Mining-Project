import pandas as pd
import sys
from pathlib import Path
from association_rules import generate_rules

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.preprocessing.preprocessing_utils import load_transactions

transaction_path = project_root / "data" / "cleaned_transactions.csv"

def build_vertical_format(transactions):
    vertical = {}

    for transaction in transactions:
        items = transaction['items']
        tid = transaction['transaction_id']
        
        for item in items:
            if item not in vertical:
                vertical[item] = set()
            vertical[item].add(tid)

    return vertical

def eclat_recursive(prefix, items, total_transactions, results, min_support=0.2):
    while items:
        item, tidset = items.pop()
        new_itemset = prefix.union([item])
        support = len(tidset) / total_transactions

        if support >= min_support:
            results[new_itemset] = support

            new_items = []
            for other_item, other_tidset in items:
                intersection = tidset.intersection(other_tidset)
                if intersection:
                    new_items.append((other_item, intersection))

            eclat_recursive(new_itemset, new_items, total_transactions, results, min_support)

def eclat(transactions, min_support=0.2): 
    vertical = build_vertical_format(transactions)
    total_transactions = len(transactions)

    items = [(item, vertical[item]) for item in vertical]

    results = {}

    eclat_recursive(frozenset(), items, total_transactions, results, min_support)

    levels = {}
    for itemset, support in results.items():
        k = len(itemset)
        if k not in levels:
            levels[k] = {}
        levels[k][itemset] = support
    
    sorted_levels = []
    for k in sorted(levels.keys()):
        sorted_levels.append(levels[k])

    return sorted_levels

def main():
    transactions = load_transactions(transaction_path)
    result = eclat(transactions, min_support=0.2)
    rules = generate_rules(result)

    print(rules)

if __name__ == "__main__":
    main()