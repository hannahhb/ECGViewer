// frontend/src/components/ECGChart.tsx
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ReferenceArea,
  CartesianGrid,
} from "recharts";

type ECGPoint = {
  x: number;  // sample index or time
  ch1: number;
  ch2: number;
};

interface Props {
  data: ECGPoint[];
  eventStartIndex: number | null;
  highlighted: boolean;
}

export const ECGChart: React.FC<Props> = ({ data, eventStartIndex, highlighted }) => {
  const eventX = eventStartIndex !== null ? data[eventStartIndex]?.x : undefined;
  const windowSize = 50; // samples to highlight around event

  const eventStart = eventStartIndex !== null ? Math.max(0, eventStartIndex - windowSize) : null;
  const eventEnd = eventStartIndex !== null ? Math.min(data.length - 1, eventStartIndex + windowSize) : null;

  const eventStartX = eventStart !== null ? data[eventStart].x : undefined;
  const eventEndX = eventEnd !== null ? data[eventEnd].x : undefined;

  return (
    <LineChart width={800} height={320} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="x" tickFormatter={(v) => (v / 200).toFixed(1)} />
      <YAxis />
      <Tooltip />
      {eventX !== undefined && (
        <ReferenceLine x={eventX} stroke="red" strokeDasharray="3 3" />
      )}
      {highlighted && eventStartX !== undefined && eventEndX !== undefined && (
        <ReferenceArea x1={eventStartX} x2={eventEndX} fillOpacity={0.2} />
      )}
      <Line type="monotone" dataKey="ch1" dot={false} />
      <Line type="monotone" dataKey="ch2" dot={false} />
    </LineChart>
  );
};
