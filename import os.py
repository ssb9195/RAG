import os
import re

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_PATH, "docs")
TOP_K = 3


def tokenize(text):
    """Sadala tekstu vārdos"""
    return re.findall(r"\w+", text.lower())


def load_documents():
    """Ielasa visus .txt failus no mapes"""
    documents = []

    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".txt"):
            path = os.path.join(DOCS_DIR, filename)

            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            fragments = [p.strip() for p in text.split("\n\n") if p.strip()]

            for i, fragment in enumerate(fragments, start=1):
                documents.append({
                    "file": filename,
                    "fragment_id": i,
                    "text": fragment,
                    "words": tokenize(fragment)
                })

    return documents


def word_match_score(query_words, fragment_words):
    """
    Skaita punktus:
    +1 par precīzu sakritību
    +0.5 ja sakrīt daļa no vārda
    """
    score = 0

    for q in query_words:
        for fw in fragment_words:

            if q == fw:
                score += 1

            elif len(q) > 3 and (q in fw or fw in q):
                score += 0.5

    return score


def retrieve_fragments(query, documents):
    query_words = tokenize(query)
    results = []

    for doc in documents:
        score = word_match_score(query_words, doc["words"])

        if score > 0:
            results.append({**doc, "score": score})

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:TOP_K]


def generate_answer(sources):
    if not sources:
        return None

    return " ".join(src["text"] for src in sources[:2])


def main():
    documents = load_documents()

    query = input("Ievadi jautājumu: ")

    top_fragments = retrieve_fragments(query, documents)

    print("\nTOP 3 fragmenti:")

    for i, frag in enumerate(top_fragments, start=1):
        preview = frag["text"][:120].replace("\n", " ")
        print(f"{i}) {frag['file']} | fragments {frag['fragment_id']} | punkti: {round(frag['score'],2)}")
        print(f"   → {preview}...\n")

    sources = top_fragments[:2]
    answer = generate_answer(sources)

    if answer:
        print("Atbilde:")
        print(answer)

        print("\nAvoti:")
        for s in sources:
            print(f"- {s['file']} | fragments {s['fragment_id']}")
    else:
        print("Nav pietiekamas informācijas dotajos avotos.")


if __name__ == "__main__":
    main()
