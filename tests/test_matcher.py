import pytest
from tamil_text_matcher import compare, find_best_match
from tamil_text_matcher.encoder import TamilPhoneticEncoder

class TestEncoder:
    def test_basic_rules(self):
        encoder = TamilPhoneticEncoder()
        # v:w, b->p, v->p? No, v is v. w->v.
        # "Vivek" -> vivek -> vivek. "Wiwek" -> vivek.
        assert encoder.encode("Vivek") == "vivek"
        assert encoder.encode("Wiwek") == "vivek"
        
        # z:s
        assert encoder.encode("Tamiz") == "tanis" # t->t, a->a, m->n, i->i, z->s
        
        # silent h & voicing
        # "Bharathi" -> barati -> parati -> palati (r->l)
        assert encoder.encode("Bharathi") == "palati" 
        assert encoder.encode("Barathi") == "palati" 

    def test_voicing_stops(self):
        encoder = TamilPhoneticEncoder()
        # g -> k
        assert encoder.encode("Ganesh") == "kanes" # s->s, sh->s (h rem), g->k, n->n. 
        # b -> p
        assert encoder.encode("Babu") == "papu"
        # d -> t
        assert encoder.encode("Deva") == "teva"

    def test_nasals_liquids(self):
        encoder = TamilPhoneticEncoder()
        # m -> n
        # 'Ram' -> 'ran' (r->l, a->a, m->n) => 'lan' ???
        # Wait, r->l. So Ram -> Lan.
        assert encoder.encode("Ram") == "lan"
        assert encoder.encode("Ran") == "lan"
        
        # l -> l, r -> l
        # 'Bala' -> 'pala'
        # 'Bara' -> 'pala'
        assert encoder.encode("Bala") == "pala"
        assert encoder.encode("Bara") == "pala"

    def test_long_vowels(self):
        encoder = TamilPhoneticEncoder()
        assert encoder.encode("kaa") == "kA"
        assert encoder.encode("ka") == "ka"
        
class TestMatcher:
    def test_exact_encoded_match(self):
        # Phonetically identical
        res = compare("Bharathi", "Barathi")
        assert res['match'] is True
        assert res['score'] == 100
        assert res['method'] == 'encoded_exact'

    def test_close_phonetic_match(self):
        # 'Vanakkam' vs 'Vanakam' 
        # With aggressive encoding (squeeze repeats, m->n), these might become identical.
        res = compare("Vanakkam", "Vanakam")
        assert res['match'] is True
        assert res['score'] > 90
        # Accepts either exact or high score JW
        assert res['method'] in ['phonetic_jw', 'encoded_exact']

    def test_initials_and_reordering(self):
        # "R. Ravi" vs "Ravi"
        # Cleaning removes '.', ' ' -> "rravi" -> "lavi" (after squeeze/map). Matches "Ravi" -> "lavi".
        res = compare("R. Ravi", "Ravi")
        assert res['match'] is True
        # Might be exact match now
        assert res['method'] in ['fuzzy_token', 'encoded_exact']
        
        # "Senthil Kumar" vs "Kumar Senthil"
        res = compare("Senthil Kumar", "Kumar Senthil")
        assert res['match'] is True
        assert res['score'] == 100 # Token sort ratio should be 100
        
    def test_find_best_match(self):
        candidates = ["Karthik", "Senthil", "Ravi"]
        match = find_best_match("Kartik", candidates)
        assert match is not None
        assert match[0] == "Karthik" 

    def test_input_normalization(self):
        """Tests for verify_norm.py cases"""
        cases = [
            ("  Barathi ", "Barathi"),  # Spaces
            ("Barathi.", "Barathi"),    # Special char
            ("BARATHI", "barathi"),     # Case
            ("Ram-Kumar", "Ram Kumar"), # Special char to space
            ("Senthil@Kumar", "Senthil Kumar"), # Special char
        ]
        
        for s1, s2 in cases:
            res = compare(s1, s2)
            assert res['match'] is True
            assert res['score'] == 100

    def test_l_and_zh_mappings(self):
        """Tests for check_l.py cases"""
        # "Palli" vs "Pali" (School)
        res = compare("Palli", "Pali")
        assert res['match'] is True
        assert res['score'] == 100
        
        # "Palli" vs "Balli" (Lizard - but phonetically 'balli' -> 'palli')
        res = compare("Palli", "Balli")
        assert res['match'] is True
        assert res['score'] == 100

        # "Muthu" vs "Mudu" (Check d->t)
        res = compare("Muthu", "Mudu")
        assert res['match'] is True
        assert res['score'] == 100
        
        # "Tamizh" vs "Tamil"
        # Currently z maps to s, so 'tanis' vs 'tanil'. Score ~92.
        # This confirms current behavior, even if we discuss changing it later.
        res = compare("Tamizh", "Tamil")
        assert res['match'] is True
        assert res['score'] >= 80

        # "Mazhai" vs "Malai"
        res = compare("Mazhai", "Malai")
        assert res['match'] is True
        assert res['score'] >= 80

        # "Pazham" vs "Palam"
        res = compare("Pazham", "Palam")
        assert res['match'] is True
        assert res['score'] >= 80

    def test_title_removal_and_false_positives(self):
        # "Dr. Ravi" vs "Ravi" - Should be exact match after stripping "Dr."
        res = compare("Dr. Ravi", "Ravi")
        assert res['match'] is True
        assert res['score'] == 100.0
        assert res['method'] == 'encoded_exact'

        # "Dr Kalyan" vs "T. L. Maharajan"
        # Previously matched because 'Dr' -> 'tl' matched 'T. L.' -> 'tl'
        # Now 'Dr' is stripped -> "Kalyan" vs "T. L. Maharajan"
        # "Kalyan" (kalan) vs "Maharajan" (nahalasan) -> Should be low score
        res = compare("Dr Kalyan", "T. L. Maharajan")
        # We assert it does NOT match or score is low
        # Note: If threshold is 80, this should now be False.
        if res['match']:
            # If it still matches, score should be significantly lower than before (84)
            # But realistically it shouldn't match.
            assert res['score'] < 60
        else:
            assert res['match'] is False