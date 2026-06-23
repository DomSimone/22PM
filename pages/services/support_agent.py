"""
22PM — Support Agent Service
================================
RAG-powered customer support chatbot. Uses ChromaDB (free, self-hosted)
for vector storage and Gemini/Groq for responses.

API Endpoints:
    POST /api/support/train       — Train chatbot on knowledge base
    POST /api/support/ask         — Ask a question to the chatbot
    POST /api/support/query       — Query with conversation history
    GET  /api/support/status      — Check chatbot status
"""

import os
import json
import logging
import hashlib
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

from llm import llm

logger = logging.getLogger("22pm.support_agent")

# Try to import vector DB — fallback to simple search if unavailable
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False
    logger.warning("ChromaDB not installed. Using keyword fallback search.")


# ===== Models =====

class Document(BaseModel):
    content: str = Field(..., min_length=10)
    source: str = ""
    metadata: dict = {}

class TrainRequest(BaseModel):
    documents: list[Document]
    collection_name: str = "22pm_knowledge_base"
    clear_existing: bool = False

class TrainResponse(BaseModel):
    status: str
    documents_indexed: int
    collection_name: str
    cost: str = "$0 (free tier - ChromaDB self-hosted)"

class AskRequest(BaseModel):
    query: str = Field(..., min_length=2)
    collection_name: str = "22pm_knowledge_base"
    conversation_history: list[dict] = []
    top_k: int = 3

class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: str
    provider_used: str
    cost: str = "$0 (free tier)"

class StatusResponse(BaseModel):
    collection_name: str
    document_count: int
    provider: str = "Gemini + Groq (auto-fallback)"
    vector_db: str = "ChromaDB" if HAS_CHROMA else "Keyword Fallback"
    status: str = "ready"


# ===== System Prompts =====

SYSTEM_PROMPT_TEMPLATE = """You are a customer support agent for {company}.
Answer using ONLY the provided context. Follow these rules strictly:

1. Answer ONLY based on the context provided below
2. If the answer isn't in the context, say: "I'll connect you with a human specialist"
3. Be polite, concise, and professional
4. Never make up information or speculate
5. Always end with: "Is there anything else I can help with?"

Context:
{context}
"""


# ===== Vector Store =====

