import os
import logging
import json
from typing import List, Dict

logger = logging.getLogger(__name__)

# Attempt to import chromadb, handle potential compatibility issues with newer Python versions
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except Exception as e:
    logger.warning(f"ChromaDB not available or incompatible (likely Pydantic V1 issue on Python 3.14+): {e}")
    CHROMA_AVAILABLE = False

class RAGService:
    def __init__(self):
        self.persist_directory = "app/data/chroma"
        self.fallback_storage = []
        
        if CHROMA_AVAILABLE:
            try:
                if not os.path.exists(self.persist_directory):
                    os.makedirs(self.persist_directory)
                self.client = chromadb.PersistentClient(path=self.persist_directory)
                self.collection = self.client.get_or_create_collection(name="scan_reports")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}. Falling back to in-memory storage.")
                self.collection = None
        else:
            self.collection = None

    def index_report(self, report_id: str, vulnerabilities: List[Dict]):
        """Converts vulnerability results into documents and embeds them."""
        documents = []
        metadatas = []
        ids = []

        for i, v in enumerate(vulnerabilities):
            doc = (
                f"Target: {v['target']}\n"
                f"CVE: {v['cve_id']}\n"
                f"Severity: {v['severity']}\n"
                f"Description: {v['description']}\n"
                f"Component: {v['component']}\n"
                f"Evidence: {v['evidence']}"
            )
            documents.append(doc)
            metadatas.append({"report_id": report_id, "cve": v['cve_id']})
            ids.append(f"{report_id}_{i}")

        if self.collection:
            try:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                return True
            except Exception as e:
                logger.error(f"Error indexing to ChromaDB: {e}")

        # Fallback storage for MVP
        for doc, meta in zip(documents, metadatas):
            self.fallback_storage.append({"content": doc, "metadata": meta})
        return True

    def query(self, question: str, report_id: str = None):
        """Retrieves context and prepares RAG prompt."""
        context = ""
        
        if self.collection:
            try:
                where_filter = {"report_id": report_id} if report_id else None
                results = self.collection.query(
                    query_texts=[question],
                    n_results=3,
                    where=where_filter
                )
                if results['documents']:
                    context = "\n---\n".join(results['documents'][0])
            except Exception as e:
                logger.error(f"Error querying ChromaDB: {e}")

        if not context and self.fallback_storage:
            # Simple keyword search fallback
            keywords = question.lower().split()
            matches = []
            for item in self.fallback_storage:
                if any(kw in item['content'].lower() for kw in keywords):
                    matches.append(item['content'])
            context = "\n---\n".join(matches[:3])
        
        return self._simulate_llm_response(question, context)

    def _simulate_llm_response(self, question: str, context: str):
        if not context:
            return {
                "Summary": "No relevant scan data found.",
                "Attack Explanation": "N/A",
                "Mitigation": "Ensure a scan has been completed.",
                "References": []
            }
            
        return {
            "Summary": f"Based on the scan context, it appears that {question[:50]} relates to the identified infrastructure vulnerabilities.",
            "Attack Explanation": "The detected vulnerabilities allow for potential unauthorized access via the identified service.",
            "Mitigation": "Update the affected components and apply security patches as per CVE recommendations.",
            "References": ["https://nvd.nist.gov/", "https://cve.mitre.org/"]
        }

