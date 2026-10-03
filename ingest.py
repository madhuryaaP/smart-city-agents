import os
import chromadb
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")


# --------------------------------------------------
# 2. LOAD EMBEDDING MODEL
# --------------------------------------------------

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded.")


# --------------------------------------------------
# 3. CONNECT TO CHROMADB
# --------------------------------------------------

print("Connecting to ChromaDB...")

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)


# --------------------------------------------------
# 4. RECREATE COLLECTION
# --------------------------------------------------

try:

    client.delete_collection(
        name="smart_city_knowledge"
    )

    print("Old collection deleted.")

except Exception:

    print("No previous collection found.")


collection = client.create_collection(
    name="smart_city_knowledge"
)

print("New ChromaDB collection created.")


# --------------------------------------------------
# 5. CHUNKING FUNCTION
# --------------------------------------------------

def create_chunks(text):
    """
    Create small, focused knowledge chunks.

    Each paragraph is treated as a separate
    knowledge unit.

    Very small consecutive paragraphs are combined
    so that individual bullet points do not become
    uselessly tiny chunks.
    """

    # --------------------------------------------------
    # Split using blank lines
    # --------------------------------------------------

    paragraphs = []

    for paragraph in text.split("\n\n"):

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        paragraphs.append(paragraph)


    chunks = []

    current_chunk = ""

    # Maximum size of a chunk
    MAX_CHARS = 500

    # Minimum size before creating a separate chunk
    MIN_CHARS = 180


    for paragraph in paragraphs:

        # --------------------------------------------------
        # First paragraph
        # --------------------------------------------------

        if not current_chunk:

            current_chunk = paragraph

            continue


        # --------------------------------------------------
        # Combine small paragraphs
        # --------------------------------------------------

        combined_length = (
            len(current_chunk)
            + len(paragraph)
            + 2
        )


        if (
            combined_length <= MAX_CHARS
            and len(current_chunk) < MIN_CHARS
        ):

            current_chunk += (
                "\n\n" + paragraph
            )

        else:

            chunks.append(
                current_chunk
            )

            current_chunk = paragraph


    # --------------------------------------------------
    # Store final chunk
    # --------------------------------------------------

    if current_chunk:

        chunks.append(
            current_chunk
        )


    return chunks


# --------------------------------------------------
# 6. READ ALL KNOWLEDGE FILES
# --------------------------------------------------

documents = []
document_ids = []
metadatas = []

chunk_number = 1


for category in [
    "infrastructure",
    "pollution"
]:

    category_path = os.path.join(
        DATA_DIR,
        category
    )


    if not os.path.exists(category_path):

        print(
            f"Folder not found: {category_path}"
        )

        continue


    print("\n====================================")
    print(
        f"Processing category: {category}"
    )
    print("====================================")


    # --------------------------------------------------
    # Read all TXT files
    # --------------------------------------------------

    for filename in sorted(
        os.listdir(category_path)
    ):

        if not filename.lower().endswith(".txt"):

            continue


        file_path = os.path.join(
            category_path,
            filename
        )


        print(
            f"\nReading: {filename}"
        )


        # --------------------------------------------------
        # Read file
        # --------------------------------------------------

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()


        # --------------------------------------------------
        # Create focused chunks
        # --------------------------------------------------

        chunks = create_chunks(text)


        print(
            f"Created {len(chunks)} focused chunks"
        )


        # --------------------------------------------------
        # Store chunks
        # --------------------------------------------------

        for chunk in chunks:

            documents.append(chunk)


            document_ids.append(
                f"chunk_{chunk_number}"
            )


            metadatas.append({

                "category": category,

                "source": filename,

                "chunk_id": chunk_number

            })


            chunk_number += 1


# --------------------------------------------------
# 7. CREATE EMBEDDINGS
# --------------------------------------------------

print(
    f"\nCreating embeddings for "
    f"{len(documents)} chunks..."
)


embeddings = model.encode(
    documents,
    show_progress_bar=True
).tolist()


# --------------------------------------------------
# 8. STORE IN CHROMADB
# --------------------------------------------------

if documents:

    collection.add(

        ids=document_ids,

        documents=documents,

        embeddings=embeddings,

        metadatas=metadatas

    )


    print(
        "\nChunks successfully stored "
        "in ChromaDB."
    )

else:

    print(
        "\nNo documents were found."
    )


# --------------------------------------------------
# 9. FINAL INFORMATION
# --------------------------------------------------

print(
    "\n------------------------------------"
)

print(
    "RAG KNOWLEDGE BASE READY"
)

print(
    "------------------------------------"
)

print(
    "Total chunks stored:",
    collection.count()
)

print(
    "\nChromaDB location:"
)

print(
    CHROMA_DIR
)