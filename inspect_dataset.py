from datasets import load_dataset
import pandas as pd

ds = load_dataset("Tulsiandhare/Multilingual_medical_symptom_triage", split="train")
df = ds.to_pandas()

print("Rows:", len(df))
print("\nUrgency counts:")
print(df["urgency"].value_counts(dropna=False).to_string())

print("\nSeverity by urgency:")
print(pd.crosstab(df["severity"], df["urgency"], normalize="index").round(2).to_string())

print("\nDuplicate patient queries:", int(df["patient_query"].duplicated().sum()))
print("\nSample patient-query lengths:")
print(df["patient_query"].astype(str).str.len().describe().round(1).to_string())
