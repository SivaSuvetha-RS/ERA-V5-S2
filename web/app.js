const language = document.getElementById("language");
const text = document.getElementById("text");

const tokenizeBtn = document.getElementById("tokenizeBtn");
const sampleBtn = document.getElementById("sampleBtn");
const clearBtn = document.getElementById("clearBtn");

const errorBox = document.getElementById("error");
const emptyResult = document.getElementById("emptyResult");
const resultContent = document.getElementById("resultContent");

const tokenCount = document.getElementById("tokenCount");
const tokensBox = document.getElementById("tokens");
const tokenIds = document.getElementById("tokenIds");
const decoded = document.getElementById("decoded");

const samples = {
    english: "India is a diverse country with many languages and cultures.",
    hindi: "भारत एक विविधतापूर्ण देश है।",
    telugu: "భారతదేశం ఒక వైవిధ్యమైన దేశం.",
    kannada: "ಭಾರತವು ವೈವಿಧ್ಯಮಯ ದೇಶವಾಗಿದೆ."
};



function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.add("show");
}



function clearError() {
    errorBox.textContent = "";
    errorBox.classList.remove("show");
}



async function tokenize() {
    clearError();

    const input = text.value.trim();

    if (!input) {
        showError("Please enter some text first.");
        return;
    }

    tokenizeBtn.disabled = true;
    tokenizeBtn.textContent = "Tokenizing...";

    try {
        const response = await fetch("/api/tokenize", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: input
            })
        });

        let data;
        try {
            data = await response.json();
        } catch {
            throw new Error("The tokenizer returned an invalid response.");
        }

        if (!response.ok) {
            throw new Error(data.error || "Tokenization failed.");
        }

        if (
            !Array.isArray(data.tokens) ||
            !Array.isArray(data.ids) ||
            data.tokens.length !== data.ids.length ||
            typeof data.decoded !== "string"
        ) {
            throw new Error("The tokenizer returned incomplete results.");
        }

        tokenCount.textContent = data.ids.length;

        tokensBox.innerHTML = "";

        data.tokens.forEach((token, index) => {
            const chip = document.createElement("span");
            chip.className = "token";

            const tokenText = document.createElement("span");
            tokenText.className = "token-text";
            tokenText.textContent = token;

            const tokenId = document.createElement("small");
            tokenId.className = "token-id";
            tokenId.textContent = `ID ${data.ids[index]}`;

            chip.title = `Token ${index + 1} | ID ${data.ids[index]}`;
            chip.append(tokenText, tokenId);

            tokensBox.appendChild(chip);
        });

        tokenIds.textContent = `[ ${data.ids.join(", ")} ]`;

        decoded.textContent = data.decoded;

        emptyResult.style.display = "none";
        resultContent.classList.add("show");

    } catch (error) {
        console.error(error);

        showError(
            error.message ||
            "Unable to connect to the tokenizer backend."
        );

    } finally {
        tokenizeBtn.disabled = false;
        tokenizeBtn.textContent = "Tokenize Text";
    }
}



sampleBtn.addEventListener("click", () => {
    text.value = samples[language.value];
    tokenize();
});



clearBtn.addEventListener("click", () => {
    text.value = "";

    tokenCount.textContent = "0";
    tokensBox.innerHTML = "";
    tokenIds.textContent = "—";
    decoded.textContent = "—";

    resultContent.classList.remove("show");
    emptyResult.style.display = "block";

    clearError();
});



tokenizeBtn.addEventListener("click", tokenize);



text.addEventListener("keydown", event => {
    if (event.ctrlKey && event.key === "Enter") {
        tokenize();
    }
});



async function loadMetrics() {
    try {
        const response = await fetch("/api/metrics");

        if (!response.ok) {
            throw new Error("Metrics could not be loaded.");
        }

        const metrics = await response.json();

        const languages = metrics.languages || {};

        const order = [
            "english",
            "hindi",
            "telugu",
            "kannada"
        ];

        const cards = document.querySelectorAll(".metric");

        cards.forEach((card, index) => {
            const data = languages[order[index]];

            if (!data) return;

            card.querySelector(".fertility").textContent =
                Number(data.fertility).toFixed(3);

            const mini = document.createElement("div");
            mini.className = "mini";

            mini.textContent =
                `Tokens: ${Number(data.tokens).toLocaleString()} | ` +
                `Words: ${Number(data.words).toLocaleString()}`;

            card.appendChild(mini);
        });

        metrics.rankings.forEach((ranking, index) => {
            const number = index + 1;
            document.getElementById(`x${number}Label`).textContent =
                `${ranking.rank} | ${ranking.language[0].toUpperCase()}${ranking.language.slice(1)}`;
            document.getElementById(`x${number}`).textContent =
                Number(ranking.fertility).toFixed(3);
        });

        document.getElementById("spread").textContent =
            Number(metrics.spread).toFixed(3);

        document.getElementById("score").textContent =
            Number(metrics.score).toFixed(2);

        document.getElementById("vocabSize").textContent =
            Number(metrics.vocab_size).toLocaleString();

        const englishTargetStatus =
            document.getElementById("englishTargetStatus");
        englishTargetStatus.textContent = metrics.english_target_met
            ? `Met (${Number(languages.english.fertility).toFixed(3)} <= 1.2)`
            : `Not met (${Number(languages.english.fertility).toFixed(3)} > 1.2)`;
        englishTargetStatus.dataset.met = metrics.english_target_met;

    } catch (error) {
        console.error("Metrics error:", error);
    }
}



loadMetrics();