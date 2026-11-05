
import re
import spacy

# Load the English language model
nlp = spacy.load("en_core_web_sm")


def unique_words(words):
    """Remove duplicates while preserving order."""
    return list(dict.fromkeys(words))


def extract_contextual_organizations(text):
    """Identify possible company names using sentence context."""

    organizations = []

    patterns = [
        r"\b((?:[A-Z][A-Za-z0-9&.-]*\s+){0,3}[A-Z][A-Za-z0-9&.-]*)\s+"
        r"(?:is|are)\s+(?:offering|hiring|recruiting|looking|seeking|providing)\b",

        r"\bCompany\s*:\s*([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,3})"
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            name = match.group(1).strip()
            organizations.append(name)

    return organizations


def analyze_job_text(job_description):
    """
    Extract possible organization names, nouns and action words.
    These insights do not prove whether a company is genuine or fraudulent.
    """

    doc = nlp(job_description)

    nouns = []
    verbs = []
    organizations = []

    # Extract nouns and verbs
    for token in doc:
        if token.is_stop or token.is_punct or token.is_space:
            continue

        if token.pos_ in ("NOUN", "PROPN"):
            nouns.append(token.text)

        elif token.pos_ in ("VERB", "AUX"):
            verbs.append(token.text)

    # Names that should not be treated as companies
    ignored_names = {
        "python developer internship",
        "python developer",
        "python developer intern",
        "software developer",
        "data entry executive",
        "web developer",
        "business analyst",
        "telegram",
        "whatsapp",
        "work from home"
    }

    # Extract organizations identified by spaCy
    for entity in doc.ents:
        if entity.label_ == "ORG":
            organizations.append(entity.text.strip())

    # Supplement spaCy with contextual extraction
    organizations.extend(
        extract_contextual_organizations(job_description)
    )

    # Filter false positives and remove duplicates
    organizations = [
        name for name in organizations
        if name.lower().strip() not in ignored_names
    ]

    return {
        "nouns": unique_words(nouns),
        "verbs": unique_words(verbs),
        "organizations": unique_words(organizations)
    }
