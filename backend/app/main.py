from enum import Enum
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="IoT Device Registry")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Pipeline(str, Enum):
    solar_monitoring = "solar_monitoring"
    generic_iot = "generic_iot"


class MetricInput(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_unit: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class DeviceCreate(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=100)
    device_type: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=255)
    pipeline: Pipeline
    description: Optional[str] = None
    metrics: List[MetricInput] = Field(default_factory=list)

    @field_validator("device_id")
    @classmethod
    def validate_device_id(cls, value: str) -> str:
        allowed = value.replace("_", "").replace("-", "")
        if not allowed.isalnum():
            raise ValueError("device_id may only contain letters, numbers, '-' and '_'")
        return value

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, value: List[MetricInput]) -> List[MetricInput]:
        if len(value) == 0:
            raise ValueError("At least one metric is required")
        return value


devices = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/devices")
def get_devices():
    return devices


@app.post("/devices")
def register_device(device: DeviceCreate):
    for existing in devices:
        if existing["device_id"] == device.device_id:
            raise HTTPException(status_code=409, detail="Device ID already exists")

    item = device.model_dump()
    devices.append(item)

    return {
        "message": "Device registered successfully",
        "device": item,
    }