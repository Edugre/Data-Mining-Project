from itertools import combinations

# Generate subsets from itemset
def get_subsets(itemset):
    subsets_list = []

    for r in range(1, len(itemset)):
        for combo in combinations(itemset, r):
            subset = frozenset(combo)
            subsets_list.append(subset)

    return subsets_list

# Compute confidence A -> B
def compute_confidence(A, B, support_lookup):
    union_itemset = A.union(B)

    support_union = support_lookup.get(union_itemset, 0)
    support_A = support_lookup.get(A, 0)

    if support_A == 0:
        return 0
    
    return support_union / support_A

# Compute lift A -> B
def compute_lift(A, B, support_lookup):
    union_itemset = A.union(B)

    support_union = support_lookup.get(union_itemset, 0)
    support_A = support_lookup.get(A, 0)
    support_B = support_lookup.get(B, 0)

    if support_A == 0 or support_B == 0:
        return 0
    
    return support_union / (support_A * support_B)

# Generate association rules
def generate_rules(frequent_itemsets, min_confidence=0.5):
    support_lookup = {}
    for Lk in frequent_itemsets:
        support_lookup.update(Lk)

    rules = []

    for Lk in frequent_itemsets:
        for itemset in Lk:
            if len(itemset) < 2:
                continue

            subsets = get_subsets(itemset)

            for A in subsets:
                B = itemset - A
                
                confidence = compute_confidence(A, B, support_lookup)

                if confidence >= min_confidence:

                    lift = compute_lift(A, B, support_lookup)

                    rules.append({
                        'antecedent': A,
                        'consequent': B,
                        'support': support_lookup[itemset],
                        'confidence': confidence,
                        'lift': lift
                    })
    
    return rules