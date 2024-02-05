# Apolline Guérineau
# TP2 INDEXATION WEB
# INDEX

Ce code Python implémente une classe `IndexWeb` permettant de construire un index non positionnel et un index positionnel à partir de données collectées par un "crawler" web. L'indexation est effectuée sur les titres, le contenu et les balises `<h1>` des pages web.

### Fonctionnalités

1. **Tokenisation des Documents :**
   - Les documents (titres, contenu, `<h1>`) sont tokenisés en utilisant le modèle spaCy pour le français.
   - L'option de stemming est disponible pendant la tokenisation.

2. **Calcul des Statistiques sur les Documents :**
   - Le script calcule diverses statistiques sur les documents, telles que le nombre total de documents, le nombre total de tokens, la moyenne des tokens par document et par champ.

3. **Construction d'Index Non Positionnel :**
   - Construit un index non positionnel pour les champs spécifiés (`'title'`, `'content'`, `'h1'`).
   - L'option de stemming est disponible lors de la construction de l'index non positionnel.

4. **Construction d'Index Positionnel :**
   - Construit un index positionnel pour les champs spécifiés (`'title'`, `'content'`, `'h1'`).
   - L'option de stemming est disponible lors de la construction de l'index positionnel.

## Comment exécuter le script

1. **Installation des dépendances**:
   Exécutez la commande suivante :
   $ pip install -r ./index/requirements.txt

2. **Exécution du script**:
    Exécutez le script avec la commande :
    $ python3 ./index/main.py

3. **Résultats**:
    Les informations statistiques calculées sont écrites dans un fichier metadata.json. De plus 4 types d'index sont créés : 
    * index non positionnels avec stemmatisation 
    * index non positionnels sans stemmatisation
    * index positionnels avec stemmatisation 
    * index positionnels sans stemmatisation

    Un index pour le titre, un index pour le contenu et un index pour la balise h1 sont créés pour chaque type d'index (on a donc au final 12 index créés).
