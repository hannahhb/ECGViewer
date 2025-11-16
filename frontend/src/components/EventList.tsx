// frontend/src/components/EventList.tsx
import React from "react";

interface EventItem {
  id: string;
  patient_id: string;
  event_name: string;
  is_rejected: boolean;
}

interface Props {
  events: EventItem[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onHover: (id: string | null) => void;
}

export const EventList: React.FC<Props> = ({
  events,
  selectedId,
  onSelect,
  onHover,
}) => {
  return (
    <div className="event-list">
      {events.map((e) => (
        <div
          key={e.id}
          className={`event-item ${e.id === selectedId ? "selected" : ""}`}
          onClick={() => onSelect(e.id)}
          onMouseEnter={() => onHover(e.id)}
          onMouseLeave={() => onHover(null)}
        >
          <div className="event-title">
            {e.event_name} — {e.id}
          </div>
          <div className="event-meta">
            {e.is_rejected ? "Rejected" : "Approved"}
          </div>
        </div>
      ))}
    </div>
  );
};
