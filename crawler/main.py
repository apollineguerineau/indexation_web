import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse, urljoin
from protego import Protego
import xml.etree.ElementTree as ET

class Crawler:
    def __init__(self, start_url, max_urls=50, politeness_delay=3, nb_links=5):
        self.start_url = start_url
        self.max_urls = max_urls
        self.politeness_delay = politeness_delay
        self.visited_urls = []
        self.frontier = [start_url]
        self.nb_links = nb_links

    def crawl(self):
        while self.frontier and len(self.visited_urls) < self.max_urls:
            url = self.frontier.pop(0)
            self.recursive_crawl(url)
            time.sleep(5)

    def recursive_crawl(self, url):
        if url in self.visited_urls:
            return

        else : 
            self.write_finded_urls(url)
            # Mark the URL as visited
            self.visited_urls.append(url)

            try:
                # Check robots.txt before crawling
                if self._is_allowed_by_robots(url)[0]:
                    # Find and add new links to the frontier
                    sitemap_urls = self._is_allowed_by_robots(url)[1]
                    links = []
                    for sitemap_url in sitemap_urls : 
                        links+=self.parse_sitemap(sitemap_url)
                    links += self.extract_links(url)
                    for link in links:
                        if link not in self.visited_urls and link not in self.frontier:
                            self.frontier.append(link)
                
            except Exception as e:
                print(f"Error while processing {url}: {e}")

    def write_finded_urls(self, url):
        with open('crawled_webpages.txt', 'a') as file:
            file.write(url + '\n')

    def extract_links(self,url):
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)][:self.nb_links]
        return links

    def _is_allowed_by_robots(self,url):
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        r = requests.get(robots_url)
        rp = Protego.parse(r.text)

        #urls sitemaps
        sitemap_urls = list(rp.sitemaps)
        # return(rp.can_fetch(url, "*"))
        return(True,sitemap_urls)
    
    def parse_sitemap(self,sitemap_url):
        response = requests.get(sitemap_url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            urls = [url.text for url in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            print(urls)
            return urls
        else:
            print(f"Failed to fetch sitemap {sitemap_url}. Status code: {response.status_code}")
            return []


if __name__ == "__main__":
    crawler = Crawler(start_url="https://ensai.fr")
    crawler.crawl()
