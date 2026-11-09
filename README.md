# SmartDocs RAG Assistant

A PDF question-answering application built with Python, Streamlit, Gemini, and ChromaDB. It uses Retrieval-Augmented Generation (RAG) to retrieve relevant passages from uploaded PDFs and provide context-based answers with source-page references.

## Features
- Upload PDF documents through a Streamlit interface.
- Extract selectable text from PDF pages using pypdf.
- Split extracted text into overlapping chunks.
- Generate document and query embeddings with Google's Gemini embedding model.
- Store and search embeddings locally using ChromaDB.
- Retrieve the top relevant passages and use them as context for Gemini answer generation.
- Validate the response structure with Pydantic and display source references.

## Tech Stack
- Python
- Streamlit
- pypdf
- Google Gemini API (google-genai)
- ChromaDB
- Pydantic
- Pytest

## Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```
4. Enter your Gemini API key in the application's API-key field when prompted.

## Tests
Run:
```bash
pytest
``

The current test suite covers text chunking and response-schema validation. It is not an end-to-end evaluation of retrieval quality or answer factuality.

## Notes and Limitations
- PDF extraction uses selectable text; scanned/image-only PDFs require OCR and are not handled by the current implementation.
- Chunking is character-based, not token-based.
- The application relies on Gemini API availability and network access.
- Source references indicate retrieved pages; they do not independently guarantee that every generated claim is fully supported.
- This is a local project and does not include cloud deployment or Docker configuration.

## Security
- Do not commit API keys or real `.env` files.
- Use `.env.example` only as a configuration reference.
- Keep API keys private and rotate them if they are accidentally exposed.

## License
No license has been specified yet. Contact the repository owner before reusing or redistributing this project.
