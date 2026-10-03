import os

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CHROMA_DIR = os.path.join(
    BASE_DIR,
    "chroma_db"
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# ============================================================
# CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_collection(
    name="smart_city_knowledge"
)

print(
    "Infrastructure Agent connected to ChromaDB."
)


# ============================================================
# INFRASTRUCTURE AGENT
# ============================================================

def infrastructure_agent(
    question,
    number_of_results=10,
    relevance_threshold=0.90
):

    print("\n====================================")
    print("INFRASTRUCTURE AGENT")
    print("====================================")

    print(
        "Question:",
        question
    )

    # --------------------------------------------------------
    # Convert question into embedding
    # --------------------------------------------------------

    query_embedding = model.encode(
        question
    ).tolist()

    # --------------------------------------------------------
    # Search ChromaDB
    # --------------------------------------------------------

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=number_of_results
    )

    documents = (
        results.get(
            "documents",
            [[]]
        )[0]
    )

    metadatas = (
        results.get(
            "metadatas",
            [[]]
        )[0]
    )

    distances = (
        results.get(
            "distances",
            [[]]
        )[0]
    )

    print(
        "\nRetrieved results:",
        len(documents)
    )

    # --------------------------------------------------------
    # Filter infrastructure documents
    # --------------------------------------------------------

    relevant_information = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        category = ""

        if metadata:

            category = str(
                metadata.get(
                    "category",
                    ""
                )
            ).lower()

        # ----------------------------------------------------
        # Only infrastructure knowledge
        # ----------------------------------------------------

        if category != "infrastructure":
            continue

        print(
            f"\nCandidate distance: "
            f"{distance:.4f}"
        )

        print(
            "Source:",
            metadata.get(
                "source",
                "unknown"
            )
        )

        # ----------------------------------------------------
        # Similarity threshold
        #
        # Chroma distance:
        # smaller = more relevant
        #
        # 0.90 is intentionally used here because
        # your existing knowledge base contains useful
        # results above 0.56.
        # ----------------------------------------------------

        if distance <= relevance_threshold:

            relevant_information.append({

                "content": document,

                "source": metadata.get(
                    "source",
                    "unknown"
                ),

                "distance": distance

            })

    # --------------------------------------------------------
    # Sort by best distance
    # --------------------------------------------------------

    relevant_information.sort(
        key=lambda x: x["distance"]
    )

    # --------------------------------------------------------
    # Maximum 3 results
    # --------------------------------------------------------

    relevant_information = (
        relevant_information[:3]
    )

    # --------------------------------------------------------
    # No result
    # --------------------------------------------------------

    if not relevant_information:

        print(
            "\nNo relevant infrastructure "
            "information found."
        )

        return {

            "agent": "infrastructure",

            "found": False,

            "context": []

        }

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print(
        "\nRelevant infrastructure information:"
    )

    for index, item in enumerate(
        relevant_information,
        start=1
    ):

        print(
            f"\nResult {index}"
        )

        print(
            "Source:",
            item["source"]
        )

        print(
            "Distance:",
            round(
                item["distance"],
                4
            )
        )

        print(
            "Content:"
        )

        print(
            item["content"]
        )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "agent": "infrastructure",

        "found": True,

        "context": relevant_information

    }


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    while True:

        question = input(
            "\nAsk an infrastructure question "
            "(type 'exit' to stop): "
        ).strip()

        if question.lower() == "exit":
            break

        result = infrastructure_agent(
            question
        )

        print(
            "\n===================================="
        )

        print(
            "AGENT RESULT"
        )

        print(
            "===================================="
        )

        print(
            "Agent:",
            result["agent"]
        )

        print(
            "Found:",
            result["found"]
        )

        for index, item in enumerate(
            result["context"],
            start=1
        ):

            print(
                f"\nResult {index}"
            )

            print(
                "Source:",
                item["source"]
            )

            print(
                "Distance:",
                round(
                    item["distance"],
                    4
                )
            )

            print(
                "Content:"
            )

            print(
                item["content"]
            )