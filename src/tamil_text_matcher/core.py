from typing import List, Dict, Union, Tuple, Optional
from rapidfuzz import distance, fuzz
from .encoder import TamilPhoneticEncoder

_encoder = TamilPhoneticEncoder()

def compare(s1: str, s2: str, threshold: int = 80) -> Dict[str, Union[bool, int, float, str]]:
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

    # Step 1: Phonetic Encoding
    enc_s1 = _encoder.encode(s1)
    enc_s2 = _encoder.encode(s2)
    
    if enc_s1 and enc_s1 == enc_s2:
        return {'match': True, 'score': 100.0, 'method': 'encoded_exact'}
        
    # Step 2: Jaro-Winkler on Phonetic Strings
    # rapidfuzz.distance.JaroWinkler.similarity returns 0.0-1.0, we want 0-100
    jw_score = distance.JaroWinkler.similarity(enc_s1, enc_s2) * 100
    if jw_score >= threshold:
        return {'match': True, 'score': jw_score, 'method': 'phonetic_jw'}
        
    # Step 3: Fallback - Token/Partial Matching (Original Strings)
    # This handles "R. Ravi" vs "Ravi" where phonetic might differ 
    # (e.g. 'rravi' vs 'ravi' or 'arravi' if sounded out, but token set handles it best).
    
    # token_set_ratio: Intersection of tokens. Good for "Senthil Kumar" vs "Kumar Senthil"
    token_set = fuzz.token_set_ratio(s1, s2)
    
    # token_sort_ratio: Sorted tokens. Good for "Senthil Kumar" vs "Kumar Senthil"
    token_sort = fuzz.token_sort_ratio(s1, s2)
    
    # partial_ratio: Substring matching. Good for "Senthil" vs "Senthil Kumar"
    partial = fuzz.partial_ratio(s1, s2)
    
    max_fuzzy = max(token_set, token_sort, partial)
    
    if max_fuzzy >= threshold:
         return {'match': True, 'score': float(max_fuzzy), 'method': 'fuzzy_token'}
         
    # Return best score found even if no match
    best_score = max(jw_score, float(max_fuzzy))
    return {'match': False, 'score': best_score, 'method': 'none'}

def find_best_match(query: str, candidates: List[str], threshold: int = 80) -> Optional[Tuple[str, float, str]]:
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
        result = compare(query, candidate, threshold)
        if result['score'] > best_result['score']:
            best_result = result
            best_candidate = candidate
            
    if best_result['match']:
        return (best_candidate, best_result['score'], best_result['method'])
    
    return None
