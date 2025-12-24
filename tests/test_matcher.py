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
