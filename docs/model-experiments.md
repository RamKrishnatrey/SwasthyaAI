# Experimental medical text-classification results

These experiments are development-only classifiers trained on a small, balanced public dataset with six text labels (Dengue, Diarrhea, Influenza, Measles, Pneumonia, Typhoid). They are not deep-learning models, clinical diagnostic tools, or urgency/triage models.

## Results observed during local experimentation

| Experiment | Split / method | Accuracy |
|---|---|---:|
| TF-IDF + Logistic Regression | Random 20% holdout, seed 42 | 94.83% |
| Word + character TF-IDF + Linear SVM | Random 20% holdout, seed 42 | 96.67% |
| Word + character TF-IDF + Linear SVM | Official validation split (450 examples) | 99.33% |
| Word + character TF-IDF + Linear SVM | Official test split (450 examples) | 99.56% |

These scores are those printed during the local development session, not an independently reproduced or clinically validated result. The 99.56% score corresponds to 448/450 examples if calculated from that split. The random split and official splits are not directly comparable.

## Important caveats

- The dataset is balanced and small; synthetic phrasing or templates can make classification easier than real-world use.
- Near-duplicate/template leakage between official splits has not yet been ruled out.
- The authoritative mapping from numeric Parquet label IDs to disease names has not yet been verified. Numeric IDs are therefore not interpreted here.
- The dataset's labels are categories, not medically validated diagnoses or urgency labels.
- The models do not establish patient safety, emergency recall, generalization, or clinical utility.
- Do not use these predictions for real clinical decisions and do not enter real patient information.

## Reproduce locally

1. Obtain the dataset separately according to its licence and place its CSV and official Parquet splits under `data/english_symptoms/` as expected by the scripts.
2. Install the project's existing Python requirements that include pandas, pyarrow, scikit-learn, and joblib.
3. Run `python training/train_official_splits.py` for the official-split experiment.
4. Run `python training/compare_models.py` only for exploratory random-holdout comparisons.

Raw datasets, gated files, cache folders, local databases, and model-generated outputs are not intended to be committed by these scripts.
