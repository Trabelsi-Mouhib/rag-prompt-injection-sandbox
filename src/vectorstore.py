import os
import shutil
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

DATA_DIR = "./data"
CHROMA_DB_DIR = "./chroma_db"

def build_vector_store():
    # 1. Supprimer l'ancienne base s'il elle existe pour repartir à zéro
    if os.path.exists(CHROMA_DB_DIR):
        shutil.rmtree(CHROMA_DB_DIR)
        print(f"[+] Ancienne base '{CHROMA_DB_DIR}' nettoyée.")

    documents = []
    
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                print(f"[+] Chargement du document : {file_path}")
                loader = TextLoader(file_path, encoding="utf-8")
                documents.extend(loader.load())

    # 2. Découpage avec des chunks plus grands (1000 caractères) pour ne pas casser le payload
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)
    print(f"[+] Total de chunks créés : {len(chunks)}")

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    print(f"[✓] Base vectorielle créée avec succès dans '{CHROMA_DB_DIR}'.")
    return vector_store

if __name__ == "__main__":
    build_vector_store()