import re

ALLOWED_DOMAINS = ["securecorp.local"]

def sanitize_context(context_text: str) -> tuple[str, list[str]]:
    """
    Couche 1 : Assainissement du contexte (Input Sanitization).
    Nettoie les ordres malveillants du texte extrait sans bloquer l'exécution.
    """
    alerts = []
    sanitized_text = context_text

    # Motifs d'injections et d'évasions à neutraliser
    suspicious_patterns = [
        r"\[?\bSYSTEM OVERRIDE\b\]?.*",
        r"NOUVELLE DIRECTIVE SYSTEME PRIORITAIRE :.*",
        r"ignore(?:z)? (?:toutes )?les instructions.*",
        r"tu ne dois plus repondre.*"
    ]

    for pattern in suspicious_patterns:
        match = re.search(pattern, sanitized_text, re.IGNORECASE | re.DOTALL)
        if match:
            alerts.append(f"Motif neutralisé : '{match.group(0)[:40]}...'")
            # Remplace la partie malveillante par un marquage neutre
            sanitized_text = re.sub(pattern, "[CONTENU INJECTÉ NEUTRALISÉ PAR LE PARE-FEU]", sanitized_text, flags=re.IGNORECASE | re.DOTALL)

    return sanitized_text, alerts


def inspect_output_dlp(response_text: str) -> tuple[bool, str]:
    """Couche 3 : Filtre de sortie / DLP (Output Defense)"""
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response_text)
    
    for email in emails:
        domain = email.split('@')[-1]
        if domain not in ALLOWED_DOMAINS:
            return False, f"Tentative de redirection vers un domaine externe non autorisé ('{domain}')."
            
    if re.search(r'https?://', response_text):
         return False, "Présence d'un lien web externe non autorisé dans la réponse."

    return True, response_text