# IndiaBPE: Multilingual BPE Tokenizer

This project trains one shared 10,000-token BPE vocabulary on the English,
Hindi, Telugu, and Kannada Wikipedia articles for India. The widget tokenizes
input, shows each token and ID, reports article-level fertility, calculates the
assignment score, and downloads the complete vocabulary as JSON.

## Article Sources

- English: <https://en.wikipedia.org/wiki/India>
- Hindi: <https://hi.wikipedia.org/wiki/%E0%A4%AD%E0%A4%BE%E0%A4%B0%E0%A4%A4>
- Telugu: <https://te.wikipedia.org/wiki/%E0%B0%AD%E0%B0%BE%E0%B0%B0%E0%B0%A4%E0%B0%A6%E0%B1%87%E0%B0%B6%E0%B0%82>
- Kannada: <https://kn.wikipedia.org/wiki/%E0%B2%AD%E0%B2%BE%E0%B2%B0%E0%B2%A4>

`data/corpus/*.txt` contains the plaintext snapshots used by the checked-in
tokenizer and metrics. Wikipedia articles change over time; rerun all steps
below after downloading new snapshots before making claims about scores.

## Reproduce

From the repository root, install the dependencies and run:

```sh
pip install -r requirements.txt
python data/download_corpus.py
python tokenizer/train_tokenizer.py
python evaluation/evaluation_tokenizer.py
python web/app.py
```

Open <http://127.0.0.1:8000/>. The training weights are English 8, Hindi 1,
Telugu 7, and Kannada 6 passes over the same article snapshots. Training uses
BPE with `WhitespaceSplit` pre-tokenization and a `##` continuation prefix,
with a single vocabulary of 10,000 entries. Decoding normalizes whitespace to
single spaces.

## Metric Definition

For each article, fertility is `encoded token count / whitespace-delimited
word count`. The four language fertilities are sorted ascending to produce
X1–X4. The assignment score is `1000 / (X4 - X1)`. The English requirement is
checked separately and must be at most 1.2. The widget reads the generated
`evaluation/metrics.json`; it does not hardcode score claims.

The vocabulary download at `/api/vocab` is JSON containing all 10,000 token
strings and their IDs, sorted by ID. Deploy the Flask application (not only
the static HTML) to a host that supports Python so its tokenizer and API routes
are available to the widget. A Render Blueprint is provided in `render.yaml`;
connect this repository to Render to create a public service URL. This local
workspace cannot create that public URL without access to a hosting account.