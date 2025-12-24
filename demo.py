from tamil_text_matcher import compare
from tamil_text_matcher.encoder import TamilPhoneticEncoder

encoder = TamilPhoneticEncoder()
examples = [
    ("Bharathi", "Barathi"),
    ("Vanakkam", "Vanakam"), # k vs kk -> squeezed? lets see.
    ("R. Ravi", "Ravi"),
    ("Senthil Kumar", "Kumar Senthil"),
    ("Vivek", "Wiwek"),
    ("Ganesh", "Kanesh"),
    ("Tamiz", "Tamil"), # z vs l? z->s, l->l. 'tanis' vs 'tamil'. match?
    ("Muthu", "Mudu"),
]

print(f"{'String 1':<15} | {'String 2':<15} | {'Enc 1':<8} | {'Enc 2':<8} | {'Match':<5} | {'Score':<5} | {'Method'}")
print("-" * 90)

for s1, s2 in examples:
    res = compare(s1, s2)
    enc1 = encoder.encode(s1)
    enc2 = encoder.encode(s2)
    print(f"{s1:<15} | {s2:<15} | {enc1:<8} | {enc2:<8} | {str(res['match']):<5} | {res['score']:<5.1f} | {res['method']}")
