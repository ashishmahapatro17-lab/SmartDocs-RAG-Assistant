import hashlib
from io import BytesIO

import chromadb
from google import genai
from google.genai import types
from pypdf import PdfReader

from smartdocs.chunking import split_text
from smartdocs.schemas import AnswerResponse

DB_PATH = "chroma_db"
COLLECTION_NAME = "smartdocs_documents"
EMBEDDING_MODEL = "gemini-embedding-001"
GENERATION_MODEL = "gemini-2.5-flash"


def _client(api_key: str):
    return genai.Client(api_key=api_key)


def _collection():
    db = chromadb.PersistentClient(path=DB_PATH)
    return db.get_or_create_collection(name=COLLECTION_NAME)


def extract_pdf_pages(pdf_bytes: bytes) -> list[tuple[int, str]]:
    reader = PdfReader(BytesIO(pdf_bytes))
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append((page_number, text))
    return pages


def _embed_text(client, text: str, task_type: str) -> list[float]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type),
    )
    return response.embeddings[0].values


def index_pdf(pdf_bytes: bytes, file_name: str, api_key: str) -> int:
    pages = extract_pdf_pages(pdf_bytes)
    if not pages:
        raise ValueError("No selectable text was found. Scanned PDFs are not supported in this simple version.")

    client = _client(api_key)
    collection = _collection()
    documents, metadatas, ids, embeddings = [], [], [], []

    for page_number, page_text in pages:
        for chunk_number, chunk in enumerate(split_text(page_text)):
            chunk_id = hashlib.sha256(
                f"{file_name}:{page_number}:{chunk_number}:{chunk}".encode("utf-8")
            ).hexdigest()[:24]
            documents.append(chunk)
            metadatas.append({"file_name": file_name, "page": page_number})
            ids.append(chunk_id)
            embeddings.append(_embed_text(client, chunk, "RETRIEVAL_DOCUMENT"))

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    return len(documents)


def answer_question(question: str, api_key: str, top_k: int = 4) -> tuple[AnswerResponse, list[dict]]:
    client = _client(api_key)
    collection = _collection()

    if collection.count() == 0:
        raise ValueError("Please process at least one PDF before asking a question.")

    query_embedding = _embed_text(client, question, "RETRIEVAL_QUERY")
    matches = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas"],
    )
    docs = matches.get("documents", [[]])[0]
    metadata = matches.get("metadatas", [[]])[0]
    if not docs:
        raise ValueError("No relevant passages were found.")

    context = "\n\n".join(
        f"[{i}] File: {meta['file_name']}, Page: {meta['page']}\n{doc}"
        for i, (doc, meta) in enumerate(zip(docs, metadata), start=1)
    )
    prompt = f"""
You are a document question-answering assistant.
Use only the supplied context. If the answer is not present, say:
"I could not find that information in the uploaded documents."
Do not use outside knowledge.
Return source_ids as the numbers of the passages that support your answer.

CONTEXT:
{context}

QUESTION:
{question}
"""
    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AnswerResponse,
            temperature=0.2,
        ),
    )
    parsed = AnswerResponse.model_validate_json(response.text)

    valid_ids = {str(i) for i in range(1, len(docs) + 1)}
    source_ids = [sid for sid in parsed.source_ids if sid in valid_ids]
    sources = []
    for sid in source_ids:
        meta = metadata[int(sid) - 1]
        item = {"file_name": meta["file_name"], "page": meta["page"]}
        if item not in sources:
            sources.append(item)

    # Fallback: display retrieved pages if the model did not return valid source IDs.
    if not sources:
        for meta in metadata:
            item = {"file_name": meta["file_name"], "page": meta["page"]}
            if item not in sources:
                sources.append(item)

    return AnswerResponse(answer=parsed.answer, source_ids=source_ids), sources
