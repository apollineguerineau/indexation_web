# TP1 INDEXATION WEB
# CRAWLER

Ce script Python est un crawler web qui explore les pages web à partir d'une URL de départ. Il extrait les liens, vérifie les fichiers robots.txt, stocke les informations dans une base de données SQLite et suit les sitemaps pour découvrir de nouvelles pages.

## Fonctionnalités

- **Crawling de pages web**: Explore les pages web à partir d'une URL de départ.
- **Extraction de liens**: Extrait les liens des pages HTML.
- **Vérification de robots.txt**: Vérifie que le crawler est autorisé à accéder à une URL.
- **Stockage des informations dans une base de données**: Utilise une base de données SQLite pour stocker les URLs, leur contenu et l'heure de leur dernière visite.
- **Suivi des sitemaps**: Explore les sitemaps pour découvrir de nouvelles pages.

## Comment exécuter le script

1. **Installation des dépendances**:
   Exécutez la commande suivante :
   $ pip install -r requirements.txt

2. **Exécution du script**:
    Exécutez le script avec la commande :
    $ python3 main.py

3. **Résultats**:
    Les URLs visitées seront enregistrées dans le fichier `crawled_webpages.txt`, et les informations seront stockées dans la base de données SQLite `database.db`.

## Configuration

Le script peut être configuré en modifiant les paramètres du constructeur `Crawler` dans le fichier `main.py`. Voici les paramètres configurables :

- `start_url`: Url de départ pour le crawler.
- `max_urls`: Nombre maximum d'URLs à explorer.
- `politeness_delay`: Délai en secondes entre les requêtes pour respecter la politeness.
- `nb_links`: Nombre de liens à extraire par page.
- `nb_sitemaps`: Nombre de sitemaps à extraire par fichier robots.txt.

