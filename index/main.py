import json
from collections import defaultdict
import spacy
from nltk.stem import SnowballStemmer

class IndexWeb:
    def __init__(self, crawler_urls = 'crawled_urls_light.json'):
        """
        Initialise l'objet Index avec les paramètres spécifiés.

        Paramètres :
        - crawler_urls (str): Le chemin vers le fichier JSON contenant les URLs du crawler.
        """
        self.crawler_urls = crawler_urls
        self.documents_tokenized = self.tokenize_document()[0]
        self.documents_tokenized_stem = self.tokenize_document()[1]

    def load_json(self):
        """
        Charge le fichier JSON contenant les URLs du crawler.
        """
        with open(self.crawler_urls, 'r') as file:
            data = json.load(file)
        return data
    
    def tokenize_document(self, stemming: bool = False) : 
        """
        Tokenise les documents à partir des titres, contenus et h1 des URLs.

        Paramètres :
        - stemming (bool): Indique si le stemming doit être appliqué lors de la tokenisation.

        Sortie :
        - tuple: (Liste de documents tokenisés sans stemming, Liste de documents tokenisés avec stemming)
        """

        # Charger le modèle spaCy pour le français
        process = spacy.load("fr_core_news_md")
        # Initialiser le stemmer Snowball pour le français
        stemmer = SnowballStemmer("french")

        documents_tokenized = []
        documents_tokenized_stem = []
        urls = self.load_json()
        for document in urls:

            title = document["title"]
            content = document["content"]
            h1 = document["h1"]

            # Traiter le texte en utilisant le pipeline spaCy, désactivant le tagueur pour l'efficacité
            pipe_title = process.pipe([title], disable=["tagger"])
            pipe_content = process.pipe([content], disable=["tagger"])
            pipe_h1 = process.pipe([h1], disable=["tagger"])

            title_tokens = []
            content_tokens = []
            h1_tokens = []

            title_tokens_stem = []
            content_tokens_stem = []
            h1_tokens_stem = []

            for doc in pipe_title:
                # Extraire les tokens du titre
                for token in doc:
                    title_tokens_stem.append((stemmer.stem(token.lemma_).lower()))
                    title_tokens.append((token.text.lower()))

            for doc in pipe_content:
                # Extraire les tokens du contenu
                for token in doc:
                    content_tokens_stem.append((stemmer.stem(token.lemma_).lower()))
                    content_tokens.append((token.text.lower()))

            for doc in pipe_h1:
                # Extraire les tokens du contenu
                for token in doc:
                    h1_tokens_stem.append((stemmer.stem(token.lemma_).lower()))
                    h1_tokens.append((token.text.lower()))

            documents_tokenized.append([title_tokens, content_tokens, h1_tokens])
            documents_tokenized_stem.append([title_tokens_stem, content_tokens_stem, h1_tokens_stem])

        return(documents_tokenized, documents_tokenized_stem)


    def calculate_statistics(self):
        """
        Calcule les statistiques sur les documents.

        Sortie :
        - dict: Dictionnaire contenant les statistiques calculées.
        """
                
        num_documents = len(self.documents_tokenized)

        total_tokens = 0
        tokens_per_field = defaultdict(int)
        avg_tokens_per_field = defaultdict(int)

        for document in self.documents_tokenized:
            total_tokens += len(document[0]) + len(document[1])
            tokens_per_field['title'] += len(document[0])
            tokens_per_field['content'] += len(document[1])
            tokens_per_field['h1'] += len(document[2])

        avg_tokens_per_document = total_tokens / num_documents
        avg_tokens_per_field['title'] = tokens_per_field['title'] / num_documents
        avg_tokens_per_field['content'] = tokens_per_field['content'] / num_documents
        avg_tokens_per_field['h1'] = tokens_per_field['h1'] / num_documents

        statistics = {
            'num_documents': num_documents,
            'total_num_tokens': total_tokens,
            'total_tokens_per_field': dict(tokens_per_field),
            'avg_tokens_per_document': avg_tokens_per_document,
            'avg_tokens_per_field_per_document': dict(avg_tokens_per_field)
        }

        return statistics
    

    def build_non_positional_index(self, field :str, stemming : bool =False):
        """
        Construit un index non positionnel pour le champ spécifié.

        Paramètres :
        - field (str): Le champ pour lequel construire l'index ('title', 'content' ou 'h1').
        - stemming (bool): Indique si le stemming doit être appliqué lors de la construction de l'index.

        Sortie :
        - dict: Index non positionnel construit pour le champ spécifié.
        """

        index = defaultdict(list)
        if field == 'title' : 
            nb=0
        elif field == 'content' : 
            nb=1
        elif field == 'h1' : 
            nb=2
        else : 
            return dict(index_title)
        
        if stemming : 
            documents = self.documents_tokenized_stem
        else : 
            documents = self.documents_tokenized

        for id, document in enumerate(documents) : 
            tokens = document[nb]
            for token in set(tokens):  # Using set to avoid duplicate tokens in the same document
                index[token].append(id)

        return dict(index)
    
    def build_positional_index(self, field : str, stemming : bool = False):
        """
        Construit un index positionnel pour le champ spécifié.

        Paramètres :
        - field (str): Le champ pour lequel construire l'index ('title', 'content' ou 'h1').
        - stemming (bool): Indique si le stemming doit être appliqué lors de la construction de l'index.

        Sortie :
        - defaultdict: Index positionnel construit pour le champ spécifié.
        """

        # Initialiser l'index positionnel
        positional_index = defaultdict(lambda: defaultdict(list))

        if field == 'title' : 
            nb=0
        elif field == 'content' : 
            nb=1
        elif field == 'h1' : 
            nb=2
        else : 
            return dict(index_title)
        
        if stemming : 
            documents = self.documents_tokenized_stem
        else : 
            documents = self.documents_tokenized

        # Parcourir tous les documents
        for id, document in enumerate(documents):
            

            # Parcourir chaque token
            tokens = document[nb]
            for position, token in enumerate(tokens):
                # Ajouter la position du terme dans l'index positionnel
                positional_index[token][id].append(position)

        return positional_index


