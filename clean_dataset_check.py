from datasets import load_dataset
import pandas as pd

df = load_dataset(
    "Tulsiandhare/Multilingual_medical_symptom_triage",
    split="train"
).to_pandas()

df["patient_query"] = df["patient_query"].astype(str).str.strip()
df["urgency"] = df["urgency"].astype(str).str.strip()

# Remove identical texts whose labels disagree.
label_counts = df.groupby("patient_query")["urgency"].nunique()
ambiguous = set(label_counts[label_counts > 1].index)
clean = df[~df["patient_query"].isin(ambiguous)].drop_duplicates(
    subset=["patient_query"]
)

print("Original rows:", len(df))
print("Ambiguous query texts:", len(ambiguous))
print("Rows retained:", len(clean))
print("\nRetained urgency labels:")
print(clean["urgency"].value_counts().to_string())
print("\nRetained language labels:")
print(clean["language"].value_counts().head(10).to_string())
