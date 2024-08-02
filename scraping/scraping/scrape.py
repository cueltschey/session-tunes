import argparse
import requests
from bs4 import BeautifulSoup

def get_urls_from_html(url):
    # Send a GET request to the URL
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all <a> tags
        for a_tag in soup.find_all('a'):
            # Print the URL from the href attribute
            print(a_tag.get('href'))
    else:
        print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract URLs from <a> tags on a given HTML page.")
    parser.add_argument("url", type=str, help="URL of the HTML page to parse")
    args = parser.parse_args()
    get_urls_from_html(args.url)
