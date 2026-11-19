from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests

app = FastAPI()

# URL de l'API REST d'Ollama
OLLAMA_URL = "http://localhost:11434/api/chat"

class PromptRequest(BaseModel):
    model: str = "llama3"  # ou le modèle de votre choix installé sur Ollama
    prompt: str

@app.post("/api/chat")
def chat_with_ollama(data: PromptRequest):
    try:
        payload = {
            "model": data.model,
            "prompt": data.prompt,
            "stream": False  # Désactive le streaming pour recevoir toute la réponse d'un coup
        }
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return {"response": result.get("response", "")}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def read_index():
    # Interface HTML intégrée pour simplifier
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Mon Interface Ollama</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }
            textarea { width: 100%; height: 100px; padding: 10px; margin-bottom: 10px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
            button:hover { background: #0056b3; }
            #response { background: #f4f4f4; padding: 15px; margin-top: 20px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h2>Discussion avec Ollama</h2>
        <textarea id="prompt" placeholder="Posez votre question ici..."></textarea><br>
        <button onclick="sendPrompt()">Envoyer</button>
        <h3>Réponse :</h3>
        <div id="response">En attente...</div>

        <script>
            async function sendPrompt() {
                const promptText = document.getElementById('prompt').value;
                const responseDiv = document.getElementById('response');
                responseDiv.innerText = "Génération en cours...";

                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: promptText })
                    });
                    const data = await res.json();
                    responseDiv.innerText = data.response || data.detail;
                } catch (err) {
                    responseDiv.innerText = "Erreur de connexion au serveur.";
                }
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)