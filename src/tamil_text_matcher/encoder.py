import re

class TamilPhoneticEncoder:
    """
    Encodes transliterated Tamil text into a simplified phonetic representation.
    Handles user-specified rules:
    - v:w, z:s maps
    - Alveolar/Velar/Bilabial mapping (Voiced -> Unvoiced)
    - Nasals (m, n) grouping
    - Liquids (l, r) grouping
    - Silent h
    - Long vowel distinction
    """

    def encode(self, text: str) -> str:
        if not text:
            return ""
        
        # 0. Basic Cleanup
        text = text.lower()
        text = re.sub(r'[^a-z]', '', text) # Keep only letters for encoding logic
        
        if not text:
            return ""

        # 1. Normalize Long Vowels FIRST (to preserve 'aa' before 'a' logic if needed, 
        # but replacement order handles it).
        # User constraint: "kaa means tamil letter nedil ka" -> Keep distinction.
        text = text.replace("aa", "A")
        text = text.replace("ee", "E")
        text = text.replace("ii", "I")
        text = text.replace("oo", "O")
        text = text.replace("uu", "U")
        
        # 2. Handle Equivalence Mappings (v:w, z:s)
        text = text.replace("w", "v")
        text = text.replace("z", "s")
        
        # 3. Silent 'h'
        # Removing 'h' handles 'bh'->'b', 'th'->'t', 'dh'->'d', 'sh'->'s' etc.
        # This effectively de-aspirates and simplifies sibilants/dentals.
        text = text.replace("h", "")
        
        # 4. Voicing Normalization (Voiced -> Unvoiced)
        # Velar: g -> k
        # Bilabial: b -> p
        # Dental/Retroflex: d -> t
        # Palatal/Affricate: j -> s (or c -> s)
        
        text = text.replace("g", "k")
        text = text.replace("b", "p")
        text = text.replace("d", "t")
        text = text.replace("j", "s")
        text = text.replace("c", "s") # 'ch' became 'c' after 'h' removal. Map 'c' to 's'.
        text = text.replace("f", "p") # 'f' is often 'p' or 'ph'
        
        # 5. Grouping Nasals and Liquids (as per "nasals like mn", "liquids like lr")
        # This reduces precision but increases fuzzy match recall for these confusion points.
        text = text.replace("m", "n") 
        text = text.replace("r", "l")
        
        # 6. Squeeze Repeats
        # 'pattu' -> 'patu', 'kann' -> 'kan'
        # Logic: replace any char repeated with single char.
        # (Regex backreference)
        text = re.sub(r'(.)\1+', r'\1', text)
        
        return text
