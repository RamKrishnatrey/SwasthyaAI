"""Experimental urgency-label baseline. Never use identifiers or the target proxy as features."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--data", required=True, help="CSV path; raw data is not committed")
    p.add_argument("--output-dir", default="models")
    a=p.parse_args()
    path=Path(a.data)
    if not path.is_file(): raise SystemExit(f"Dataset not found: {path}")
    df=pd.read_csv(path, low_memory=False)
    label_col=next((c for c in ("urgency","urgency_label","label") if c in df.columns),None)
    symptom_cols=[c for c in ("symptom_1","symptom_2","symptom_3") if c in df.columns]
    if not label_col: raise SystemExit(f"No urgency label column. Columns: {list(df.columns)}")
    if symptom_cols:
        # Use symptom fields only: do not include severity because it can encode the urgency target.
        text=df[symptom_cols].fillna("").astype(str).agg(" ; ".join,axis=1)
    else:
        text_col=next((c for c in ("patient_query","symptom_text","text","description") if c in df.columns),None)
        if not text_col: raise SystemExit(f"No safe symptom text columns found. Columns: {list(df.columns)}")
        text=df[text_col].fillna("").astype(str)
    data=pd.DataFrame({"text":text.str.strip(),"label":df[label_col].fillna("").astype(str).str.strip()})
    data=data[(data.text!="")&(data.label!="")]
    data["key"]=data.text.str.casefold().str.replace(r"\s+"," ",regex=True)
    label_counts=data.groupby("key").label.nunique()
    conflicting=set(label_counts[label_counts>1].index)
    data=data[~data.key.isin(conflicting)].drop_duplicates("key").reset_index(drop=True)
    if data.label.nunique()<2 or data.label.value_counts().min()<2:
        raise SystemExit("Need at least two label classes and at least two records per class after cleaning.")
    x_train,x_test,y_train,y_test=train_test_split(data.text,data.label,test_size=.2,random_state=42,stratify=data.label)
    features=FeatureUnion([
        ("word",TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=80000,sublinear_tf=True)),
        ("char",TfidfVectorizer(analyzer="char",ngram_range=(2,5),min_df=2,max_features=100000,sublinear_tf=True)),
    ])
    model=Pipeline([("features",features),("classifier",LinearSVC(class_weight="balanced"))])
    print(f"Training rows: {len(x_train)}; held-out rows: {len(x_test)}; labels: {sorted(data.label.unique())}")
    model.fit(x_train,y_train); pred=model.predict(x_test)
    out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    metrics={
      "model":"word_char_tfidf_linear_svc","input_columns":symptom_cols or ["text"],
      "label_column":label_col,"rows_after_cleaning":int(len(data)),
      "train_rows":int(len(x_train)),"test_rows":int(len(x_test)),
      "accuracy":float(accuracy_score(y_test,pred)),
      "macro_f1":float(f1_score(y_test,pred,average="macro")),
      "classes":[str(c) for c in model.classes_],
      "classification_report":classification_report(y_test,pred,output_dict=True,zero_division=0),
      "confusion_matrix":confusion_matrix(y_test,pred,labels=model.classes_).tolist(),
      "limitations":["Dataset labels may be synthetic or unverified.","Metrics measure agreement with dataset labels, not clinical safety.","Experimental demo only; not a validated triage model."]
    }
    joblib.dump(model,out/"urgency_model.joblib")
    (out/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    print(f"Accuracy: {metrics['accuracy']:.4f}; macro-F1: {metrics['macro_f1']:.4f}")
    print(classification_report(y_test,pred,zero_division=0))
    print(f"Saved {out/'metrics.json'} and {out/'urgency_model.joblib'}")
if __name__=="__main__": main()
