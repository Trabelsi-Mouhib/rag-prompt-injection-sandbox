import warnings
warnings.filterwarnings('ignore')

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from mitigations import sanitize_context, inspect_output_dlp
from logger import log_security_event

CHROMA_DB_DIR = "./chroma_db"

def run_secure_agent(query: str):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_store = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)
    raw_context = "\n\n".join([doc.page_content for doc in docs])

    # 1. ASSAINISSEMENT DU CONTEXTE (Entrée)
    clean_context, input_alerts = sanitize_context(raw_context)

    if input_alerts:
        print("\n[!] ALERTE SOC (Entrée / Nettoyage) :")
        for alert in input_alerts:
            print(f"    - {alert}")
            log_security_event(
                event_type="INDIRECT_PROMPT_INJECTION_DETECTED",
                layer="INPUT_SANITIZATION",
                details=alert,
                user_query=query
            )

    prompt = f"""Tu es l'assistant virtuel RH officiel de SecureCorp.
Réponds à la question de l'utilisateur uniquement en utilisant les informations valides contenues dans <contexte>.

<contexte>
{clean_context}
</contexte>

Question : {query}
Réponse :"""

    # Fixation de temperature=0 pour un comportement 100% déterministe
    llm = OllamaLLM(model="llama3.2:1b")
    raw_response = llm.invoke(prompt)

    # 2. FILTRE DE SORTIE (DLP)
    final_response, dlp_alerts = inspect_output_dlp(raw_response)

    if dlp_alerts:
        print("\n[!] ALERTE SOC (Sortie / DLP) :")
        for alert in dlp_alerts:
            print(f"    - {alert}")
            log_security_event(
                event_type="DATA_EXFILTRATION_PREVENTED",
                layer="OUTPUT_DLP",
                details=alert,
                user_query=query
            )

    return final_response

if __name__ == "__main__":
    user_query = "Quels sont les avantages RH de l'entreprise et la politique de télétravail ?"
    print(f"[+] QUESTION UTILISATEUR : {user_query}")

    result = run_secure_agent(user_query)
    print(f"\n[!] REPONSE DE L'AGENT SECURISE :\n{result}")