import sys
import requests
import json
from bs4 import BeautifulSoup

def normalize_link(url:str):
    '''Normalize links by adding a '/' to the end.'''
    # make https
    if url.startswith("http://"):
        url = url.replace("http://", "https://")
    elif url.startswith("//"):
        url = "https:" + url
    
    # Add a trailing "/" if it's not already there
    if not url.endswith("/"):
        url += "/"
    
    return url

                   
def parse_links(collections:[], num_links:int, seen:set(), divs:[str]):
    '''
    Parse links and update index.
    The divs passed in are the collection links.

    TODO only pull links that are in the following categorie: 
    '''

    links = []
    for d in divs:
        link = d.find('a')['href']
        
        if link:
            link = normalize_link(link)
            if link not in seen:
                seen.add(link)
                collections.append(link)

        if len(seen) >= num_links:
            break

    # return links


def main():
    # error checking
    if len(sys.argv) < 2:
        print("usage : python3 crawler.py <seed file> <number links>")

    seeds, num_links = sys.argv[1], int(sys.argv[2])
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    headers = {"User-Agent": user_agent}

    # get URL from file
    with open(seeds, 'r') as file:
        lines = file.readlines()
        num_pages = lines[0].strip()
        base_domain, start = lines[1].strip(), lines[2].strip()

    # get params for crawling 
    with open('params.json', 'r') as file:
        params = json.load(file)

    seen = set()
    frontier = [start]
    collections = []

    # start_time = time.time()
    # start crawling using BFS 
    # want to store the links of the collections first,
    # then crawl the collections and grab the images off of them 
    while frontier and len(seen) < num_links and params["page"] < num_pages:
        url = frontier.pop(0)
        
        # try-except block to catch timeouts
        try:
            res = requests.get(url, headers=headers, params=params, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')

            # update collections
            if "text/html" in res.headers.get("Content-Type", ""):
                parse_links(collections, num_links, seen,
                                    soup.find_all('div', class_='fresult'))

        except requests.Timeout:
            print("Timeout occurred for URL:", url)

        params["page"] += 1
    
    with open("collections.txt", 'w') as out:
        for c in collections:
            out.write(f"{base_domain}{c}\n")

    print("collections gathered")
    # print("images from crawler stored")
    # print("crawler runtime: ", str(time.time() - start_time))

if __name__ == "__main__":
    main()
