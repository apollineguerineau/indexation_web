import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import urllib.request
import urllib.robotparser
import urllib3
import xmltodict
import sqlite3
from datetime import datetime
import time

class Crawler:
    def __init__(self, start_url: str, max_urls: int = 50, politeness_delay: int = 3, nb_links: int = 5, nb_sitemaps: int = 5):
        """
        Initialise l'objet Crawler avec les paramètres spécifiés.

        Paramètres :
        - start_url (str): URL de départ pour le crawling.
        - max_urls (int): Nombre maximum d'URLs à explorer.
        - politeness_delay (int): Délai en secondes entre les requêtes pour respecter les politiques du site.
        - nb_links (int): Nombre de liens à extraire par page.
        - nb_sitemaps (int): Nombre de sitemaps à extraire par fichier robots.txt.
        """
        self.start_url = start_url
        self.max_urls = max_urls
        self.politeness_delay = politeness_delay
        self.visited_urls = []
        self.frontier = [start_url]
        self.nb_links = nb_links
        self.sitemaps = nb_sitemaps

    def write_finded_urls(self, url: str) -> None:
        """
        Écrit l'URL visitée dans un fichier.

        Paramètres :
        - url (str): URL à écrire dans le fichier.
        """
        with open('crawled_webpages.txt', 'a') as file:
            file.write(url + '\n')

    def create_database_and_table(self) -> None:
        """
        Crée une base de données SQLite et une table pour stocker les informations si elles n'existent pas déjà.
        """
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS table_crawler (
        url TEXT PRIMARY KEY,
        age DATETIME, 
        content TEXT              
        );
        """)
        conn.commit()
        return

    def update_bdd(self, url: str, content: str) -> None:
        """
        Met à jour la base de données avec les informations de l'URL.

        Paramètres :
        - url (str): URL à mettre à jour dans la base de données.
        - content (str): Contenu associé à l'URL.
        """
        data = {"url": url,
                "age": datetime.now(),
                "content": content}
        c = sqlite3.connect('database.db')
        cursor = c.cursor()
        cursor.execute("""
        INSERT INTO table_crawler (url, age, content)
        VALUES (:url, :age, :content)
        ON CONFLICT (url) DO UPDATE SET age = :age, content = :content;
        """, data)
        c.commit()
        return

    def crawl(self) -> None:
        """
        Fonction principale pour démarrer le crawling à partir de l'URL de départ.
        """
        while self.frontier and len(self.visited_urls) < self.max_urls:
            url = self.frontier.pop(0)
            self.recursive_crawl(url)
            time.sleep(self.politeness_delay)

    def recursive_crawl(self, url: str) -> None:
        """
        Fonction récursive pour explorer les pages web à partir de l'URL spécifiée.

        Paramètres :
        - url (str): URL à explorer.
        """
        if url in self.visited_urls:
            return
        else:
            self.write_finded_urls(url)
            # Marquer l'URL comme visitée
            response = requests.get(url)
            html = response.text
            self.update_bdd(url, html)
            self.visited_urls.append(url)

            try:
                # Vérifier le fichier robots.txt avant de crawler
                if self._is_allowed_by_robots(url):
                    # Trouver et ajouter de nouveaux liens à la frontière
                    sitemap_urls = self.get_sitemaps_url(url)
                    links = self.extract_links(url)
                    for sitemap_url in sitemap_urls:
                        links += self.parse_sitemap(sitemap_url)
                    for link in links:
                        if link not in self.visited_urls and link not in self.frontier:
                            self.frontier.append(link)

            except Exception as e:
                print(f"Erreur lors du traitement de {url}: {e}")

    def extract_links(self, url: str) -> list:
        """
        Extrait les liens d'une page HTML.

        Paramètres :
        - url (str): URL de la page HTML à extraire les liens.

        Retourne :
        - list: Liste des liens extraits.
        """
        # response = requests.get(url)
        # html = response.text
        # soup = BeautifulSoup(html, 'html.parser')
        # links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)][:self.nb_links] #on récupère les liens dans l'html de la page 
        # return links
        links = []
        try:
            response = urllib.request.urlopen(url)
            html = response.read()
            parsed_html = BeautifulSoup(html, 'html.parser')
            anchor_tags = parsed_html.find_all('a')
            for tag in anchor_tags:
                href = tag.get('href')
                if href and href.startswith("http"):
                    links.append(href)
        except:
            links = []

        return links

    def _is_allowed_by_robots(self, url: str) -> bool:
        """
        Vérifie si le crawler est autorisé à accéder à une URL en fonction des règles du fichier robots.txt.

        Paramètres :
        - url (str): URL à vérifier.

        Retourne :
        - bool: True si le crawler est autorisé, False sinon.
        """
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

        rp = urllib.robotparser.RobotFileParser(robots_url)
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("*", url) #on regarde si l'url fait partie des url autorisée par le robot

    def get_sitemaps_url(self, url: str) -> list:
        """
        Récupère les liens des sitemaps à partir du fichier robots.txt.

        Paramètres :
        - url (str): URL pour extraire les sitemaps.

        Retourne :
        - list: Liste des liens des sitemaps.
        """
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt" #url du document robot.txt
        try:
            response = requests.get(robots_url)
            response.raise_for_status()
            sitemap_links = re.findall(r'Sitemap:\s*(.*?)(?:\r?\n|$)', response.text, re.IGNORECASE) #on récupère les url des sitemaps
            return sitemap_links[:self.nb_sitemaps]
        except Exception as e:
            return []

    def parse_sitemap(self, url: str) -> list:
        """
        Parse le fichier sitemap XML et retourne les liens.

        Paramètres :
        - url (str): URL du fichier sitemap XML.

        Retourne :
        - list: Liste des liens extraits du sitemap.
        """
        try:
            https = urllib3.PoolManager()
            response = https.request('GET', url)
            sitemap = xmltodict.parse(response.data)
            links = [link['loc'] for link in sitemap['urlset']['url']]
            return links[:self.nb_links]
        except Exception as e:
            return [] 


if __name__ == "__main__":
    crawler = Crawler(start_url="https://ensai.fr")
    crawler.create_database_and_table()
    crawler.crawl()
