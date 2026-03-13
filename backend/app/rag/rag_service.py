import os
import logging
import json
import requests
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
        context_docs = []
        is_general_query = any(word in question.lower() for word in ["all", "summarize", "list", "explain everything", "overview"])
        
        if self.collection:
            try:
                where_filter = {"report_id": report_id} if report_id else None
                # If general query, just fetch the first few documents for the report
                if is_general_query and report_id:
                    results = self.collection.get(where=where_filter, limit=5)
                    if results['documents']:
                        context_docs = results['documents']
                else:
                    results = self.collection.query(
                        query_texts=[question],
                        n_results=3,
                        where=where_filter
                    )
                    if results['documents'] and results['documents'][0]:
                        context_docs = results['documents'][0]
            except Exception as e:
                logger.error(f"Error querying ChromaDB: {e}")

        if not context_docs and self.fallback_storage:
            # Simple keyword search fallback
            keywords = question.lower().split()
            
            # Filter fallback storage by report_id if provided
            report_docs = [item for item in self.fallback_storage if not report_id or item['metadata']['report_id'] == report_id]
            
            if is_general_query and report_id:
                context_docs = [item['content'] for item in report_docs[:5]]
            else:
                matches = []
                for item in report_docs:
                    if any(kw in item['content'].lower() for kw in keywords):
                        matches.append(item['content'])
                context_docs = matches[:3]
        
        # Final fallback: if no matches but we have a report_id, just give them some data
        if not context_docs and report_id:
            report_docs = [item for item in self.fallback_storage if item['metadata']['report_id'] == report_id]
            context_docs = [item['content'] for item in report_docs[:3]]

        context = "\n---\n".join(context_docs)
        return self._call_ollama(question, context)

    def _call_ollama(self, question: str, context: str):
        """Calls local Ollama instance for real intelligence generation."""
        try:
            url = "http://localhost:11434/api/generate"
            
            prompt = f"""
            You are VulnSight Neural Core, an advanced cybersecurity intelligence AI.
            Based on the following security scan context, answer the user's question.
            
            CONTEXT:
            {context}
            
            USER QUESTION:
            {question}
            
            INSTRUCTIONS:
            1. Analyze the context carefully.
            2. Provide a high-fidelity summary of findings.
            3. Explain potential attack vectors based on the findings.
            4. Provide specific, actionable mitigation steps.
            5. If context is missing, use your general security knowledge but acknowledge the lack of specific scan data.
            6. Return ONLY a valid JSON object with the following keys:
               "Summary": A concise summary of the situation.
               "Attack Explanation": How an attacker would exploit these findings.
               "Mitigation": Step-by-step remediation advice.
               "References": A list of relevant security URLs (CVEs, OWASP, etc).
            
            JSON ONLY RESPONSE:
            """
            
            response = requests.post(url, json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return json.loads(result.get("response", "{}"))
            else:
                raise Exception(f"Ollama returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Ollama Error: {e}")
            return {
                "Summary": "Communication break in Neural Core.",
                "Attack Explanation": f"The intelligence bridge failed to establish a connection with the local LLM: {str(e)}",
                "Mitigation": "Ensure Ollama is running (`ollama serve`) and the 'llama3.2' model is pulled.",
                "References": ["https://ollama.ai/"]
            }

