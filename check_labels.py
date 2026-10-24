from datasets import load_dataset
import pandas as pd

df = load_dataset(
    "Tulsiandhare/Multilingual_medical_symptom_triage",
    split="train"
).to_pandas()

for severity in ["Mild", "Moderate", "Severe"]:
    subset = df[df["severity"].astype(str).str.lower() == severity.lower()]
    print(f"\n{severity}:")
    print(subset["patient_query"].head(3).to_string(index=False))

print("\nUrgency labels per identical patient query:")
conflicts = df.groupby("patient_query")["urgency"].nunique()
print("Queries with conflicting urgency labels:", int((conflicts > 1).sum()))
