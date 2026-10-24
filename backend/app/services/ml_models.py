# SwasthyaAI ML Models Service
# Model registry and inference interface for trained ML/DL models
# Integrates existing models (DDXPlus, etc.) with the backend

import os
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

# Try to import ML libraries
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available")

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    logger.warning("joblib not available")

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logger.warning("ONNX Runtime not available")

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available")


class ModelFormat(str, Enum):
    PYTORCH = "pytorch"
    ONNX = "onnx"
    SKLEARN = "sklearn"
    TENSORFLOW = "tensorflow"
    HUGGINGFACE = "huggingface"


class ModelTask(str, Enum):
    TRIAGE = "triage"
    SYMPTOM_CLASSIFICATION = "symptom_classification"
    DIAGNOSIS_PREDICTION = "diagnosis_prediction"
    DRUG_INTERACTION = "drug_interaction"
    MEDICAL_NER = "medical_ner"
    REPORT_CLASSIFICATION = "report_classification"


@dataclass
class ModelMetadata:
    name: str
    version: str
    task: ModelTask
    format: ModelFormat
    path: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    labels: List[str]
    description: str
    created_at: str
    metrics: Dict[str, float]
    requirements: Dict[str, str]


class BaseModelInference(ABC):
    """Abstract base class for model inference."""

    @abstractmethod
    def load(self, model_path: str, **kwargs) -> None:
        """Load model from disk."""
        pass

    @abstractmethod
    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference on inputs."""
        pass

    @abstractmethod
    def preprocess(self, raw_input: Any) -> Dict[str, Any]:
        """Preprocess raw input for model."""
        pass

    @abstractmethod
    def postprocess(self, raw_output: Any) -> Dict[str, Any]:
        """Postprocess model output."""
        pass


class PyTorchModelInference(BaseModelInference):
    """PyTorch model inference."""

    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu") if TORCH_AVAILABLE else None

    def load(self, model_path: str, **kwargs) -> None:
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch not available")
        self.model = torch.jit.load(model_path, map_location=self.device) if model_path.endswith('.pt') else torch.load(model_path, map_location=self.device)
        self.model.eval()
        self.model.to(self.device)

    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        with torch.no_grad():
            # Convert inputs to tensors
            tensor_inputs = {k: torch.tensor(v).to(self.device) if isinstance(v, (list, np.ndarray)) else v for k, v in inputs.items()}
            outputs = self.model(**tensor_inputs)
            return self._tensor_to_dict(outputs)

    def preprocess(self, raw_input: Any) -> Dict[str, Any]:
        # To be implemented by specific model
        return raw_input

    def postprocess(self, raw_output: Any) -> Dict[str, Any]:
        return self._tensor_to_dict(raw_output)

    def _tensor_to_dict(self, output) -> Dict[str, Any]:
        if isinstance(output, torch.Tensor):
            return {"logits": output.cpu().numpy().tolist()}
        elif isinstance(output, dict):
            return {k: v.cpu().numpy().tolist() if isinstance(v, torch.Tensor) else v for k, v in output.items()}
        return {"output": output}


class ONNXModelInference(BaseModelInference):
    """ONNX model inference."""

    def __init__(self):
        self.session = None

    def load(self, model_path: str, **kwargs) -> None:
        if not ONNX_AVAILABLE:
            raise RuntimeError("ONNX Runtime not available")
        self.session = ort.InferenceSession(model_path)

    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Convert inputs to numpy arrays
        np_inputs = {k: np.array(v) if isinstance(v, list) else v for k, v in inputs.items()}
        outputs = self.session.run(None, np_inputs)
        output_names = [o.name for o in self.session.get_outputs()]
        return dict(zip(output_names, [o.tolist() for o in outputs]))

    def preprocess(self, raw_input: Any) -> Dict[str, Any]:
        return raw_input

    def postprocess(self, raw_output: Any) -> Dict[str, Any]:
        return raw_output


class SklearnModelInference(BaseModelInference):
    """Scikit-learn model inference."""

    def __init__(self):
        self.model = None
        self.preprocessor = None

    def load(self, model_path: str, preprocessor_path: Optional[str] = None, **kwargs) -> None:
        if not JOBLIB_AVAILABLE:
            raise RuntimeError("joblib not available")
        self.model = joblib.load(model_path)
        if preprocessor_path and os.path.exists(preprocessor_path):
            self.preprocessor = joblib.load(preprocessor_path)

    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        X = inputs.get("features", inputs)
        if self.preprocessor:
            X = self.preprocessor.transform(X)
        predictions = self.model.predict(X)
        probabilities = None
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(X)
        return {
            "predictions": predictions.tolist(),
            "probabilities": probabilities.tolist() if probabilities is not None else None
        }

    def preprocess(self, raw_input: Any) -> Dict[str, Any]:
        return raw_input

    def postprocess(self, raw_output: Any) -> Dict[str, Any]:
        return raw_output


class HuggingFaceModelInference(BaseModelInference):
    """Hugging Face transformers model inference."""

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu") if TORCH_AVAILABLE else None

    def load(self, model_path: str, tokenizer_path: Optional[str] = None, **kwargs) -> None:
        if not TRANSFORMERS_AVAILABLE:
            raise RuntimeError("Transformers not available")
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch required for Hugging Face models")

        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path or model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()
        self.model.to(self.device)

    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        texts = inputs.get("text", [])
        if isinstance(texts, str):
            texts = [texts]

        encoded = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**encoded)
            logits = outputs.logits.cpu().numpy()
            probs = torch.nn.functional.softmax(torch.tensor(logits), dim=-1).numpy()

        return {
            "logits": logits.tolist(),
            "probabilities": probs.tolist(),
            "predictions": logits.argmax(axis=-1).tolist()
        }

    def preprocess(self, raw_input: Any) -> Dict[str, Any]:
        if isinstance(raw_input, str):
            return {"text": raw_input}
        return raw_input

    def postprocess(self, raw_output: Any) -> Dict[str, Any]:
        return raw_output


class ModelRegistry:
    """Registry for managing ML models."""

    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models: Dict[str, BaseModelInference] = {}
        self.metadata: Dict[str, ModelMetadata] = {}
        self._inference_classes = {
            ModelFormat.PYTORCH: PyTorchModelInference,
            ModelFormat.ONNX: ONNXModelInference,
            ModelFormat.SKLEARN: SklearnModelInference,
            ModelFormat.HUGGINGFACE: HuggingFaceModelInference,
        }

    def register_model(self, metadata: ModelMetadata) -> None:
        """Register a model with its metadata."""
        self.metadata[metadata.name] = metadata
        logger.info(f"Registered model: {metadata.name} v{metadata.version}")

    def load_model(self, model_name: str, **kwargs) -> BaseModelInference:
        """Load a model by name."""
        if model_name in self.models:
            return self.models[model_name]

        if model_name not in self.metadata:
            raise ValueError(f"Model {model_name} not registered")

        meta = self.metadata[model_name]
        inference_class = self._inference_classes.get(meta.format)
        if not inference_class:
            raise ValueError(f"No inference class for format {meta.format}")

        inference = inference_class()
        full_path = self.models_dir / meta.path
        inference.load(str(full_path), **kwargs)

        self.models[model_name] = inference
        logger.info(f"Loaded model: {model_name}")
        return inference

    def predict(self, model_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run prediction on a model."""
        inference = self.load_model(model_name)
        preprocessed = inference.preprocess(inputs)
        raw_output = inference.predict(preprocessed)
        return inference.postprocess(raw_output)

    def get_metadata(self, model_name: str) -> Optional[ModelMetadata]:
        """Get model metadata."""
        return self.metadata.get(model_name)

    def list_models(self) -> List[ModelMetadata]:
        """List all registered models."""
        return list(self.metadata.values())

    def discover_models(self) -> None:
        """Auto-discover models in the models directory."""
        for model_dir in self.models_dir.iterdir():
            if model_dir.is_dir():
                metadata_file = model_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file) as f:
                            data = json.load(f)
                        metadata = ModelMetadata(**data)
                        self.register_model(metadata)
                    except Exception as e:
                        logger.error(f"Failed to load metadata for {model_dir.name}: {e}")


