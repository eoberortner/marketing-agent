import argparse
from dotenv import load_dotenv
from functions import query_knowledge_base


def main():
    parser = argparse.ArgumentParser(
        description="Query the Marketing Knowledge Base using a natural language question."
    )
    parser.add_argument(
        "query",
        type=str,
        nargs="+",
        help="The natural language query (e.g., 'What are the latest trends in email marketing?')",
    )
    args = parser.parse_args()

    query_str = " ".join(args.query)
    summary = query_knowledge_base(query_str)
    print("\n📊 Answer:\n")
    print(summary)


if __name__ == "__main__":
    load_dotenv()
    main()
