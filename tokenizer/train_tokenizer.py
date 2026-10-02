from pathlib import Path
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import WhitespaceSplit
from tokenizers.decoders import WordPiece
from tokenizers.trainers import BpeTrainer

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "data" / "corpus"
OUTPUT_DIR = ROOT / "tokenizer"

LANGUAGES = ["english", "hindi", "telugu", "kannada"]
LANGUAGE_WEIGHTS = {
    "english": 8,
    "hindi": 1,
    "telugu": 7,
    "kannada": 6,
}
VOCAB_SIZE = 10_000



def main():
    corpus_files = [
        str(CORPUS_DIR / f"{language}.txt")
        for language in LANGUAGES
        for _ in range(LANGUAGE_WEIGHTS[language])
    ]

    print("Training multilingual BPE tokenizer...")
    print("Languages:", ", ".join(LANGUAGES))
    print("Vocabulary size:", VOCAB_SIZE)

    tokenizer = Tokenizer(
        BPE(
            unk_token="[UNK]",
            continuing_subword_prefix="##",
        )
    )

    tokenizer.pre_tokenizer = WhitespaceSplit()
    tokenizer.decoder = WordPiece(prefix="##", cleanup=False)

    trainer = BpeTrainer(
        vocab_size=VOCAB_SIZE,
        special_tokens=["[UNK]"],
        continuing_subword_prefix="##",
        show_progress=True,
    )

    tokenizer.train(
        files=corpus_files,
        trainer=trainer,
    )

    output_file = OUTPUT_DIR / "tokenizer.json"
    tokenizer.save(str(output_file))

    print()
    print("Training complete.")
    print("Vocabulary size:", tokenizer.get_vocab_size())
    print("Saved to:", output_file)



if __name__ == "__main__":
    main()