# DDXPlus-specific integration
class DDXPlusInference:
    """Integration for DDXPlus differential diagnosis model."""

    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.model = None
        self.conditions = []
        self.symptoms = []

    def load(self):
        """Load DDXPlus model and metadata."""
        # Load model (adapt based on actual format)
        if (self.model_path / "model.pt").exists():
            self.model = PyTorchModelInference()
            self.model.load(str(self.model_path / "model.pt"))
        elif (self.model_path / "model.onnx").exists():
            self.model = ONNXModelInference()
            self.model.load(str(self.model_path / "model.onnx"))

        # Load condition and symptom vocabularies
        if (self.model_path / "conditions.json").exists():
            with open(self.model_path / "conditions.json") as f:
                self.conditions = json.load(f)
        if (self.model_path / "symptoms.json").exists():
            with open(self.model_path / "symptoms.json") as f:
                self.symptoms = json.load(f)

    def predict_differential(self, symptoms: List[str], age: int = None, sex: str = None, top_k: int = 5) -> Dict[str, Any]:
        """Run differential diagnosis prediction."""
        if not self.model:
            self.load()

        # Convert symptoms to model input format
        symptom_vector = self._symptoms_to_vector(symptoms)

        inputs = {
            "symptoms": symptom_vector,
            "age": age or 30,
            "sex": 0 if sex == "male" else 1 if sex == "female" else 0.5
        }

        result = self.model.predict(inputs)
        probabilities = result.get("probabilities", [[]])[0] if result.get("probabilities") else []

        # Get top-k predictions
        if probabilities:
            top_indices = np.argsort(probabilities)[-top_k:][::-1]
            differentials = [
                {
                    "condition": self.conditions[i] if i < len(self.conditions) else f"condition_{i}",
                    "probability": float(probabilities[i]),
                    "icd10": None  # Would need mapping
                }
                for i in top_indices
            ]
        else:
            differentials = []

        return {
            "differentials": differentials,
            "input_symptoms": symptoms,
            "model": "DDXPlus",
            "disclaimer": "This is decision support only, not a medical diagnosis. Consult a healthcare professional."
        }

    def _symptoms_to_vector(self, symptoms: List[str]) -> List[float]:
        """Convert symptom list to binary vector."""
        vector = [0.0] * len(self.symptoms)
        symptom_set = set(s.lower() for s in symptoms)
        for i, s in enumerate(self.symptoms):
            if s.lower() in symptom_set:
                vector[i] = 1.0
        return vector


