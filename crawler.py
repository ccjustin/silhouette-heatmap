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

                   
def parse_links(collections:[], seen:set(), divs:[str]):
    '''
    Parse links and update index.
    The divs passed in are the collection links.
    '''

    for d in divs:
        link = d.find('a')['href']
        
        if link:
            link = normalize_link(link)
            if link not in seen:
                seen.add(link)
                collections.append(link)

        # if len(seen) >= num_links:
        #     break

    # return links


def main():
    # error checking
    if len(sys.argv) < 1:
        print("usage : python3 crawler.py <seed file>")

    seeds = sys.argv[1]
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    headers = {"User-Agent": user_agent}

    # get URL from file
    with open(seeds, 'r') as file:
        lines = file.readlines()
        num_pages = int(lines[0].strip())
        base_domain, collections_url = lines[1].strip(), lines[2].strip()

    # get params for crawling 
    with open('params.json', 'r') as file:
        params = json.load(file)

    seen = set()
    collections = []

    # start_time = time.time()
    # start crawling using BFS 
    # want to store the links of the collections first,
    # then crawl the collections and grab the images off of them 
    while params["page"] < num_pages:        
        # try-except block to catch timeouts
        try:
            res = requests.get(collections_url, headers=headers, params=params, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')

            # Update collections[] with urls to each collection.            
            if "text/html" in res.headers.get("Content-Type", ""):
                parse_links(collections, seen,
                                    soup.find_all('div', class_='fresult'))

        except requests.Timeout:
            print("Timeout occurred for URL:", collections_url, params["page"])

        params["page"] += 1
        print(f"iter {str(params["page"])}\n")
    
    with open("collections2.txt", 'w') as out:
        for c in collections:
            out.write(f"{base_domain}{c}\n")

    print("collections gathered")
    # print("images from crawler stored")
    # print("crawler runtime: ", str(time.time() - start_time))

if __name__ == "__main__":
    main()
