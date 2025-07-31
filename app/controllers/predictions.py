import torch
from fastapi import APIRouter, Depends
from transformers.pipelines.base import Pipeline

from app.schema.prediction import PredictionIn, PredictionOut
from app.services.auth import has_valid_access_token
from app.services.model import get_model

router = APIRouter(prefix="/predict")


@router.post("/", dependencies=[Depends(has_valid_access_token)])
async def predict_on_text(text: PredictionIn, model: Pipeline = Depends(get_model)):
    with torch.no_grad():
        preds = model(text.model_input)
    return PredictionOut(model_predictions=preds)
