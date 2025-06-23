import os

from dotenv import load_dotenv
from connectors.llm import DeepSeekClient

from storage.vector_store import VectorStore

# from sentence_transformers import SentenceTransformer


def extract_triplets(text):
    triplets = []
    relation, subject, relation, object_ = "", "", "", ""
    text = text.strip()
    current = "x"
    for token in (
        text.replace("<s>", "")
        .replace("<pad>", "")
        .replace("</s>", "")
        .split()
    ):
        if token == "<triplet>":
            current = "t"
            if relation != "":
                triplets.append(
                    {
                        "head": subject.strip(),
                        "type": relation.strip(),
                        "tail": object_.strip(),
                    }
                )
                relation = ""
            subject = ""
        elif token == "<subj>":
            current = "s"
            if relation != "":
                triplets.append(
                    {
                        "head": subject.strip(),
                        "type": relation.strip(),
                        "tail": object_.strip(),
                    }
                )
            object_ = ""
        elif token == "<obj>":
            current = "o"
            relation = ""
        else:
            if current == "t":
                subject += " " + token
            elif current == "s":
                object_ += " " + token
            elif current == "o":
                relation += " " + token
    if subject != "" and relation != "" and object_ != "":
        triplets.append(
            {
                "head": subject.strip(),
                "type": relation.strip(),
                "tail": object_.strip(),
            }
        )
    return triplets


def test_vector_store():
    load_dotenv()
    assert os.environ.get("OPENAI_API_KEY") is not None

    vs = VectorStore()

    query = "What are red flags in marketing?"
    results = vs.search(query, top_k=3)

    # for r in results:
    #     print(f"\n📰 {r['title']}\n📝 {r['summary_processed']}\n🔗 {r['link']}")

    task_description = f"""
    TASK: Summarize the following information in a professionally sound manner.
    
    {results}
    """

    llm_client = DeepSeekClient()
    summary = llm_client.summarize(
        agent_description="You are a marketing expert.",
        task_description=task_description,
    )

    assert summary is not None

    return
