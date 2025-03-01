from __future__ import annotations

import tensorflow as tf
from vemotion import settings
from slack_sdk import WebClient
from deepface import DeepFace
import cv2
from pydantic import BaseModel, Field
from typing import Optional, Tuple
import numpy as np

def main() -> None:
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        return
    r = analyze_camera(frame)
    print(1)
    print(r.dominant_emotion)
    cap.release()
    cv2.destroyAllWindows()

def test_message() -> None:
    client = WebClient(token=settings.slack_user_token)
    response = client.chat_postMessage(
        channel="#bot-spam",
        text="Hello from Python! :tada:",
    )
    assert response["message"]["text"] == "Hello from Python! :tada:"


# def analyze_camera(cap: cv2.VideoCapture) -> Result:
def analyze_camera(frame: np.ndarray) -> Result:
    while True:
        # cv2.imshow("frame", frame)
        try:
            results: Result = DeepFace.analyze(frame, actions=("emotion"), enforce_detection=True)
            result = [i for i in results if i['emotion']][0]
        except ValueError:
            continue
        print(result)
        return Result.model_validate(result)


class EmotionScores(BaseModel):
    angry: float
    disgust: float
    fear: float
    happy: float
    sad: float
    surprise: float
    neutral: float
class Region(BaseModel):
    x: int
    y: int
    w: int
    h: int
    left_eye: Optional[Tuple[int, int]]
    right_eye: Optional[Tuple[int, int]]    

# {'emotion': {'angry': np.float32(2.389397e-08), 'disgust': np.float32(1.1228367e-13), 'fear': np.float32(1.39792675e-08), 'happy': np.float32(95.657745), 'sad': np.float32(4.1215037e-05), 'surprise': np.float32(1.5151296e-05), 'neutral': np.float32(4.3421926)}, 'dominant_emotion': 'happy', 'region': {'x': 186, 'y': 138, 'w': 245, 'h': 245, 'left_eye': None, 'right_eye': None}, 'face_confidence': np.float64(0.97)}
class Result(BaseModel):
    emotion: EmotionScores
    # region: Region
    dominant_emotion: str
    face_confidence: float = Field(..., ge=0.0, le=1.0)


if __name__ == "__main__":
    main()