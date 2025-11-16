// frontend/src/App.tsx
import React, { useEffect, useState } from "react";
// import { EventList } from "./components/EventList";
import EventSidebar from "./components/EventSidebar";
import { ECGChart } from "./components/ECGChart";

const API_BASE = "http://localhost:8000";

type EventSummary = {
  id: string;
  patient_id: string;
  event_name: string;
  is_rejected: boolean;
};

type EventDetail = {
  id: string;
  patient_id: string;
  event_name: string;
  is_rejected: boolean;
  ecg: number[][];
  predicted_event_name: string;
  event_start_index: number;
};

function App() {
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [hoverId, setHoverId] = useState<string | null>(null);
  const [detail, setDetail] = useState<EventDetail | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/events`)
      .then((res) => res.json())
      .then(setEvents);
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    fetch(`${API_BASE}/events/${selectedId}`)
      .then((res) => res.json())
      .then(setDetail);
  }, [selectedId]);

  const ecgData =
    detail?.ecg.map((row, idx) => ({
      x: idx,
      ch1: row[0],
      ch2: row[1],
    })) ?? [];

  const highlight = hoverId !== null && hoverId === detail?.id;

  return (
    <div className="app-container">
      <aside className="sidebar">
  <EventSidebar
    events={events}
    selectedId={selectedId}
    onSelect={setSelectedId}
    onHover={setHoverId}
  />
</aside>


      <main className="main-panel">
        {detail ? (
          <>
            <div className="header">
              <div>
                <h1>{detail.event_name}</h1>
                <p>Patient: {detail.patient_id}</p>
                <p>Model prediction: {detail.predicted_event_name}</p>
              </div>
            </div>
            <ECGChart
              data={ecgData}
              eventStartIndex={detail.event_start_index}
              highlighted={highlight}
            />
          </>
        ) : (
          <p>Select an episode to view ECG.</p>
        )}
      </main>
    </div>
  );
}

export default App;