class VectorStore:
    """ChromaDB-based vector store with free fallback."""

    def __init__(self, persist_dir: str = "./chroma_data"):
        self.persist_dir = persist_dir
        self._client = None
        self._collections = {}

        if HAS_CHROMA:
            try:
                os.makedirs(persist_dir, exist_ok=True)
                self._client = chromadb.Client(ChromaSettings(
                    persist_directory=persist_dir,
                    anonymized_telemetry=False
                ))
                logger.info(f"ChromaDB initialized at {persist_dir}")
            except Exception as e:
                logger.warning(f"ChromaDB init failed: {e}. Using fallback.")

    def _get_collection(self, name: str):
        """Get or create a collection."""
        if name in self._collections:
            return self._collections[name]

        if self._client:
            try:
                col = self._client.get_or_create_collection(name=name)
                self._collections[name] = col
                return col
            except Exception:
                pass
        return None

    def index_documents(self, documents: list[Document], collection_name: str,
                        clear: bool = False) -> int:
        """Index documents for search."""
        if not HAS_CHROMA:
            # Fallback: store in memory dict
            store = self._collections.get(collection_name)
            if store is None or clear:
                store = {}
            for doc in documents:
                key = hashlib.md5(doc.content.encode()).hexdigest()
                store[key] = doc
            self._collections[collection_name] = store
            return len(documents)

        col = self._get_collection(collection_name)
        if not col:
            return 0

        if clear:
            try:
                self._client.delete_collection(collection_name)
                col = self._client.create_collection(name=collection_name)
                self._collections[collection_name] = col
            except Exception:
                pass

        ids = []
        texts = []
        metadatas = []

        for doc in documents:
            doc_id = hashlib.md5(doc.content.encode()).hexdigest()[:16]
            ids.append(doc_id)
            texts.append(doc.content)
            metadatas.append({
                "source": doc.source or "unknown",
                **doc.metadata
            })

        # Add in batches of 100
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_end = min(i + batch_size, len(texts))
            col.add(
                ids=ids[i:batch_end],
                documents=texts[i:batch_end],
                metadatas=metadatas[i:batch_end]
            )

        return len(documents)

    def search(self, query: str, collection_name: str, top_k: int = 3) -> list[tuple[str, str, float]]:
        """Search for relevant documents."""
        store = self._collections.get(collection_name)
        if store is None:
            return []

        if not HAS_CHROMA:
            # Keyword fallback search
            query_lower = query.lower()
            query_words = query_lower.split()
            scored = []

            for key, doc in store.items():
                content_lower = doc.content.lower()
                score = sum(1 for word in query_words if word in content_lower)
                if score > 0:
                    scored.append((doc.content, doc.source, score))

            scored.sort(key=lambda x: x[2], reverse=True)
            return [(c, s, sc) for c, s, sc in scored[:top_k]]

        # ChromaDB search
        try:
            results = store.query(
                query_texts=[query],
                n_results=min(top_k, 10)
            )
            
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            return [
                (doc, meta.get("source", "unknown"), 1.0 - dist)
                for doc, meta, dist in zip(documents, metadatas, distances)
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def count_documents(self, collection_name: str) -> int:
        """Count documents in collection."""
        store = self._collections.get(collection_name)
        if store is None:
            return 0
        if isinstance(store, dict):
            return len(store)
        try:
            return store.count()
        except Exception:
            return 0


# ===== Service =====

class SupportAgentService:
    """RAG-powered customer support chatbot."""

    def __init__(self):
        self.vector_store = VectorStore()
        self.company_name = "22PM Client"

    async def train(self, request: TrainRequest) -> TrainResponse:
        """Index documents into the vector store."""
        count = self.vector_store.index_documents(
            request.documents,
            request.collection_name,
            request.clear_existing
        )
        
        return TrainResponse(
            status="success",
            documents_indexed=count,
            collection_name=request.collection_name
        )

    async def ask(self, request: AskRequest) -> AskResponse:
        """Answer a query using RAG."""
        # 1. Search for relevant context
        results = self.vector_store.search(
            request.query,
            request.collection_name,
            request.top_k
        )

        if not results:
            return AskResponse(
                answer="I'll connect you with a human specialist. I don't have enough information to answer that question.",
                sources=[],
                confidence="low",
                provider_used="gemini/groq (auto-fallback)"
            )

        # 2. Build context from search results
        context_parts = []
        sources = []
        for content, source, score in results:
            context_parts.append(f"[Source: {source}]\n{content}")
            if source not in sources:
                sources.append(source)

        context = "\n\n".join(context_parts)

        # 3. Build conversation history
        history_text = ""
        for msg in request.conversation_history[-4:]:  # Last 4 messages
            role = msg.get("role", "user")
            text = msg.get("content", "")
            history_text += f"{role}: {text}\n"

        # 4. Generate response
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            company=self.company_name,
            context=context
        )

        full_prompt = f"""
Conversation history:
{history_text}

Current question: {request.query}

Answer using only the provided context above. If unsure, say you'll connect to a human.
"""
        result = await llm.generate(full_prompt, system_prompt, temperature=0.3, max_tokens=512)

        # 5. Determine confidence
        confidence = "high"
        if "human specialist" in result.text.lower() or "don't have" in result.text.lower():
            confidence = "low"

        return AskResponse(
            answer=result.text,
            sources=sources,
            confidence=confidence,
            provider_used=f"{result.provider}/{result.model}"
        )

    async def status(self, collection_name: str = "22pm_knowledge_base") -> StatusResponse:
        """Get chatbot status."""
        count = self.vector_store.count_documents(collection_name)
        return StatusResponse(
            collection_name=collection_name,
            document_count=count
        )