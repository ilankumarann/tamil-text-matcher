from typing import List, Dict, Union, Tuple, Optional
import re
from rapidfuzz import distance, fuzz
from .encoder import TamilPhoneticEncoder

_encoder = TamilPhoneticEncoder()

def compare(s1: str, s2: str, threshold: int = 80, use_jw: bool = False) -> Dict[str, Union[bool, int, float, str]]:
    """
    Compares two transliterated Tamil strings using a multi-stage approach.
    
    Stages:
    1. Phonetic Encoded Exact Match: Checks if phonetic representations are identical.
    2. Phonetic Encoded Jaro-Winkler: Checks phonetic similarity.
    3. Fuzzy Token/Partial Match: Checks original strings for structural matches 
       (handling initials, reordering, partial names).
       
    Args:
        s1: First string.
        s2: Second string.
        threshold: Score threshold to consider a match (0-100).
        
    Returns:
        Dict containing 'match' (bool), 'score' (float), and 'method' (str).
    """
    if not s1 or not s2:
        return {'match': False, 'score': 0, 'method': 'none'}

    # Step 0: Input Normalization
    # Convert to lower, strip whitespace, and replace special chars with space
    # (Preserving spaces is important for token_set_ratio)
    def clean(text):
        if not text: return ""
        text = text.lower()
        
        # Remove common titles
        # Must be at start of string, followed by space or optional dot then space
        text = re.sub(r'^(dr|mr|mrs|miss|er)\.?\s+', '', text)
        
        # Replace non-alphanumeric with space
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    s1_clean = clean(s1)
    s2_clean = clean(s2)
    
    if not s1_clean or not s2_clean:
         return {'match': False, 'score': 0, 'method': 'none'}

    # Step 1: Phonetic Encoding
    # encoder.encode handles its own cleaning (stripping non-alpha), so passing s1/s1_clean is fine.
    # We pass s1_clean for consistency, though encoder removes spaces anyway.
    enc_s1 = _encoder.encode(s1_clean)
    enc_s2 = _encoder.encode(s2_clean)
    
    if enc_s1 and enc_s1 == enc_s2:
        return {'match': True, 'score': 100.0, 'method': 'encoded_exact'}
        
    # Step 2: Jaro-Winkler on Phonetic Strings
    # rapidfuzz.distance.JaroWinkler.similarity returns 0.0-1.0, we want 0-100
    # Step 2: Jaro-Winkler on ORIGINAL Normalized Strings
    # User feedback: Phonetic JW is too enthusiastic.
    # JW on original strings handles typos (e.g. Tamizh vs Tamil) better.
    # OPTIONAL: Only run if use_jw is True
    jw_score = 0
    if use_jw:
        jw_score = distance.JaroWinkler.similarity(s1_clean, s2_clean) * 100
    
    # Store potential result
    best_res = {'match': False, 'score': 0, 'method': 'none'}
    
    if use_jw and jw_score >= threshold:
        best_res = {'match': True, 'score': jw_score, 'method': 'jaro_winkler'}
        # If perfect match found, return immediately
        if jw_score == 100.0:
            return best_res

    # Step 3: Fallback - Token/Partial Matching (Original Strings)
    # Use cleaned strings (lowercase, space-normalized)
    
    # token_set_ratio: Intersection of tokens. Good for "Senthil Kumar" vs "Kumar Senthil"
    token_set = fuzz.token_set_ratio(s1_clean, s2_clean)
    
    # token_sort_ratio: Sorted tokens. Good for "Senthil Kumar" vs "Kumar Senthil"
    token_sort = fuzz.token_sort_ratio(s1_clean, s2_clean)
    
    # partial_ratio REMOVED: potentially dangerous for names (e.g. "Harini" vs "Bhavatharini" -> 100)
    # token_set handles "Senthil" vs "Senthil Kumar" properly.
    
    max_fuzzy = max(token_set, token_sort)
    
    # Use fuzzy token score if it's better than phonetic score and meets threshold
    if max_fuzzy >= threshold and max_fuzzy > best_res['score']:
         return {'match': True, 'score': float(max_fuzzy), 'method': 'fuzzy_token'}
    
    # Return whatever we found (either phonetic match or no match)
    if best_res['match']:
        return best_res
         
    # Return best score found even if no match
    overall_best = max(jw_score, float(max_fuzzy))
    return {'match': False, 'score': overall_best, 'method': 'none'}

def find_best_match(query: str, candidates: List[str], threshold: int = 80, use_jw: bool = False) -> Optional[Tuple[str, float, str]]:
    """
    Finds the best match for a query string from a list of candidates.
    
    Args:
        query: Transliterated Tamil string to search for.
        candidates: List of candidate strings.
        threshold: Minimum score to accept result.
        
    Returns:
        Tuple of (best_candidate, score, method) or None if no match meets threshold.
    """
    best_candidate = None
    best_result = {'score': -1, 'match': False}
    
    for candidate in candidates:
        result = compare(query, candidate, threshold, use_jw=use_jw)
        if result['score'] > best_result['score']:
            best_result = result
            best_candidate = candidate
            
    if best_result['match']:
        return (best_candidate, best_result['score'], best_result['method'])
    
    return None
