# Tamil Text Matcher

A Python package primarily intended for matching Tamil names that have been transliterated to English. It effectively handles varied spellings, phonetic similarities, and structural differences such as initials appearing at the start or end.

## Installation

It is highly recommended to use a virtual environment for your project.

### Install from Git
You can install the package directly from the GitHub repository:

```bash
pip install git+https://github.com/ilankumarann/tamil-text-matcher.git
```

### Using requirements.txt
Alternatively, you can include the repository URL in your `requirements.txt` file:

```text
git+https://github.com/ilankumarann/tamil-text-matcher.git
```

Then install the dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Comparing Two Strings
Use the `compare` function to check the similarity between two strings. It employs a multi-stage approach, checking for phonetic matches first and falling back to fuzzy token matching for structural differences (like reordered names or initials).

```python
from tamil_text_matcher import compare

# Example 1: Phonetic similarity (Bharathi vs Barathi)
result = compare("Bharathi", "Barathi")
print(f"Match: {result['match']}, Score: {result['score']}, Method: {result['method']}")
# Output: Match: True, Score: 95.8..., Method: phonetic_jw

# Example 2: Structural difference with initials (R. Ravi vs Ravi)
result = compare("R. Ravi", "Ravi")
print(f"Match: {result['match']}, Score: {result['score']}, Method: {result['method']}")
# Output: Match: True, Score: 100.0, Method: fuzzy_token
```

### Finding the Best Match
Use `find_best_match` to retrieve the best matching candidate for a query string from a list of options.

```python
from tamil_text_matcher import find_best_match

candidates = ["Ravi", "Senthil", "Ganesh", "Muthu", "Barathi"]
query = "Tamiz"

# Note: 'Tamiz' and 'Tamil' (not in list) might be phonetically similar, 
# but here lets try a known match or no match scenario.
# Let's try matching "Kanesh" to "Ganesh"
match = find_best_match("Kanesh", candidates)

if match:
    best_candidate, score, method = match
    print(f"Best match for 'Kanesh' is '{best_candidate}' with score {score} using {method}")
else:
    print("No match found.")
```