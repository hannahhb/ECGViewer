import numpy as np
from .ecg_loader import SAMPLE_RATE


def detect_event_start(ecg: np.ndarray, baseline_secs: float = 20.0, win_secs: float = 0.5) -> int:
    """
    Simple anomaly-based event start detector.

    - Computes baseline mean over first `baseline_secs`
    - Slides a window of `win_secs`
    - Measures deviation from baseline
    - Returns index of max deviation

    This must use the SAME downsample factor as your classifier.
    """

    sr = SAMPLE_RATE // 4  # match downsample_factor=4
    baseline_len = int(baseline_secs * sr)
    window_len = int(win_secs * sr)

    ch1 = ecg[:, 0]
    baseline_mean = ch1[:baseline_len].mean()

    scores = []
    for start in range(0, len(ch1) - window_len):
        window = ch1[start:start + window_len]
        diff = abs(window.mean() - baseline_mean)
        scores.append(diff)

    scores = np.array(scores)
    return int(scores.argmax())  # this is the predicted start index
