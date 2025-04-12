import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

class VectorStore:
    """
    A class to create and search a vector store.

    Attributes:
        docs_dir (str): The directory containing the documents.
        documents (list): A list of document contents.
        vectorizer (TfidfVectorizer): The TF-IDF vectorizer.
        tfidf_matrix (csr_matrix): The TF-IDF matrix.
    """

    def __init__(self, docs_dir):
        """
        Initialize the VectorStore.

        Args:
            docs_dir (str): The directory containing the documents.
        """
        self.docs_dir = docs_dir
        self.documents = self.load_documents()
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)

    def load_documents(self):
        """
        Load the documents from the directory.

        Returns:
            list: A list of document contents.
        """
        documents = []
        for root, _, files in os.walk(self.docs_dir):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    documents.append(f.read())
        return documents

    def search(self, query):
        """
        Search the vector store for documents similar to the query.

        Args:
            query (str): The search query.

        Returns:
            list: A list of similar documents.
        """
        query_vec = self.vectorizer.transform([query])
        cosine_similarities = linear_kernel(query_vec, self.tfidf_matrix).flatten()
        related_docs_indices = cosine_similarities.argsort()[:-11:-1]
        return [self.documents[i] for i in related_docs_indices]