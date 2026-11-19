import os
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_embedding(text):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text}
    )
    return response.json()["embedding"]

def search_movies(query_text, top_k=5):
    query_vector = get_embedding(query_text)
    
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    
    # Requête SQL avec l'opérateur de distance cosinus (<=>) de pgvector
    # Plus la distance est proche de 0, plus les vecteurs sont similaires
    cursor.execute(
        "SELECT source, content FROM documents ORDER BY embedding <=> %s::vector LIMIT %s;",
        (str(query_vector), top_k)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def ask_llm(user_query, context_results):
    context_str = "\n---\n".join([row[1] for row in context_results])
    
    prompt = f"""Tu es un assistant cinéphile expert. En t'appuyant EXCLUSIVEMENT sur les descriptions de films fournies dans le contexte ci-dessous, sélectionne et présente les 3 meilleures recommandations pour répondre à la demande de l'utilisateur. 
Justifie en deux phrases pourquoi chaque choix correspond à la demande. 
Si aucun élément ne correspond, signale-le clairement.

Contexte :
{context_str}

Demande de l'utilisateur : {user_query}
"""

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
    )
    return response.json()["message"]["content"]

# --- Programme principal ---
if __name__ == "__main__":
    query = input("Que recherchez-vous comme film ? ")
    print("\nRecherche des films pertinents dans la base...")
    candidates = search_movies(query, top_k=5)
    
    print("Génération de la réponse par le LLM...")
    answer = ask_llm(query, candidates)
    
    print("\n--- Réponse finale ---")
    print(answer)