import json
import os
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Connexion PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# 1. Nettoyage pour garantir l'idempotence (on vide la table avant de recharger)
cursor.execute("TRUNCATE TABLE documents RESTART IDENTITY;")
conn.commit()

# 2. Jeu de données de films (15 fiches)
movies_data = [
    {"title": "Inception", "category": "Science-Fiction", "year": 2010, "description": "Un voleur expérimenté qui dérobe des secrets à travers les rêves se voit offrir une chance d'effacer son casier s'il parvient à 'semer' une idée dans l'esprit d'un PDG."},
    {"title": "Interstellar", "category": "Science-Fiction", "year": 2014, "description": "Un groupe d'explorateurs utilise une faille spatio-temporelle récemment découverte afin de repousser les limites humaines et traverser les vastes distances d'un voyage interstellaire."},
    {"title": "Blade Runner 2049", "category": "Science-Fiction", "year": 2017, "description": "Un jeune blade runner découvre un secret enfoui depuis longtemps qui a le potentiel de plonger ce qui reste de la société dans le chaos."},
    {"title": "The Dark Knight", "category": "Action", "year": 2008, "description": "Batman s'associe au lieutenant Jim Gordon et au procureur Harvey Dent pour démanteler les organisations criminelles qui infestent Gotham. Mais ils font face à un criminel chaotique connu sous le nom du Joker."},
    {"title": "Gladiator", "category": "Historique", "year": 2000, "description": "Un général romain influent est trahi par le fils ambitieux de l'empereur, le conduisant à devenir un gladiateur cherchant à se venger."},
    {"title": "The Matrix", "category": "Science-Fiction", "year": 1999, "description": "Un hacker informatique découvre que la réalité telle qu'elle est perçue par l'humanité est une simulation virtuelle créée par des machines malveillantes."},
    {"title": "Pulp Fiction", "category": "Policier", "year": 1994, "description": "Les vies de deux tueurs à gages, d'un boxeur, de la femme d'un gangster et de deux braqueurs de petits restaurants s'entremêlent dans quatre histoires de violence et de rédemption."},
    {"title": "Le Seigneur des Anneaux : La Communauté de l'Anneau", "category": "Fantastique", "year": 2001, "description": "Un jeune hobbit, Frodon Sacquet, hérite d'un anneau magique doté d'un pouvoir maléfique et entreprend une quête périlleux pour le détruire."},
    {"title": "Jurassic Park", "category": "Science-Fiction", "year": 1993, "description": "Des scientifiques visitent un parc à thème peuplé de dinosaures clonés, mais la situation dégénère lorsque les créatures s'échappent de leurs enclos."},
    {"title": "Whiplash", "category": "Drame", "year": 2014, "description": "Un jeune batteur de jazz talentueux intègre un conservatoire prestigieux où il subit l'enseignement tyrannique d'un professeur intransigeant."},
    {"title": "Mad Max: Fury Road", "category": "Action", "year": 2015, "description": "Dans un monde post-apocalyptique désertique, une rebelle et un ancien prisonnier unissent leurs forces pour fuir un tyran sanguinaire au volant d'un camion blindé."},
    {"title": "Le Fabuleux Destin d'Amélie Poulain", "category": "Comédie", "year": 2001, "description": "Une jeune serveuse parisienne naïve et rêveuse décide d'apporter le bonheur aux gens qui l'entourent par de petits actes de gentillesse anonymes."},
    {"title": "Avatar", "category": "Science-Fiction", "year": 2009, "description": "Un marine paraplégique est envoyé sur la lointaine lune de Pandora pour une mission unique, mais il se retrouve déchiré entre suivre ses ordres et protéger le peuple autochtone."},
    {"title": "Titanic", "category": "Romance", "year": 1997, "description": "Une aristocrate de dix-sept ans tombe amoureuse d'un artiste pauvre et libre d'esprit à bord du paquebot luxueux et infortuné lors de son voyage inaugural."},
    {"title": "Seul sur Mars", "category": "Science-Fiction", "year": 2015, "description": "Un astronaute est accidentellement laissé pour mort sur Mars par son équipage et doit utiliser son ingéniosité et son esprit de survie pour subsister sur la planète rouge."}
]

def get_embedding(text):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text}
    )
    return response.json()["embedding"]

# 3. Insertion des films
for movie in movies_data:
    content = f"Titre : {movie['title']}. Catégorie : {movie['category']}. Année : {movie['year']}. Résumé : {movie['description']}"
    embedding = get_embedding(content)
    
    metadata = json.dumps({"year": movie["year"], "category": movie["category"]})
    
    cursor.execute(
        "INSERT INTO documents (source, content, metadata, embedding) VALUES (%s, %s, %s, %s)",
        (movie["title"], content, metadata, embedding)
    )

conn.commit()
cursor.close()
conn.close()
print("Ingestion terminée avec succès !")