if __name__ == "__main__":
    indexcalculator = IndexWeb()

    statistics = indexcalculator.calculate_statistics()

    index_title = indexcalculator.build_non_positional_index('title')
    index_content = indexcalculator.build_non_positional_index('content')
    index_h1 = indexcalculator.build_non_positional_index('h1')
    index_title_stem = indexcalculator.build_non_positional_index('title', stemming=True)
    index_content_stem = indexcalculator.build_non_positional_index('content', stemming=True)
    index_h1_stem = indexcalculator.build_non_positional_index('h1', stemming=True)

    pos_index_title = indexcalculator.build_positional_index('title')
    pos_index_content = indexcalculator.build_positional_index('content')
    pos_index_h1 = indexcalculator.build_positional_index('h1')
    pos_index_title_stem = indexcalculator.build_positional_index('title', stemming=True)
    pos_index_content_stem = indexcalculator.build_positional_index('content', stemming=True)
    pos_index_h1_stem = indexcalculator.build_positional_index('h1', stemming=True)

    with open('metadata.json', 'w') as metadata_file:
        json.dump(statistics, metadata_file, indent=2)


    with open('./non_positional_index/title.non_pos_index.json', 'w') as index_file_title:
        json.dump(index_title, index_file_title, indent=2)

    with open('./non_positional_index/content.non_pos_index.json', 'w') as index_file_content:
        json.dump(index_content, index_file_content, indent=2)

    with open('./non_positional_index/h1.non_pos_index.json', 'w') as index_file_h1:
        json.dump(index_h1, index_file_h1, indent=2)

    with open('./non_positional_index/mon_stemmer.title.non_pos_index.json', 'w') as index_stem_file_title:
        json.dump(index_title_stem, index_stem_file_title, indent=2)

    with open('./non_positional_index/mon_stemmer.content.non_pos_index.json', 'w') as index_stem_file_content:
        json.dump(index_content_stem, index_stem_file_content, indent=2)

    with open('./non_positional_index/mon_stemmer.h1.non_pos_index.json', 'w') as index_stem_file_h1:
        json.dump(index_h1_stem, index_stem_file_h1, indent=2)


    with open('./positional_index/content.pos_index.json', 'w') as pos_index_file_content:
        json.dump(pos_index_content, pos_index_file_content, indent=2)

    with open('./positional_index/title.pos_index.json', 'w') as pos_index_file_title:
        json.dump(pos_index_title, pos_index_file_title, indent=2)
    
    with open('./positional_index/h1.pos_index.json', 'w') as pos_index_file_h1:
        json.dump(pos_index_h1, pos_index_file_h1, indent=2)
    
    with open('./positional_index/mon_stemmer.title.pos_index.json', 'w') as pos_index_stem_file_title:
        json.dump(pos_index_title_stem, pos_index_stem_file_title, indent=2)

    with open('./positional_index/mon_stemmer.content.pos_index.json', 'w') as pos_index_stem_file_content:
        json.dump(pos_index_content_stem, pos_index_stem_file_content, indent=2)

    with open('./positional_index/mon_stemmer.h1.pos_index.json', 'w') as pos_index_stem_file_h1:
        json.dump(pos_index_h1_stem, pos_index_stem_file_h1, indent=2)