import os
import chromadb
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. PROJECT PATH
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CHROMA_DIR = os.path.join(
    BASE_DIR,
    "chroma_db"
)


# --------------------------------------------------
# 2. LOAD EMBEDDING MODEL
# --------------------------------------------------

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# --------------------------------------------------
# 3. CONNECT TO CHROMADB
# --------------------------------------------------

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_collection(
    name="smart_city_knowledge"
)

print("Connected to ChromaDB.")

print(
    "Knowledge chunks available:",
    collection.count()
)


# --------------------------------------------------
# 4. RETRIEVE INFORMATION
# --------------------------------------------------

def retrieve_information(
    question,
    number_of_results=2
):

    # Convert question into embedding
    question_embedding = model.encode(
        [question]
    ).tolist()


    # Search ChromaDB
    results = collection.query(

        query_embeddings=question_embedding,

        n_results=number_of_results,

        include=[
            "documents",
            "metadatas",
            "distances"
        ]

    )


    return results


# --------------------------------------------------
# 5. DISPLAY RESULTS
# --------------------------------------------------

def ask_knowledge_base(question):

    print(
        "\n===================================="
    )

    print(
        "QUESTION"
    )

    print(
        "===================================="
    )

    print(
        question
    )


    results = retrieve_information(
        question
    )


    documents = results.get(
        "documents",
        [[]]
    )[0]


    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]


    distances = results.get(
        "distances",
        [[]]
    )[0]


    if not documents:

        print(
            "\nNo relevant information found."
        )

        return


    print(
        "\n===================================="
    )

    print(
        "RELEVANT KNOWLEDGE"
    )

    print(
        "===================================="
    )


    for i, document in enumerate(
        documents
    ):

        print(
            f"\nResult {i + 1}"
        )


        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        if i < len(metadatas):

            metadata = metadatas[i]


            print(
                "Category:",
                metadata.get(
                    "category"
                )
            )


            print(
                "Source:",
                metadata.get(
                    "source"
                )
            )


        # --------------------------------------------------
        # Distance
        # --------------------------------------------------

        if i < len(distances):

            print(
                "Similarity distance:",
                round(
                    distances[i],
                    4
                )
            )


        # --------------------------------------------------
        # Content
        # --------------------------------------------------

        print(
            "\nContent:"
        )

        print(
            document
        )


# --------------------------------------------------
# 6. MAIN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "\n===================================="
    )

    print(
        "SMART CITY RAG RETRIEVER"
    )

    print(
        "===================================="
    )


    while True:

        question = input(
            "\nAsk a question "
            "(type 'exit' to stop): "
        )


        if question.lower() == "exit":

            print(
                "\nExiting..."
            )

            break


        if not question.strip():

            print(
                "Please enter a question."
            )

            continue


        ask_knowledge_base(
            question
        )