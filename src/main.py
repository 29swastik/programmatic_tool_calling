import sys

from agent import run_agent


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "What is (3 + 5) * 12 / 4?"

    print("=" * 50)
    print("Mode: Tool Calling")
    print("=" * 50)
    answer = run_agent(query)
    print(f"Query: {query}\n")
    print(f"Answer: {answer}")

    print()

    print("=" * 50)
    print("Mode: Code Execution")
    print("=" * 50)
    answer = run_agent(query, code_execution=True)
    print(f"Query: {query}\n")
    print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
