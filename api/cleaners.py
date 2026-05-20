import re

def normalize_fuvest_2026(text: str) -> str:
    """
    Cleans up encoding oddities in FUVEST 2026.
    Specifically:
    - \u00ac (not sign '¬') maps to space character
    """
    if not text:
        return ""
    # Replace \u00ac with normal space
    text = text.replace("\u00ac", " ")
    # Replace double spaces and strip
    text = re.sub(r' +', ' ', text)
    return text.strip()

def normalize_pism_accents(text: str) -> str:
    """
    Normalizes separated overlay accents commonly found in PISM exams (which are compiled with LaTeX).
    For example:
    - Gradua\u00b8 c\u02dc ao -> Graduação
    - Coordena\u00b8 c\u02dc ao -> Coordenação
    - Quest\u02dc ao -> Questão
    - Pr\u00b4 o -> Pró
    - M\u00b4 odulo -> Módulo
    """
    if not text:
        return ""

    # Replace space-accent combinations and separate characters
    replacements = [
        # Cedilla + c
        (r'\u00b8\s*c', 'ç'),
        (r'c\s*\u00b8', 'ç'),
        (r'\u00b8\s*C', 'Ç'),
        (r'C\s*\u00b8', 'Ç'),

        # Tilde combinations
        (r'a\s*\u02dc\s*o', 'ão'),
        (r'\u02dc\s*ao', 'ão'),
        (r'a\s*\u02dc', 'ã'),
        (r'\u02dc\s*a', 'ã'),
        (r'o\s*\u02dc', 'õ'),
        (r'\u02dc\s*o', 'õ'),
        (r'A\s*\u02dc\s*O', 'ÃO'),
        (r'A\s*\u02dc', 'Ã'),

        # Acute accents
        (r'\u00b4\s*a', 'á'),
        (r'a\s*\u00b4', 'á'),
        (r'\u00b4\s*e', 'é'),
        (r'e\s*\u00b4', 'é'),
        (r'\u00b4\s*i', 'í'),
        (r'i\s*\u00b4', 'í'),
        (r'\u00b4\s*o', 'ó'),
        (r'o\s*\u00b4', 'ó'),
        (r'\u00b4\s*u', 'ú'),
        (r'u\s*\u00b4', 'ú'),
        (r'\u00b4\s*A', 'Á'),
        (r'\u00b4\s*E', 'É'),
        (r'\u00b4\s*I', 'Í'),
        (r'\u00b4\s*O', 'Ó'),
        (r'\u00b4\s*U', 'Ú'),

        # Circumflex accents
        (r'\u02c6\s*a', 'â'),
        (r'a\s*\u02c6', 'â'),
        (r'\u02c6\s*e', 'ê'),
        (r'e\s*\u02c6', 'ê'),
        (r'\u02c6\s*o', 'ô'),
        (r'o\s*\u02c6', 'ô'),
        (r'\u02c6\s*A', 'Â'),
        (r'\u02c6\s*E', 'Ê'),
        (r'\u02c6\s*O', 'Ô'),

        # Grave accents
        (r'\u0060\s*a', 'à'),
        (r'a\s*\u0060', 'à'),
        (r'\u0060\s*A', 'À'),
    ]

    result = text
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)

    # Clean double spaces
    result = re.sub(r' +', ' ', result)
    return result.strip()

def clean_exam_text(text: str, exam_type: str) -> str:
    """
    Dispatches cleaning to appropriate normalizer based on the exam type.
    """
    if not text:
        return ""
    
    # Standard spacing cleanups
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    if "FUVEST" in exam_type.upper():
        # FUVEST 2026 uses \u00ac, let's run FUVEST-specific normalizations
        text = normalize_fuvest_2026(text)
    elif "PISM" in exam_type.upper():
        # PISM uses separated accents
        text = normalize_pism_accents(text)
        
    # General cleanup (e.g. replace soft hyphens or weird spaces)
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    text = re.sub(r'\n{3,}', '\n\n', text) # Collapse multiple newlines
    return text.strip()
