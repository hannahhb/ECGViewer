# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .ecg_loader import index_dataset
# from .classifier import ArrhythmiaClassifier, detect_event_start
from .classifier import HybridEnsembleClassifier
from .event_detector import detect_event_start 

classifier = HybridEnsembleClassifier()

from pydantic import BaseModel

DATA_ROOT = "data"  # path to unzipped dataset

app = FastAPI(title="TriFetch ECG Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

events_index = index_dataset(DATA_ROOT)
# classifier = ArrhythmiaClassifier()
# On first run you can call classifier.train(events_index); later use load()
classifier.train(events_index)
# classifier.load()

class EventSummary(BaseModel):
    id: str
    patient_id: str
    event_name: str
    is_rejected: bool

class EventDetail(BaseModel):
    id: str
    patient_id: str
    event_name: str
    is_rejected: bool
    ecg: list  # list of [ch1, ch2] arrays
    predicted_event_name: str
    event_start_index: int


@app.get("/events", response_model=list[EventSummary])
def list_events():
    return [
        EventSummary(
            id=e.event_id,
            patient_id=e.patient_id,
            event_name=e.event_name,
            is_rejected=e.is_rejected,
        )
        for e in events_index.values()
    ]


@app.get("/events/{event_id}", response_model=EventDetail)
def get_event(event_id: str):
    e = events_index.get(event_id)
    if e is None:
        raise HTTPException(status_code=404, detail="Event not found")

    ecg = e.load_ecg(downsample_factor=4)
    predicted = classifier.predict(ecg)
    start_idx = detect_event_start(ecg)

    return EventDetail(
        id=e.event_id,
        patient_id=e.patient_id,
        event_name=e.event_name,
        is_rejected=e.is_rejected,
        ecg=ecg.tolist(),
        predicted_event_name=predicted,
        event_start_index=start_idx,
    )
