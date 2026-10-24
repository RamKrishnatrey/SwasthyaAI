from pathlib import Path
import re
import joblib

MODEL_PATH = Path(
    r"C:\Users\Manish\SwasthyaAI\models\best_official_split_model.joblib"
)

EMERGENCY_PATTERNS = {
    "possible cardiac emergency": r"\b(chest pain|chest pressure)\b",
    "severe breathing difficulty": r"\b(can't breathe|cannot breathe|severe shortness of breath|gasping for air)\b",
    "possible stroke": r"\b(face drooping|slurred speech|sudden weakness on one side)\b",
    "loss of consciousness": r"\b(unconscious|passed out|not waking up)\b",
    "severe bleeding": r"\b(severe bleeding|bleeding won't stop|uncontrolled bleeding)\b",
}

DISCLAIMER = (
    "Experimental text-model output only. This is not a diagnosis "
    "or a substitute for professional medical care."
)


def emergency_warnings(text):
    lowered = text.casefold()
    return [
        warning
        for warning, pattern in EMERGENCY_PATTERNS.items()
        if re.search(pattern, lowered)
    ]


def main():
    if not MODEL_PATH.is_file():
        print(f"Model file not found: {MODEL_PATH}")
        print("Update MODEL_PATH in this new file to your model's location.")
        return

    try:
        model = joblib.load(MODEL_PATH)
    except Exception as exc:
        print(f"Could not load model: {exc}")
        return

    print("\nStandalone Experimental Health Agent")
    print("Type 'exit' to quit.")
    print(DISCLAIMER)

    while True:
        text = input("\nDescribe the symptoms: ").strip()

        if text.casefold() in {"exit", "quit"}:
            break
        if not text:
            print("Please enter a description.")
            continue

        warnings = emergency_warnings(text)
        if warnings:
            print("\nURGENT SAFETY WARNING")
            print(" ".join(warnings))
            print("Seek emergency medical help now; do not wait for this tool.")
            continue

        try:
            prediction = model.predict([text])[0]
            print(f"\nExperimental model label: {prediction}")
            print(DISCLAIMER)
            print("Please consult a qualified healthcare professional.")
        except Exception as exc:
            print(f"Prediction unavailable: {exc}")


if __name__ == "__main__":
    main()
