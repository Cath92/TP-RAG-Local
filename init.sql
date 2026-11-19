-- 1. Activer l'extension vectorielle
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Créer la table principale de stockage des segments indexés
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(768)
);