# Global registry instance
model_registry = ModelRegistry()


def get_model_registry() -> ModelRegistry:
    """Get global model registry."""
    return model_registry


# Convenience functions
async def predict_triage(symptoms: List[str], age_group: str, language: str = "en") -> Dict[str, Any]:
    """Predict triage using best available model."""
    # Try DDXPlus first, fallback to mock
    try:
        ddxplus = DDXPlusInference("./models/ddxplus")
        return ddxplus.predict_differential(symptoms)
    except Exception as e:
        logger.warning(f"DDXPlus prediction failed: {e}, using mock")
        # Fallback to mock triage
        from app.services.triage import predict_mock
        text = " ".join(symptoms)
        return predict_mock(text, language)


def initialize_models(models_dir: str = "./models"):
    """Initialize model registry and discover models."""
    global model_registry
    model_registry = ModelRegistry(models_dir)
    model_registry.discover_models()
    return model_registry


__all__ = [
    "ModelRegistry",
    "ModelMetadata",
    "ModelFormat",
    "ModelTask",
    "BaseModelInference",
    "PyTorchModelInference",
    "ONNXModelInference",
    "SklearnModelInference",
    "HuggingFaceModelInference",
    "DDXPlusInference",
    "model_registry",
    "get_model_registry",
    "predict_triage",
    "initialize_models",
]