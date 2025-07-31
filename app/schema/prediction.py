from pydantic import BaseModel, ConfigDict


class PredictionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PredictionIn(PredictionBase):
    model_input: list[str]


class PredictionOut(PredictionBase):
    model_predictions: list[dict[str, str | float]]
