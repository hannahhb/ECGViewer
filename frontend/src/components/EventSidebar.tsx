import React, { useState } from "react";

type EventSummary = {
  id: string;
  patient_id: string;
  event_name: string;
  is_rejected: boolean;
};

interface SidebarProps {
  events: EventSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onHover: (id: string | null) => void;
}

// Utility: group events by event_name → Approved/Rejected
function groupEvents(events: EventSummary[]) {
  const grouped: Record<
    string,
    { Approved: EventSummary[]; Rejected: EventSummary[] }
  > = {};

  for (const e of events) {
    const type = e.event_name || "Unknown";
    const status = e.is_rejected ? "Rejected" : "Approved";

    if (!grouped[type]) {
      grouped[type] = { Approved: [], Rejected: [] };
    }
    grouped[type][status].push(e);
  }

  return grouped;
}

export default function EventSidebar({
  events,
  selectedId,
  onSelect,
  onHover,
}: SidebarProps) {
  const grouped = groupEvents(events);

  const [openType, setOpenType] = useState<{ [key: string]: boolean }>({});
  const [openStatus, setOpenStatus] = useState<{ [key: string]: boolean }>({});

  const toggleType = (type: string) => {
    setOpenType((prev) => ({ ...prev, [type]: !prev[type] }));
  };

  const toggleStatus = (type: string, status: string) => {
    const key = `${type}-${status}`;
    setOpenStatus((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="sidebar-content">
      {/* Loop over each event type */}
      {Object.keys(grouped).map((type) => (
        <div className="event-group" key={type}>
          {/* --- Event Type Header --- */}
          <div
            className="event-type-header"
            onClick={() => toggleType(type)}
          >
            <span>{type}</span>
            <span>{openType[type] ? "−" : "+"}</span>
          </div>

          {/* --- Contents inside Event Type --- */}
          {openType[type] && (
            <div className="event-type-body">
              {["Approved", "Rejected"].map((status) => {
                const key = `${type}-${status}`;
                const eventsInGroup = grouped[type][status];

                // Skip empty groups
                if (eventsInGroup.length === 0) return null;

                return (
                  <div className="event-status-group" key={key}>
                    {/* Status header */}
                    <div
                      className="event-status-header"
                      onClick={() => toggleStatus(type, status)}
                    >
                      <span>{status}</span>
                      <span>{openStatus[key] ? "−" : "+"}</span>
                    </div>

                    {/* Status list */}
                    {openStatus[key] && (
                      <div className="event-list">
                        {eventsInGroup.map((ev) => (
                          <div
                            key={ev.id}
                            className={`event-item ${
                              selectedId === ev.id ? "selected" : ""
                            }`}
                            onClick={() => onSelect(ev.id)}
                            onMouseEnter={() => onHover(ev.id)}
                            onMouseLeave={() => onHover(null)}
                          >
                            <div className="event-id">{ev.id}</div>
                            <div className="event-status">
                              {status}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
