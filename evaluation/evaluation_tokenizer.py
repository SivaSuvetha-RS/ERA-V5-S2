from pathlib import Path
from tokenizers import Tokenizer
import json

ROOT = Path(__file__).resolve().parents[1]
TOKENIZER_FILE = ROOT / "tokenizer" / "tokenizer.json"
CORPUS_DIR = ROOT / "data" / "corpus"
OUTPUT_FILE = ROOT / "evaluation" / "metrics.json"

LANGUAGES = ["english", "hindi", "telugu", "kannada"]
ENGLISH_FERTILITY_LIMIT = 1.2



def main():
    tokenizer = Tokenizer.from_file(str(TOKENIZER_FILE))

    results = {}

    for language in LANGUAGES:
        corpus_file = CORPUS_DIR / f"{language}.txt"
        text = corpus_file.read_text(encoding="utf-8")

        encoding = tokenizer.encode(text)

        token_count = len(encoding.ids)
        word_count = len(text.split())

        fertility = token_count / word_count

        results[language] = {
            "tokens": token_count,
            "words": word_count,
            "fertility": fertility,
        }

    ranked_languages = sorted(
        LANGUAGES,
        key=lambda language: results[language]["fertility"],
    )
    ranked_values = [
        results[language]["fertility"]
        for language in ranked_languages
    ]
    x1, x2, x3, x4 = ranked_values

    spread = x4 - x1

    score = 1000 / spread if spread > 0 else 0

    output = {
        "languages": results,
        "rankings": [
            {
                "rank": f"X{index}",
                "language": language,
                "fertility": results[language]["fertility"],
            }
            for index, language in enumerate(ranked_languages, start=1)
        ],
        "x1": x1,
        "x2": x2,
        "x3": x3,
        "x4": x4,
        "spread": spread,
        "score": score,
        "vocab_size": tokenizer.get_vocab_size(),
        "english_target": ENGLISH_FERTILITY_LIMIT,
        "english_target_met": (
            results["english"]["fertility"] <= ENGLISH_FERTILITY_LIMIT
        ),
        "word_count_method": "whitespace-delimited words",
    }

    OUTPUT_FILE.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n=== TOKENIZER EVALUATION ===")

    for language in LANGUAGES:
        data = results[language]
        print(
            f"{language.title():8} "
            f"tokens={data['tokens']:,} "
            f"words={data['words']:,} "
            f"fertility={data['fertility']:.6f}"
        )

    print()
    for ranking in output["rankings"]:
        print(
            f"{ranking['rank']} ({ranking['language']}) "
            f"= {ranking['fertility']:.6f}"
        )
    print(f"Spread = {spread:.6f}")
    print(f"Score  = {score:.2f}")
    print(
        "English <= 1.2: "
        + ("PASS" if output["english_target_met"] else "FAIL")
    )
    print(f"Vocabulary size: {output['vocab_size']:,}")
    print()
    print(f"Saved metrics to {OUTPUT_FILE}")



if __name__ == "__main__":
    main()
