"""Utility functions for BibTeX to RFC conversion."""

import re

def latex_to_unicode(text: str) -> str:
    """Convert LaTeX accents and special characters to Unicode.
    
    Args:
        text: A string containing LaTeX accents and special characters.
    Returns:
        A string with LaTeX accents and special characters converted to Unicode.
    """
    if not text:
        return text

    # Mapping for LaTeX accents to Unicode
    accent_map = {
        "'": {
            'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú', 'y': 'ý',
            'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú', 'Y': 'Ý',
        },
        '`': {
            'a': 'à', 'e': 'è', 'i': 'ì', 'o': 'ò', 'u': 'ù',
            'A': 'À', 'E': 'È', 'I': 'Ì', 'O': 'Ò', 'U': 'Ù',
        },
        '"': {
            'a': 'ä', 'e': 'ë', 'i': 'ï', 'o': 'ö', 'u': 'ü', 'y': 'ÿ',
            'A': 'Ä', 'E': 'Ë', 'I': 'Ï', 'O': 'Ö', 'U': 'Ü', 'Y': 'Ÿ',
        },
        '^': {
            'a': 'â', 'e': 'ê', 'i': 'î', 'o': 'ô', 'u': 'û',
            'A': 'Â', 'E': 'Ê', 'I': 'Î', 'O': 'Ô', 'U': 'Û',
        },
        '~': {
            'a': 'ã', 'n': 'ñ', 'o': 'õ',
            'A': 'Ã', 'N': 'Ñ', 'O': 'Õ',
        },
        'c': {
            'c': 'ç', 'C': 'Ç',
        },
        'v': {
            's': 'š', 'S': 'Š', 'z': 'ž', 'Z': 'Ž', 'c': 'č', 'C': 'Č',
        },
        'u': {
            'g': 'ğ', 'G': 'Ğ',
        },
        '.': {
            'I': 'İ',
        },
    }

    def replace_accented(match):
        accent = match.group(1)
        char = match.group(2)
        return accent_map.get(accent, {}).get(char, match.group(0))

    # Curly-brace form: {\'e}
    text = re.sub(r'\{\\(["\'`^~cvu.])([a-zA-Z])\}', replace_accented, text)
    # Direct form: \'e
    text = re.sub(r'\\(["\'`^~cvu.])([a-zA-Z])', replace_accented, text)

    # Remove any remaining curly braces
    text = text.replace("{", "").replace("}", "")
    return text 