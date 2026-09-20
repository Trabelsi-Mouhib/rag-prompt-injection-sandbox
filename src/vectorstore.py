import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# Configuration des dossiers
DATA_DIR = "./data"
CHROMA_DB_DIR = "./chroma_db"

def build_vector_store():
    documents = []
    
    # 1. Charger tous les fichiers texte (.txt) des dossiers benign et malicious
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                print(f"[+] Chargement du document : {file_path}")
                loader = TextLoader(file_path, encoding="utf-8")
                documents.extend(loader.load())

    # 2. Découper les documents en chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"[+] Total de chunks créés : {len(chunks)}")

    # 3. Initialiser le modèle d'embeddings Ollama
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # 4. Stocker les chunks et leurs vecteurs dans ChromaDB sur le disque
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    print(f"[✓] Base vectorielle créée avec succès dans '{CHROMA_DB_DIR}'.")
    return vector_store

if __name__ == "__main__":
    build_vector_store()
