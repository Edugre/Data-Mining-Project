import pandas as pd
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.preprocessing.preprocessing_utils import load_transactions

transaction_path = "data/cleaned_transactions.csv"

# Extract the lists of items from the transactions dictionary 
def get_items_list(transactions):
    items_list = []

    for transaction in transactions:
        items_list.append(transaction['items'])

    return items_list

# Generate frequent 1-itemsets
def generate_L1(transactions, min_support=0.2):
    item_count = {}
    L1 = {}

    for transaction in transactions:
        for item in transaction:
            item_count[item] = item_count.get(item, 0) + 1

    for item, count in item_count.items():
         support = count / len(transactions)

         if support >= min_support:
             L1[frozenset({item})] = support

    return L1

# Generate candidate k-itemsets
def generate_Ck(L_prev, k):
    candidates = set()
    L_prev_list = list(L_prev.keys())

    for i in range(len(L_prev_list)):
        for j in range(i + 1, len(L_prev_list)):
            itemsetA = L_prev_list[i]
            itemsetB = L_prev_list[j]
            union = itemsetA.union(itemsetB)

            if len(union) == k:
                candidates.add(union)

    return candidates

# Generate frequent k-itemsets from candidates
def generate_Lk(candidates, transactions, min_support=0.2):

    item_set_count = {cand: 0 for cand in candidates}
    Lk = {}

    for transaction in transactions:
        transaction_set = set(transaction)

        for candidate in candidates:
            if candidate.issubset(transaction_set):
                item_set_count[candidate] = item_set_count[candidate] + 1

    for candidate, count in item_set_count.items():
        support = count / len(transactions)

        if support >= min_support:
            Lk[candidate] = support

    return Lk

# Apriori algorithm 
def apriori(transactions, min_support=0.2):
    L = []

    L1 = generate_L1(transactions, min_support)
    L.append(L1)

    k = 2
    while True:
        L_prev = L[k-2]

        Ck = generate_Ck(L_prev, k)
        Lk = generate_Lk(Ck, transactions)

        if not Lk:
            break

        L.append(Lk)
        k += 1

    return L


def main():
    transactions = load_transactions(transaction_path)
    items_list = get_items_list(transactions)

    frequency_list = apriori(items_list)

    print(frequency_list)



if __name__ == "__main__":
    main()