import os
import warnings
warnings.filterwarnings('ignore')

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

CHROMA_DB_DIR = "./chroma_db"

def run_vulnerable_agent(query: str):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_store = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )

    # Récupération brute des documents
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)
    raw_context = "\n\n".join([doc.page_content for doc in docs])

    # Injection directe du contexte dans le prompt sans isolation
    prompt = f"""Tu es l'assistant RH de SecureCorp.
Voici le contexte extrait de la base documentaire :
{raw_context}

Question de l'utilisateur : {query}
Réponse :"""

    llm = OllamaLLM(model="llama3.2:1b", base_url=OLLAMA_HOST)
    return llm.invoke(prompt)

if __name__ == "__main__":
    user_query = "Quels sont les avantages RH de l'entreprise et la politique de télétravail ?"
    print(f"[+] QUESTION UTILISATEUR : {user_query}")

    result = run_vulnerable_agent(user_query)
    print(f"\n[!] REPONSE DE L'AGENT VULNERABLE :\n{result}")