# backend/app/ecg_loader.py
import os
import json
import numpy as np
from pathlib import Path
from typing import Dict, List

SAMPLE_RATE = 200  # Hz

class ECGEvent:
    def __init__(self, event_id, patient_id, event_name, is_rejected, folder, ecg_paths):
        self.event_id = event_id
        self.patient_id = patient_id
        self.event_name = event_name
        self.is_rejected = is_rejected
        self.folder = folder
        self.ecg_paths = ecg_paths  # list of 3 .txt paths

        self._ecg_cached = None

    def load_ecg(self, downsample_factor: int = 2):
        if self._ecg_cached is not None:
            return self._ecg_cached

        traces = []
        for p in self.ecg_paths:
            data = np.loadtxt(p, delimiter=",", skiprows=1)  # shape (6000, 2)
            traces.append(data)
        full = np.vstack(traces)  # (18000, 2)

        if downsample_factor > 1:
            full = full[::downsample_factor]

        self._ecg_cached = full
        return full

def index_dataset(root: str) -> Dict[str, ECGEvent]:
    root_path = Path(root)
    events = {}

    # iterate class folders (e.g., AFIB_approved)
    for class_folder in root_path.iterdir():
        if not class_folder.is_dir():
            continue

        # iterate event subfolders inside (e.g., AFIB_approved/12345/)
        for event_folder in class_folder.iterdir():
            if not event_folder.is_dir():
                continue

            # find the metadata JSON
            json_files = list(event_folder.glob("event_*.json"))
            if len(json_files) == 0:
                continue  # bad folder

            json_file = json_files[0]
            event_id = json_file.stem.split("_")[1]

            with open(json_file) as f:
                meta = json.load(f)

            event_name = meta.get("Event_Name")
            patient_id = meta.get("Patient_IR_ID")
            is_rejected = meta.get("IsRejected") == "1"

            # find 3 ECG .txt files
            # find all ECG .txt files inside event folder
            ecg_paths = sorted(event_folder.glob("*.txt"))

            if len(ecg_paths) == 0:
                print(f"⚠️  Skipping event {event_id}: no ECG txt files found in {event_folder}")
                continue

            events[event_id] = ECGEvent(
                event_id=event_id,
                patient_id=patient_id,
                event_name=event_name,
                is_rejected=is_rejected,
                folder=str(event_folder),
                ecg_paths=[str(p) for p in ecg_paths],
            )

    return events
