from ddgs import DDGS


def web_search(query, max_results=5):
    results = []

    with DDGS() as ddgs:
        for item in ddgs.text(
            query,
            max_results=max_results
        ):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", "")
            })

    return results


if __name__ == "__main__":
    query = input("Search: ")

    results = web_search(query)

    if not results:
        print("No results found.")
    else:
        for result in results:
            print("\nTITLE:", result["title"])
            print("URL:", result["url"])
            print("SNIPPET:", result["snippet"])