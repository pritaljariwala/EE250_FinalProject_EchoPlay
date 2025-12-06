import os
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import joblib

# -------------------------------
# 1. Parameters
# -------------------------------
DATA_DIR = "audio_samples"   # folder structure: audio_samples/play, pause, skip
SAMPLE_RATE = 16000
N_MFCC = 13
DURATION = 6.0               # seconds
MAX_LEN = int(SAMPLE_RATE * DURATION)

# -------------------------------
# 2. Feature Extraction Function
# -------------------------------
def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=SAMPLE_RATE)
    # pad or truncate
    if len(y) < MAX_LEN:
        y = np.pad(y, (0, MAX_LEN - len(y)))
    else:
        y = y[:MAX_LEN]
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)
    mfcc_scaled = np.mean(mfcc.T, axis=0)  # average over time
    return mfcc_scaled

# -------------------------------
# 3. Load Dataset
# -------------------------------
X = []
y = []

for label in ["play", "pause", "skip"]:
    folder = os.path.join(DATA_DIR, label)
    if not os.path.exists(folder):
        print(f"Warning: Folder {folder} does not exist")
        continue
    for file in os.listdir(folder):
        if file.endswith(".wav"):
            features = extract_features(os.path.join(folder, file))
            X.append(features)
            y.append(label)

X = np.array(X)
y = np.array(y)

print(f"Loaded {len(X)} audio samples")

# -------------------------------
# 4. Train/Test Split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -------------------------------
# 5. Train Classifier
# -------------------------------
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# -------------------------------
# 6. Evaluate
# -------------------------------
y_pred = clf.predict(X_test)
print("Test Accuracy:", accuracy_score(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# -------------------------------
# 7. Save Model
# -------------------------------
joblib.dump(clf, "command_classifier.pkl")
print("Trained model saved as command_classifier.pkl")


