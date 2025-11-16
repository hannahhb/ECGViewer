import numpy as np
import joblib
from typing import Dict, List
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, f1_score

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

from .ecg_loader import ECGEvent


MODEL_PATH = "models/hybrid_ensemble.pkl"

class HybridEnsembleClassifier:
    def __init__(self):
        self.models = []          # list of all trained models
        self.encoder = None       # label encoder

    def _extract_features(self, ecg):
        ch1, ch2 = ecg[:, 0], ecg[:, 1]
        return np.array([
            ch1.mean(), ch1.std(), ch1.max(), ch1.min(),
            ch2.mean(), ch2.std(), ch2.max(), ch2.min(),
            np.mean(np.abs(np.diff(ch1))),
            np.mean(np.abs(np.diff(ch2))),
        ], dtype=np.float32)

    def train(self, events: Dict[str, ECGEvent]):
        print("\n============================")
        print("  TRAINING HYBRID ENSEMBLE  ")
        print("============================\n")

        # -------------------------------
        # Load & extract features
        # -------------------------------
        X, y = [], []

        for e in events.values():
            ecg = e.load_ecg(downsample_factor=4)
            if ecg is None or len(ecg) == 0:
                continue
            X.append(self._extract_features(ecg))
            y.append(e.event_name)

        X = np.vstack(X)
        self.encoder = LabelEncoder()
        y = self.encoder.fit_transform(y)

        # -------------------------------
        # 5-Fold Setup
        # -------------------------------
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        all_models = []
        fold_metrics = []

        for fold, (train_idx, val_idx) in enumerate(kf.split(X)):
            print(f"\n=== Fold {fold+1}/5 ===")

            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            fold_models = []

            # ----------------------
            # Model 1: RandomForest
            # ----------------------
            rf = RandomForestClassifier(
                n_estimators=200,
                max_depth=12,
                random_state=fold
            )
            rf.fit(X_train, y_train)
            pred_rf = rf.predict(X_val)

            # ----------------------
            # Model 2: XGBoost
            # ----------------------
            xgb = XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.9,
                objective="multi:softmax",
                eval_metric="mlogloss",
                random_state=fold
            )
            xgb.fit(X_train, y_train)
            pred_xgb = xgb.predict(X_val)

            # ----------------------
            # Model 3: SVM (RBF kernel)
            # ----------------------
            svm = SVC(
                kernel="rbf",
                C=3,
                gamma="scale",
                probability=False,
                random_state=fold
            )
            svm.fit(X_train, y_train)
            pred_svm = svm.predict(X_val)

            # ----------------------
            # Compute validation score
            # ----------------------
            val_preds = np.vstack([pred_rf, pred_xgb, pred_svm]).T
            final_pred = []

            # majority vote per sample
            for row in val_preds:
                vals, counts = np.unique(row, return_counts=True)
                final_pred.append(vals[counts.argmax()])

            acc = accuracy_score(y_val, final_pred)
            f1 = f1_score(y_val, final_pred, average="weighted")
            fold_metrics.append((acc, f1))

            print(f"Fold validation accuracy: {acc:.4f}")
            print(f"Fold validation F1:       {f1:.4f}")

            # Save the 3 models from this fold
            fold_models.extend([rf, xgb, svm])
            all_models.extend(fold_models)

        self.models = all_models

        # Save ensemble
        joblib.dump(
            {"models": self.models, "encoder": self.encoder},
            MODEL_PATH
        )

        print("\n============================")
        print(" Hybrid Ensemble Completed ")
        print("============================")
        print("Mean accuracy:", np.mean([m[0] for m in fold_metrics]))
        print("Mean F1 score:", np.mean([m[1] for m in fold_metrics]))

    def load(self):
        saved = joblib.load(MODEL_PATH)
        self.models = saved["models"]
        self.encoder = saved["encoder"]

    def predict(self, ecg):
        feats = self._extract_features(ecg).reshape(1, -1)

        preds = [int(model.predict(feats)[0]) for model in self.models]

        # Majority vote across all model outputs (15 votes)
        vote = max(set(preds), key=preds.count)
        return self.encoder.inverse_transform([vote])[0]
