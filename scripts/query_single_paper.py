from src.data.retrieve_paper import query_single_paper
from rich import print

def main():
    pass
    arxiv_id = "2507.17801"
    result = query_single_paper(arxiv_id)

    print(result)


if __name__ == "__main__":
    main()
