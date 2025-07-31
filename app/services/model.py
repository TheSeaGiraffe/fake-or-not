from pathlib import Path

import torch
from transformers import pipeline
from transformers.pipelines.base import Pipeline

from app.config import ML_MODEL_PATH

misinfo_classifier: Pipeline = None


def init_model():
    global misinfo_classifier
    misinfo_classifier = pipeline("text-classification", Path(ML_MODEL_PATH))


def get_model():
    return misinfo_classifier


def cleanup_model():
    global misinfo_classifier
    del misinfo_classifier

    if torch.cuda.is_available():
        torch.cuda.empty_cache()
