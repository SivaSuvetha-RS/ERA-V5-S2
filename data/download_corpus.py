import requests
from pathlib import Path

LANGUAGES = {
    "english": ("en", "India"),
    "hindi": ("hi", "भारत"),
    "telugu": ("te", "భారతదేశం"),
    "kannada": ("kn", "ಭಾರತ"),
}

OUTPUT_DIR = Path("data/corpus")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def download_wikipedia_article(language_code, title):
    url = (
        f"https://{language_code}.wikipedia.org/w/api.php"
    )

    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "titles": title,
        "format": "json",
        "redirects": 1,
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
        headers={"User-Agent": "ERA-V5-S2-tokenizer/1.0"},
    )
    response.raise_for_status()

    data = response.json()
    pages = data["query"]["pages"]

    page = next(iter(pages.values()))
    text = page.get("extract", "").strip()

    if not text:
        raise RuntimeError(
            f"No text was returned for {language_code}"
        )

    return text


def main():
    for language, (code, title) in LANGUAGES.items():
        print(f"Downloading {language}...")

        text = download_wikipedia_article(code, title)

        output_file = OUTPUT_DIR / f"{language}.txt"
        output_file.write_text(text, encoding="utf-8")

        print(
            f"Saved {len(text):,} characters to {output_file}"
        )


if __name__ == "__main__":
    main()
