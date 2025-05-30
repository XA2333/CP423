import re
from collections import defaultdict

# Load the inverted index from file
def load_inverted_index(filepath):
    index = defaultdict(set)
    all_docs = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            term, doc_list = line.strip().split(':', 1)
            docs = set(map(str.strip, doc_list.split(',')))
            index[term] = docs
            all_docs.update(docs)
    return index, all_docs

# Preprocess user query
def preprocess_query(query):
    return query.lower()

# Evaluate Boolean expression
def evaluate_query(query, index, all_docs):
    """
    Supports:
    - AND
    - OR
    - NOT
    Query must be space-separated, e.g., 'canada AND NOT ontario'
    """
    tokens = query.strip().split()
    result_stack = []
    operator_stack = []

    def apply_operator(op, right, left=None):
        if op == 'AND':
            return left & right
        elif op == 'OR':
            return left | right
        elif op == 'NOT':
            return all_docs - right
        else:
            raise ValueError(f"Unsupported operator: {op}")

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.upper() in {'AND', 'OR'}:
            operator_stack.append(token.upper())
        elif token.upper() == 'NOT':
            i += 1
            term = tokens[i]
            right = index.get(term, set())
            result_stack.append(apply_operator('NOT', right))
        else:
            result_stack.append(index.get(token, set()))
        i += 1

    # Left-associative processing
    result = result_stack[0]
    for j in range(len(operator_stack)):
        op = operator_stack[j]
        right = result_stack[j + 1]
        result = apply_operator(op, right, result)

    return result

if __name__ == "__main__":
    # Load the inverted index
    index, all_docs = load_inverted_index("inverted_index.txt")

    # Loop to take user queries
    print("Boolean Search Engine (type 'exit' to quit)")
    while True:
        query = input("\nEnter your query (e.g., canada AND NOT ontario): ").strip()
        if query.lower() == 'exit':
            break

        query = preprocess_query(query)
        try:
            result_docs = evaluate_query(query, index, all_docs)
            print(f"\nMatched {len(result_docs)} documents:")
            for doc in sorted(result_docs):
                print(f" - {doc}")
        except Exception as e:
            print(f"Error: {e}")
