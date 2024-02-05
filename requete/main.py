import json
from collections import defaultdict
from operator import itemgetter
import nltk
from nltk import word_tokenize
from math import log
import os

class RankingSystem:
    def __init__(self, 
                 index_title_file='./requete/title_pos_index.json', 
                 index_content_file='./requete/content_pos_index.json', 
                 documents_file='./requete/documents.json',
                 nb_results=10, 
                 all_token=True, 
                 naive_ranking=True):
        """
        Initialise l'objet RankingSystem avec les paramètres spécifiés.

        Paramètres :
        - index_title_file (str): Chemin vers le fichier JSON de l'index pour les titres.
        - index_content_file (str): Chemin vers le fichier JSON de l'index pour le contenu.
        - documents_file (str): Chemin vers le fichier JSON contenant les documents.
        - nb_results (int): Nombre de résultats à retourner.
        - all_token (bool): Indique si tous les tokens de la requête doivent être présents dans les documents filtrés.
        - naive_ranking (bool): Indique si le ranking doit être effectué de manière naïve (par comptage) ou avec le score BM25.
        """
        self.index_title = self.load_json(index_title_file)
        self.index_content = self.load_json(index_content_file)
        self.documents = self.load_json(documents_file)
        self.nb_results = nb_results
        self.all_token = all_token
        self.naive_ranking = naive_ranking

    def load_json(self, index_file : str):
        """
        Charge un fichier JSON et retourne son contenu.

        Paramètres :
        - index_file (str): Chemin vers le fichier JSON.

        Sortie :
        - dict: Contenu du fichier JSON.
        """
        with open(index_file, 'r') as file:
            return json.load(file)

    def tokenize_query(self, query : str):
        """
        Tokenise une requête en utilisant la tokenization de nltk.

        Paramètres :
        - query (str): Requête de l'utilisateur.

        Sortie :
        - list: Liste de tokens.
        """
        # Tokenization avec un split sur les espaces
        tokens = word_tokenize(query, 'french')
        tokens = [token.lower() for token in tokens]
        return tokens

    def filter_documents_all_token(self, query_tokens):
        """
        Filtre les documents qui contiennent tous les tokens de la requête.

        Paramètres :
        - query_tokens (list): Liste de tokens de la requête.

        Sortie :
        - list: Liste de documents filtrés.
        """
        filtered_documents = []
        for i, document in enumerate(self.documents):
            to_append = True
            for token in query_tokens:
                doc_ids_title = []
                doc_ids_content = []
                if token in self.index_title.keys():
                    doc_ids_title = self.index_title[token].keys()          
                if token in self.index_content.keys():
                    doc_ids_title = self.index_content[token].keys()   

                if str(document["id"]) not in doc_ids_title and str(document["id"]) not in doc_ids_content:
                    to_append = False

            if to_append == True:
                filtered_documents.append(document)

        return filtered_documents

    def filter_documents(self, query_tokens):
        """
        Filtre les documents qui contiennent au moins un token de la requête.

        Paramètres :
        - query_tokens (list): Liste de tokens de la requête.

        Sortie :
        - list: Liste de documents filtrés.
        """
        filtered_documents = []
        for i, document in enumerate(self.documents):
            for token in query_tokens:
                doc_ids_title = []
                doc_ids_content = []
                if token in self.index_title.keys():
                    doc_ids_title = self.index_title[token].keys()          
                if token in self.index_content.keys():
                    doc_ids_title = self.index_content[token].keys()  

                if str(document["id"]) in doc_ids_title or str(document["id"]) in doc_ids_content:
                    filtered_documents.append(document)

        return filtered_documents

    def linear_naive_ranking(self, query_tokens, filtered_documents):
        """
        Classe les documents en utilisant un ranking linéaire naïf (par comptage).

        Paramètres :
        - query_tokens (list): Liste de tokens de la requête.
        - filtered_documents (list): Liste de documents filtrés.

        Sortie :
        - list: Liste de résultats triés.
        """
        # Initialiser le score pour chaque document
        document_scores = defaultdict(float)

        # Parcourir chaque terme de la requête
        for query_token in query_tokens:

            # Vérifier si le terme est présent dans l'index
            if query_token in self.index_title.keys():

                # Parcourir chaque document contenant le terme
                for doc in filtered_documents:
                    # Augmenter le score du document en fonction du nombre d'occurrences du terme
                    try: 
                        score_title = len(self.index_title[query_token][str(doc["id"])]) / len(doc["title"])
                    except: 
                        score_title = 0
                    try: 
                        score_content = len(self.index_content[query_token][str(doc["id"])]) / len(doc["content"])
                    except: 
                        score_content = 0

                    document_scores[doc["id"]] += score_title + score_content

        # Trier les documents en fonction de leur score décroissant
        ranked_documents = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)

        # Récupérer les détails des documents classés
        results = [{'title': self.documents[doc_id]['title'], 'url': self.documents[doc_id]['url']} for doc_id, _ in ranked_documents]
        return results

    def bm25_score(self, query, document, k1=1.5, b=0.75):
        """
        Calcule le score BM25 pour un document par rapport à une requête.

        Paramètres :
        - query (list): Liste de termes de la requête.
        - document (list): Liste de termes du document.
        - k1 (float): Paramètre de saturation.
        - b (float): Paramètre de la longueur du document.

        Sortie :
        - float: Score BM25.
        """
        doc_length = len(document["content"])
        avg_doc_length = sum(len(doc["content"]) for doc in self.documents) / len(self.documents)
        num_documents = len(self.documents)

        score = 0
        for term in query:
            df = sum(1 for doc in self.documents if term in doc)
            idf = log((num_documents - df + 0.5) / (df + 0.5) + 1.0)

            tf = document["content"].count(term)
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))

            score += idf * (numerator / denominator)

        return score

    def linear_ranking_with_bm25(self, query, filtered_documents):
        """
        Classe les documents en utilisant un ranking linéaire avec le score BM25.

        Paramètres :
        - query (list): Liste de termes de la requête.
        - filtered_documents (list): Liste de documents filtrés.

        Sortie :
        - list: Liste de résultats triés.
        """
        document_scores = defaultdict(float)

        for doc in filtered_documents:
            score = self.bm25_score(query, doc)
            document_scores[doc["id"]] += score

        # Trier les documents en fonction de leur score décroissant
        ranked_documents = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)

        # Récupérer les détails des documents classés
        results = [{'title': self.documents[doc_id]['title'], 'url': self.documents[doc_id]['url']} for doc_id, _ in ranked_documents]
        return results

    def run_query(self, user_query):
        """
        Exécute une requête de l'utilisateur.

        Paramètres :
        - user_query (str): Requête de l'utilisateur.

        Sortie :
        - tuple: (Liste de résultats triés, Nombre de documents ayant survécu au filtre).
        """
        query_tokens = self.tokenize_query(user_query)
        if self.all_token == True : 
            filtered_documents = self.filter_documents_all_token(query_tokens)
        else : 
            filtered_documents = self.filter_documents(query_tokens)
        if self.naive_ranking == True: 
            ranked_documents = self.linear_naive_ranking(query_tokens, filtered_documents)
        else : 
            ranked_documents = self.linear_ranking_with_bm25(query_tokens, filtered_documents)

        # Écriture dans le fichier JSON
        if os.path.exists("./requete/results.json"):
            os.remove("./requete/results.json")
        with open("./requete/results.json", "w", encoding="utf-8") as fichier_json:
            json.dump(ranked_documents[:self.nb_results], fichier_json, ensure_ascii=False, indent=2)

        return ranked_documents[:self.nb_results], len(filtered_documents)

if __name__ == "__main__":
    # Exemple d'utilisation
    ranking_system = RankingSystem(all_token=False, naive_ranking=True)
    user_query = input("Entrez votre requête: ")
    results = ranking_system.run_query(user_query)

    print("Nombre de documents dans l'index : ")
    print(len(ranking_system.index_title))
    print('Nombre de documents ayant survécus au filtre : ')
    print(results[1])
    print(f'Les {ranking_system.nb_results} meilleures pages trouvées sont : ')
    for doc in results[0]:
        print(doc)
        print('---------------------------------------------------------------------------------------')

