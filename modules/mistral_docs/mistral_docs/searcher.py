import os
from .vector_store import VectorStore

DOCS_DIR = os.path.join("./git", "docs")

def search_docs(query, vector_store=None):
    """
    Search the stored documents using both normal search and vector search.

    Args:
        query (str): The search query.
        vector_store (VectorStore, optional): The vector store to use for vector search. Defaults to None.

    Returns:
        list: A list of search results.
    """
    if vector_store is None:
        vector_store = VectorStore(DOCS_DIR)

    vector_results = vector_store.search(query)
    normal_results = normal_search(query, DOCS_DIR)

    # Combine and limit results to 5
    combined_results = vector_results + normal_results
    return combined_results[:3]

def normal_search(query, docs_dir):
    """
    Perform a normal search on the stored documents.

    Args:
        query (str): The search query.
        docs_dir (str): The directory containing the documents.

    Returns:
        list: A list of search results.
    """
    results = []
    for root, _, files in os.walk(docs_dir):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if query.lower() in content.lower():
                    results.append(content)
                    if len(results) >= 3:
                        return results
    return results