import os
import json
from enum import Enum
from typing import Optional, List

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from datetime import datetime
from typing import Optional

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
)

app = FastAPI(title="IoT Device Registry")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
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


def get_conn():
    return psycopg.connect(DATABASE_URL)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/devices")
def get_devices():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    device_id,
                    device_type,
                    location,
                    pipeline,
                    topic_prefix,
                    is_active,
                    created_at
                FROM device_registry
                ORDER BY created_at DESC
                """
            )
            rows = cur.fetchall()

    return [
        {
            "device_id": row[0],
            "device_type": row[1],
            "location": row[2],
            "pipeline": row[3],
            "topic_prefix": row[4],
            "is_active": row[5],
            "created_at": row[6],
        }
        for row in rows
    ]


@app.post("/devices")
def register_device(device: DeviceCreate):
    topic_prefix = (
        f"solar/{device.device_id}"
        if device.pipeline == Pipeline.solar_monitoring
        else f"iot/{device.device_id}"
    )

    metrics_json = [metric.model_dump() for metric in device.metrics]

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO device_registry (
                        device_id,
                        device_type,
                        location,
                        pipeline,
                        topic_prefix
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        device.device_id,
                        device.device_type,
                        device.location,
                        device.pipeline.value,
                        topic_prefix,
                    ),
                )

                if device.pipeline == Pipeline.generic_iot:
                    metadata = {
                        "metrics": metrics_json,
                        "expected_payload_format": "measurements_object",
                    }

                    cur.execute(
                        """
                        INSERT INTO iot_devices (
                            device_id,
                            device_name,
                            device_type,
                            description,
                            location,
                            metadata
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            device.device_id,
                            device.device_id,
                            device.device_type,
                            device.description,
                            device.location,
                            json.dumps(metadata),
                        ),
                    )

                elif device.pipeline == Pipeline.solar_monitoring:
                    cur.execute(
                        """
                        INSERT INTO samples (
                            sample_name,
                            sample_type,
                            description,
                            grid_rows,
                            grid_cols
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            device.device_id,
                            device.device_type,
                            device.description,
                            1,
                            1,
                        ),
                    )

        return {
            "message": "Device registered successfully",
            "device_id": device.device_id,
            "pipeline": device.pipeline.value,
            "topic_prefix": topic_prefix,
        }

    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Device ID already exists in registry, IoT devices, or samples",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    
@app.get("/devices/{device_id}/metrics")
def get_device_metrics(device_id: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pipeline FROM device_registry WHERE device_id = %s",
                (device_id,),
            )
            row = cur.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Device not found")

            pipeline = row[0]

            if pipeline == "generic_iot":
                cur.execute(
                    """
                    SELECT DISTINCT m.metric_name
                    FROM iot_measurements m
                    JOIN iot_devices d ON d.id_device = m.id_device
                    WHERE d.device_id = %s
                    ORDER BY m.metric_name
                    """,
                    (device_id,),
                )

            else:
                cur.execute(
                    """
                    SELECT DISTINCT m.metric_name
                    FROM monitoring m
                    JOIN samples s ON s.id_sample = m.id_sample
                    WHERE s.sample_name = %s
                    ORDER BY m.metric_name
                    """,
                    (device_id,),
                )

            return [r[0] for r in cur.fetchall()]


@app.get("/devices/{device_id}/measurements")
def get_device_measurements(
    device_id: str,
    metric_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 500,
):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pipeline FROM device_registry WHERE device_id = %s",
                (device_id,),
            )
            row = cur.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Device not found")

            pipeline = row[0]

            params = [device_id]
            filters = []

            if metric_name:
                filters.append("m.metric_name = %s")
                params.append(metric_name)

            if start_date:
                filters.append("m.measurement_date >= %s")
                params.append(start_date)

            if end_date:
                filters.append("m.measurement_date <= %s")
                params.append(end_date)

            where_extra = ""
            if filters:
                where_extra = " AND " + " AND ".join(filters)

            params.append(limit)

            if pipeline == "generic_iot":
                query = f"""
                    SELECT
                        d.device_id,
                        m.topic,
                        m.metric_name,
                        m.metric_value,
                        m.metric_unit,
                        m.measurement_date
                    FROM iot_measurements m
                    JOIN iot_devices d ON d.id_device = m.id_device
                    WHERE d.device_id = %s
                    {where_extra}
                    ORDER BY m.measurement_date DESC
                    LIMIT %s
                """
            else:
                query = f"""
                    SELECT
                        s.sample_name AS device_id,
                        NULL AS topic,
                        m.metric_name,
                        m.metric_value,
                        m.metric_unit,
                        m.measurement_date
                    FROM monitoring m
                    JOIN samples s ON s.id_sample = m.id_sample
                    WHERE s.sample_name = %s
                    {where_extra}
                    ORDER BY m.measurement_date DESC
                    LIMIT %s
                """

            cur.execute(query, params)
            rows = cur.fetchall()

    return [
        {
            "device_id": row[0],
            "topic": row[1],
            "metric_name": row[2],
            "metric_value": row[3],
            "metric_unit": row[4],
            "measurement_date": row[5],
        }
        for row in rows
    ]