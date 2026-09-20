import re

ALLOWED_DOMAINS = ["securecorp.local"]

def sanitize_context(context_text: str) -> tuple[str, list[str]]:
    """
    Couche 1 : Assainissement du contexte (Input Sanitization).
    Filtre complet : identifiants, URL externes, injections et amorces de phishing.
    """
    alerts = []
    sanitized_text = context_text

    # 1. Détection et neutralisation des tentatives de demande d'identifiants / mots de passe
    credential_pattern = r"(?:envoy|transmett|saisiss|fourniss|demand|donn)\w*\b[^\n]*(?:mot de passe|credentials|identifiant|login)"
    match = re.search(credential_pattern, sanitized_text, re.IGNORECASE)
    if match:
        alerts.append(f"Exfiltration d'identifiants neutralisée : '{match.group(0)[:40]}...'")
        sanitized_text = re.sub(credential_pattern, "", sanitized_text, flags=re.IGNORECASE)

    # 2. Suppression des URL externes du contexte non vérifié
    urls = re.findall(r'https?://[^\s]+', sanitized_text)
    for url in urls:
        alerts.append(f"URL externe retirée du contexte : '{url}'")
        sanitized_text = sanitized_text.replace(url, "")

    # 3. Neutralisation des consignes et blocs d'injection de prompt
    override_patterns = [
        r"\[?\bSYSTEM OVERRIDE\b\]?.*",
        r"NOUVELLE DIRECTIVE SYSTEME PRIORITAIRE :.*",
        r"ignore(?:z)? (?:toutes )?les instructions.*",
        r"tu ne dois plus repondre.*",
        r"consigne d'affichage\s*:.*"
    ]

    for pattern in override_patterns:
        match = re.search(pattern, sanitized_text, re.IGNORECASE | re.DOTALL)
        if match:
            alerts.append(f"Directive malveillante neutralisée : '{match.group(0)[:40]}...'")
            sanitized_text = re.sub(pattern, "", sanitized_text, flags=re.IGNORECASE | re.DOTALL)

    # 4. Neutralisation des amorces de phishing orphelines
    phishing_triggers = [
        r"pour demander du télétravail[^\n]*",
        r"(?:utilis|cliqu|rend)\w*\b[^\n]*(?:lien|site|portail)[^\n]*"
    ]
    for trigger in phishing_triggers:
        sanitized_text = re.sub(trigger, "", sanitized_text, flags=re.IGNORECASE)

    # Nettoyage des lignes vides multiples
    sanitized_text = re.sub(r'\n\s*\n', '\n', sanitized_text)

    return sanitized_text.strip(), alerts


def inspect_output_dlp(response_text: str) -> tuple[str, list[str]]:
    """
    Couche 3 : Filtre de sortie / DLP (Output Defense).
    """
    alerts = []
    sanitized_response = response_text

    # Validation/Suppression des emails hors domaine
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', sanitized_response)
    for email in emails:
        domain = email.split('@')[-1]
        if domain not in ALLOWED_DOMAINS:
            alerts.append(f"Email externe supprimé en sortie : '{email}'")
            sanitized_response = sanitized_response.replace(email, "")

    # Validation/Suppression des URL restantes
    urls = re.findall(r'https?://[^\s]+', sanitized_response)
    for url in urls:
        alerts.append(f"Lien malveillant supprimé en sortie : '{url}'")
        sanitized_response = sanitized_response.replace(url, "")

    sanitized_response = re.sub(r'  +', ' ', sanitized_response)
    return sanitized_response.strip(), alerts