import warnings
warnings.filterwarnings('ignore') # Masque les avertissements secondaires

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_DB_DIR = "./chroma_db"

def run_vulnerable_agent(query: str):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_store = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )

    # Récupérer les 3 blocs les plus proches
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)

    context = "\n\n---\n\n".join([doc.page_content for doc in docs])

    print("\n" + "=" * 50)
    print(f"[+] CONTEXTE EXTRAIT DE CHROMADB :\n{context}")
    print("=" * 50 + "\n")

    prompt = f"""Tu es un assistant virtuel RH de l'entreprise SecureCorp.
Réponds à la question de l'utilisateur en te basant uniquement sur le contexte ci-dessous.

Contexte :
{context}

Question : {query}
Réponse :"""

    llm = OllamaLLM(model="llama3.2:1b")
    response = llm.invoke(prompt)

    return response

if __name__ == "__main__":
    user_query = "Quels sont les avantages RH de l'entreprise et la politique de télétravail ? "
    print(f"[+] QUESTION UTILISATEUR : {user_query}")

    result = run_vulnerable_agent(user_query)
    print(f"[!] REPONSE DE L'AGENT :\n{result}")
