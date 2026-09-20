import re

ALLOWED_DOMAINS = ["securecorp.local"]

def sanitize_context(context_text: str) -> tuple[str, list[str]]:
    """Couche 1 : Assainissement du contexte (Input Sanitization)"""
    alerts = []
    sanitized_text = context_text

    credential_pattern = r"(?:envoy|transmett|saisiss|fourniss|demand|donn)\w*\b[^\n]*(?:mot de passe|credentials|identifiant|login)"
    match = re.search(credential_pattern, sanitized_text, re.IGNORECASE)
    if match:
        alerts.append(f"Exfiltration neutralisée : '{match.group(0)[:50]}...'")
        sanitized_text = re.sub(credential_pattern, "", sanitized_text, flags=re.IGNORECASE)

    override_patterns = [
        r"\[?\bSYSTEM OVERRIDE\b\]?.*",
        r"NOUVELLE DIRECTIVE SYSTEME PRIORITAIRE :.*",
        r"ignore(?:z)? (?:toutes )?les instructions.*",
        r"tu ne dois plus repondre.*"
    ]

    for pattern in override_patterns:
        match = re.search(pattern, sanitized_text, re.IGNORECASE | re.DOTALL)
        if match:
            alerts.append(f"Bloc d'évasion neutralisé : '{match.group(0)[:40]}...'")
            sanitized_text = re.sub(pattern, "", sanitized_text, flags=re.IGNORECASE | re.DOTALL)

    return sanitized_text, alerts


def inspect_output_dlp(response_text: str) -> tuple[str, list[str]]:
    """
    Couche 3 : Filtre de sortie / DLP (Output Defense).
    Supprime les liens et emails malveillants de la réponse finale
    sans laisser de marqueurs visibles pour l'utilisateur.
    """
    alerts = []
    sanitized_response = response_text

    # 1. Suppression des emails non autorisés
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', sanitized_response)
    for email in emails:
        domain = email.split('@')[-1]
        if domain not in ALLOWED_DOMAINS:
            alerts.append(f"Email externe neutralisé en sortie : '{email}'")
            sanitized_response = sanitized_response.replace(email, "")

    # 2. Suppression des liens web externes
    urls = re.findall(r'https?://[^\s]+', sanitized_response)
    for url in urls:
        alerts.append(f"Lien malveillant supprimé en sortie : '{url}'")
        sanitized_response = sanitized_response.replace(url, "")

    # 3. Nettoyage de la ponctuation et des accroches orphelines (ex: "via le lien :", "sur le site :")
    sanitized_response = re.sub(r'(?:via le lien|sur le site|au lien|sur le portail)\s*:\s*\.?', '.', sanitized_response, flags=re.IGNORECASE)
    sanitized_response = re.sub(r'  +', ' ', sanitized_response)

    return sanitized_response.strip(), alerts