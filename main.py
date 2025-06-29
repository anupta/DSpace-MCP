from fastmcp import FastMCP
import requests
import configparser
import sys

dspace_url = ""

mcp = FastMCP("DSpace MCP")

def parse_conf(path: str = "C:/config.ini"):
    config = configparser.ConfigParser()
    config.read(path)
    global dspace_url
    if 'dspace' in config:
        dspace_url = config['dspace']['dspace_url']

def format_metadata(metadata: dict) -> str:
    """Formats DSpace metadata into a readable string"""
    output = []
    for key, fields in metadata.items():
        values = [entry['value'] for entry in fields if 'value' in entry]
        value_str = "; ".join(values)
        output.append(f"{key}: {value_str}")
    return "\n".join(output)

def safe_dspace_search(query: str, offset: int = 0, limit: int = 10) -> list:
    try:
        params = {
            "query": query,
            "size": limit,
            "page": offset
        }
        url = f"{dspace_url}/server/api/discover/search/objects"
        response = requests.get(url, params=params, timeout=10)
        response.encoding = 'utf-8'

        if not response.ok:
            return [f"Error {response.status_code}: {response.text.strip()}"]

        results = []
        data = response.json()

        objects = data.get("_embedded", {}).get("searchResult", {}).get("_embedded", {}).get("objects", [])
        for item in objects:
            target = item.get("_embedded", {}).get("indexableObject", {})
            metadata = target.get("metadata", {})
            handle = target.get("handle", "N/A")
            formatted = format_metadata(metadata)
            results.append(f"Handle: {handle}\n{formatted}\n" + "-"*40)

        return results if results else ["No results found."]
    except Exception as e:
        return [f"Request failed: {str(e)}"]

def check_functions():
    global dspace_url
    if dspace_url != "":

        @mcp.tool()
        def search_saree(offset: int = 0, limit: int = 10, lookfor: str = "*") -> list:
            """
            Search DSpace content and return all metadata fields for matching items.
            """
            return safe_dspace_search(lookfor, offset, limit)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        parse_conf(str(sys.argv[1]))
    else:
        parse_conf()
    check_functions()
    mcp.run()
