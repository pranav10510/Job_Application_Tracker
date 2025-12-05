"""
Lightweight RAG Engine for Job Application Tracker
Uses TF-IDF vectorization (scikit-learn) instead of neural embeddings
Fast, reliable, and works without PyTorch/GPU dependencies
"""

import pickle
import os
from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import (
    CHROMA_DB_PATH,
    TOP_K_RESULTS,
    SIMILARITY_THRESHOLD
)

class RAGEngine:
    """
    Lightweight RAG using TF-IDF vectorization for semantic search
    """

    def __init__(self):
        """Initialize TF-IDF vectorizer and storage"""

        print("Initializing Lightweight RAG Engine (TF-IDF)...")

        # TF-IDF vectorizer with optimized parameters
        self.vectorizer = TfidfVectorizer(
            max_features=5000,      # Limit vocabulary size
            ngram_range=(1, 3),     # Use unigrams, bigrams, and trigrams
            stop_words='english',   # Remove common words
            min_df=1,               # Minimum document frequency
            sublinear_tf=True       # Use log scaling for term frequency
        )

        # Storage for documents and metadata
        self.documents = {}      # {app_id: searchable_text}
        self.metadatas = {}      # {app_id: metadata_dict}
        self.doc_vectors = None  # TF-IDF matrix
        self.app_ids = []        # List of app IDs in order

        # Create storage directory
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        self.storage_file = os.path.join(CHROMA_DB_PATH, 'tfidf_rag.pkl')

        # Load existing data if available
        self._load_from_disk()

        print(f"✓ RAG Engine initialized. Applications in index: {len(self.documents)}")

    def _load_from_disk(self):
        """Load saved RAG data from disk"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', {})
                    self.metadatas = data.get('metadatas', {})
                    self.vectorizer = data.get('vectorizer', self.vectorizer)
                    self.app_ids = data.get('app_ids', [])

                    # Rebuild vectors
                    if self.documents:
                        texts = [self.documents[aid] for aid in self.app_ids]
                        self.doc_vectors = self.vectorizer.transform(texts)

                print(f"✓ Loaded {len(self.documents)} applications from disk")
            except Exception as e:
                print(f"⚠️ Error loading RAG data: {e}")
                # Continue with empty storage

    def _save_to_disk(self):
        """Save RAG data to disk"""
        try:
            data = {
                'documents': self.documents,
                'metadatas': self.metadatas,
                'vectorizer': self.vectorizer,
                'app_ids': self.app_ids
            }
            with open(self.storage_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"⚠️ Error saving RAG data: {e}")

    def add_application(self,
                       app_id: str,
                       company: str,
                       position: str,
                       email_subject: str,
                       email_body: str,
                       status: str,
                       notes: str = "") -> None:
        """
        Add a job application to the RAG index

        Args:
            app_id: Unique application ID
            company: Company name
            position: Job position/title
            email_subject: Email subject line
            email_body: Full email text
            status: Application status
            notes: User notes
        """

        # Create searchable text
        searchable_text = f"""
        Company: {company}
        Position: {position}
        Subject: {email_subject}

        Email Content:
        {email_body[:1500]}

        Notes: {notes}
        """.strip()

        # Store document and metadata
        self.documents[str(app_id)] = searchable_text
        self.metadatas[str(app_id)] = {
            "company": company,
            "position": position,
            "status": status,
            "email_subject": email_subject,
            "has_notes": bool(notes)
        }

        # Rebuild index
        self.app_ids = list(self.documents.keys())
        texts = [self.documents[aid] for aid in self.app_ids]

        # Fit vectorizer if first document, otherwise transform
        if len(self.app_ids) == 1:
            self.doc_vectors = self.vectorizer.fit_transform(texts)
        else:
            # Refit with all documents
            self.doc_vectors = self.vectorizer.fit_transform(texts)

        # Save to disk
        self._save_to_disk()

        print(f"✓ Added to RAG: {company} - {position} (Total: {len(self.documents)})")

    def search_similar_applications(self,
                                   query_text: str,
                                   status_filter: Optional[str] = None,
                                   exclude_id: Optional[str] = None,
                                   top_k: int = TOP_K_RESULTS) -> List[Dict]:
        """
        Search for similar applications using TF-IDF cosine similarity

        Args:
            query_text: Text to search for
            status_filter: Optional filter by status
            exclude_id: Don't return this application ID
            top_k: Number of results to return

        Returns:
            List of similar applications with metadata and similarity scores
        """

        if not self.documents or self.doc_vectors is None:
            return []

        # Vectorize query
        query_vector = self.vectorizer.transform([query_text])

        # Calculate cosine similarities
        similarities = cosine_similarity(query_vector, self.doc_vectors)[0]

        # Get indices sorted by similarity (highest first)
        sorted_indices = np.argsort(similarities)[::-1]

        # Build results
        results = []
        for idx in sorted_indices:
            app_id = self.app_ids[idx]
            similarity = similarities[idx]

            # Skip if below threshold
            if similarity < SIMILARITY_THRESHOLD:
                continue

            # Skip if excluded
            if exclude_id and str(app_id) == str(exclude_id):
                continue

            # Apply status filter
            metadata = self.metadatas[app_id]
            if status_filter and metadata['status'] != status_filter:
                continue

            results.append({
                'id': app_id,
                'document': self.documents[app_id],
                'metadata': metadata,
                'similarity': round(float(similarity), 3)
            })

            # Stop when we have enough results
            if len(results) >= top_k:
                break

        return results

    def build_rag_context(self, similar_apps: List[Dict]) -> str:
        """
        Format similar applications into context for LLM prompt

        Args:
            similar_apps: List of similar applications from search

        Returns:
            Formatted string for prompt injection
        """
        if not similar_apps:
            return "No similar past applications found."

        context_parts = ["=== SIMILAR PAST APPLICATIONS ===\n"]

        for i, app in enumerate(similar_apps, 1):
            metadata = app['metadata']
            similarity = app['similarity']

            context_parts.append(f"""
Application #{i} (Similarity: {similarity*100:.1f}%)
Company: {metadata['company']}
Position: {metadata['position']}
Status: {metadata['status']}

Key Details:
{app['document'][:300]}...
---
""")

        return "\n".join(context_parts)

    def get_collection_stats(self) -> Dict:
        """Get statistics about the RAG index"""
        return {
            "total_applications": len(self.documents),
            "vectorizer": "TF-IDF (scikit-learn)",
            "vocabulary_size": len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, 'vocabulary_') else 0,
            "storage_file": self.storage_file
        }


# Singleton instance
_rag_engine = None

def get_rag_engine() -> RAGEngine:
    """Get or create RAG engine singleton"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
