import pandas as pd

def load_transactions(csv_path):
    df = pd.read_csv(csv_path)

    df['items'] = df['items'].fillna('').str.split(',')

    return df.to_dict('records')

def load_products_set(csv_path):
    df = pd.read_csv(csv_path)

    return set(df['product_name'].str.strip().str.lower())

def standardize_items(items):
    return [item.strip().lower() for item in items]

def remove_duplicates(items):
    new_items = []
    duplicates_set = set()
    duplicates_count = 0

    for item in items:
        if item in duplicates_set:
            duplicates_count += 1
        else:
            new_items.append(item)
            duplicates_set.add(item)
    
    return new_items, duplicates_count

def remove_invalid(items, products_set):
    new_items = []
    invalid_count = 0

    for item in items:
        if item in products_set:
            new_items.append(item)
        else:
            invalid_count += 1

    return new_items, invalid_count


def clean_transaction(items, products_set):
    stats = {}
    new_items = standardize_items(items)
    new_items, duplicates_count = remove_duplicates(new_items)
    new_items, invalid_count = remove_invalid(new_items, products_set)

    stats["duplicates"] = duplicates_count
    stats["invalid"] = invalid_count

    return new_items, stats, set(new_items)

def preprocess_transactions(transactions, products):
    processed_transactions = []
    uniques_set = set()

    stats = {
        "first_total": len(transactions),
        "empty": 0,
        "single": 0,
        "duplicates": 0,
        "invalid": 0,
        "total_items": 0
    }

    for transaction in transactions:

        new_transaction, transaction_stats, unique_items = clean_transaction(transaction["items"], products)

        if len(new_transaction) <= 0:
            stats["empty"] += 1
        elif len(new_transaction) == 1:
            stats["single"] += 1
        else:
            processed_transactions.append({"transaction_id": transaction["transaction_id"], "items": new_transaction})
            stats["total_items"] += len(new_transaction)
            uniques_set |= unique_items

        stats["duplicates"] += transaction_stats["duplicates"]
        stats["invalid"] += transaction_stats["invalid"] 
    
    stats["uniques"] = len(uniques_set)
    stats["valid_transactions"] = len(processed_transactions)

    return processed_transactions, stats

def save_to_csv(transactions, path):
    df = pd.DataFrame(transactions)

    df["items"] = df["items"].apply(lambda lst: ",".join(lst))
    
    df.to_csv(path, index=False)

def main():
    transactions_path = "data/sample_transactions.csv"
    products_path = "data/products.csv"

    df = load_transactions(transactions_path)

    products = load_products_set(products_path)

    transactions, stats = preprocess_transactions(df, products)

    print("Preprocessing Report:\n" \
    "----------------------\n" \
    f"- Total transactions: {stats['first_total']}\n" \
    f"- Empty transactions: {stats['empty']}\n" \
    f"- Single-item transactions: {stats['single']}\n" \
    f"- Duplicate items found: {stats['duplicates']} instances\n" \
    f"- Invalid items found: {stats['invalid']} instances\n" \
    "\nAfter Cleaning:\n" \
    f"- Valid transactions: {stats['valid_transactions']}\n" \
    f"- Total items: {stats['total_items']}\n" \
    f"- Unique products: {stats['uniques']}\n")

    save_to_csv(transactions, "data/cleaned_transactions.csv")

if __name__ == "__main__":
    main()