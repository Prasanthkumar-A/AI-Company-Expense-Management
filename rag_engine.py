
import os
import chromadb
import ollama

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# ------------------------------------------------
# 1. CONFIGURATION
# ------------------------------------------------

MODEL_NAME = "llama3.2"

DATABASE_PATH = "chroma_db"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Load the embedding model
embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

# Connect to persistent ChromaDB
client = chromadb.PersistentClient(
    path=DATABASE_PATH
)

# Create or access the document collection
collection = client.get_or_create_collection(
    name="company_documents"
)


# ------------------------------------------------
# 2. EXTRACT TEXT FROM PDF
# ------------------------------------------------

def extract_pdf_text(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page_number, page in enumerate(reader.pages):

        page_text = page.extract_text()

        if page_text:
            text += f"\n[Page {page_number + 1}]\n"
            text += page_text

    return text


# ------------------------------------------------
# 3. EXTRACT TEXT FROM TXT
# ------------------------------------------------

def extract_txt_text(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ------------------------------------------------
# 4. SPLIT TEXT INTO CHUNKS
# ------------------------------------------------

def split_into_chunks(
    text,
    chunk_size=500,
    overlap=80
):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ------------------------------------------------
# 5. PROCESS AND STORE DOCUMENTS
# ------------------------------------------------

def process_document(file_path):

    filename = os.path.basename(file_path)

    extension = os.path.splitext(filename)[1].lower()

    if extension == ".pdf":

        text = extract_pdf_text(file_path)

    elif extension == ".txt":

        text = extract_txt_text(file_path)

    else:

        raise ValueError(
            "Only PDF and TXT files are supported."
        )

    if not text.strip():

        raise ValueError(
            "No readable text found in this document. "
            "Scanned PDFs need OCR before indexing."
        )

    chunks = split_into_chunks(text)

    # Remove old chunks for this filename
    collection.delete(
        where={"source": filename}
    )

    embeddings = embedding_model.encode(
        chunks,
        normalize_embeddings=True
    ).tolist()

    ids = [
        f"{filename}_{index}"
        for index in range(len(chunks))
    ]

    metadatas = [
        {
            "source": filename,
            "chunk": index + 1
        }
        for index in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)


# ------------------------------------------------
# 6. SEARCH RELEVANT DOCUMENT CHUNKS
# ------------------------------------------------

def retrieve_documents(question, top_k=4):

    if collection.count() == 0:

        return []

    query_embedding = embedding_model.encode(
        [question],
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count())
    )

    documents = results.get("documents", [[]])[0]

    metadatas = results.get("metadatas", [[]])[0]

    retrieved = []

    for document, metadata in zip(
        documents,
        metadatas
    ):

        retrieved.append({
            "text": document,
            "source": metadata.get("source", "Unknown"),
            "chunk": metadata.get("chunk", "Unknown")
        })

    return retrieved


# ------------------------------------------------
# 7. GENERATE ANSWER USING OLLAMA
# ------------------------------------------------


def ask_ai(question, expense_data=None):

    # -----------------------------------
    # 1. Retrieve relevant company documents
    # -----------------------------------

    retrieved = retrieve_documents(question)

    context = ""

    if retrieved:

        context = "\n\n".join([
            (
                f"Source: {item['source']}\n"
                f"{item['text']}"
            )
            for item in retrieved
        ])

    else:

        context = "No relevant company document was found."

    # -----------------------------------
    # 2. Prepare expense database context
    # -----------------------------------

    expense_context = "No expense database information supplied."

    if expense_data is not None and not expense_data.empty:

        expense_context = expense_data.to_string(
            index=False
        )

    # -----------------------------------
    # 3. Create intelligent AI prompt
    # -----------------------------------

    prompt = f"""
You are an intelligent AI assistant for a company
expense management and analysis system.

You can answer three types of questions:

1. COMPANY POLICY QUESTIONS
Use the retrieved company documents.

2. COMPANY EXPENSE QUESTIONS
Use the supplied expense database information.

3. GENERAL QUESTIONS
Answer using your general knowledge.

IMPORTANT RULES:

- Understand what the user is asking.
- Answer in simple and clear language.
- Do not invent company financial records.
- Do not invent company policies.
- If a company policy is missing, clearly mention that.
- If company expense data is unavailable, say so.
- For general knowledge questions, provide a useful answer.
- Do not force every question to be about expenses.
- Distinguish actual records from hypothetical examples.

COMPANY DOCUMENT CONTEXT:

{context}

COMPANY EXPENSE DATABASE:

{expense_context}

USER QUESTION:

{question}

Provide the most useful answer.
"""

    # -----------------------------------
    # 4. Generate answer using Ollama
    # -----------------------------------

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response["message"]["content"]

    return answer, retrieved


# ------------------------------------------------
# 8. GET INDEXED DOCUMENT COUNT
# ------------------------------------------------

def get_document_count():

    return collection.count()
