# Apolline Guérineau
# TP2 INDEXATION WEB
# REQUETE ET RANKING

Ce projet implémente un système de classement de documents web basé sur un index construit au préalable. La requête de l'utilisateur est tokenisée (de la même manière que les documents de l'index), et on retourne un nombre choisi de résultats parmis les plus pernitents, ceux-ci étant déterminé par une fonction de ranking.

## Fonctionnalités

Le script contient une classe principale appelée RankingSystem, qui est responsable du traitement des requêtes et du classement des résultats. À l'initialisation de la classe, les fichiers d'index et de documents sont chargés, et divers paramètres tels que le nombre de résultats à retourner, l'utilisation de tous les tokens dans la requête, et le type de classement (naïf ou avec le score BM25) sont spécifiés.

1. **Méthode load_json**

La méthode load_json est utilisée pour charger un fichier JSON et renvoyer son contenu sous forme de dictionnaire.

2. **Méthode tokenize_query**

Cette méthode utilise la tokenization de la bibliothèque NLTK pour diviser une requête en tokens. Les tokens sont ensuite convertis en minuscules.
Méthodes de Filtrage

* filter_documents_all_token: Filtre les documents qui contiennent tous les tokens de la requête.
* filter_documents: Filtre les documents qui contiennent au moins un token de la requête.

3. **Méthodes de Classement**

* linear_naive_ranking: Classe les documents en utilisant un classement naïf basé sur le nombre d'occurrences de tokens.
* bm25_score: Calcule le score BM25 pour un document par rapport à une requête.
* linear_ranking_with_bm25: Classe les documents en utilisant un classement basé sur le score BM25.

4. **Méthode run_query**

Cette méthode prend une requête de l'utilisateur, effectue la tokenization, le filtrage, et le classement des résultats, puis renvoie les résultats ainsi que le nombre de documents ayant survécu au filtre.

## Configuration

Le script peut être configuré en modifiant les paramètres du constructeur `RankingSystem` dans le fichier `main.py`. Voici les paramètres configurables :

- index_title : chemin vers l'index positionnels pour les titres
- index_content : chemin vers l'index positionnels pour les contenus
- documents : chemin vers la liste de dictionnaires des documents 
- nb_results : nombre de page que l'on souhaite retourner parmi les plus pertinentes
- all_token : filtrer les documents qui ont tous les tokens de la requête si all_token==True, sinon filtre les documents qui ont au moins un token de la requête
- naive_ranking : trier les documents selon une fonction de ranking 'naive', sinon tri selon le score de bm25


## Comment exécuter le script

1. **Installation des dépendances**:
   Exécutez la commande suivante :
   $ pip install -r ./requete/requirements.txt

2. **Exécution du script**:
    Exécutez le script avec la commande :
    $ python3 ./requete/main.py

3. **Résultats**:
    Les documents les plus pertinents pour la requête sont sockés dans le fichier results.json