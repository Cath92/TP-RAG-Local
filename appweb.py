import os
import requests
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)

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

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    query = ""
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            candidates = search_movies(query, top_k=5)
            answer = ask_llm(query, candidates)
            
    return render_template("index.html", answer=answer, query=query)

if __name__ == "__main__":
    app.run(debug=True, port=5000)