from enum import Enum
from pydantic import BaseModel
from typing import List


class Emotion(str, Enum):
    FEAR = "FEAR"
    HAPPY = "HAPPY"
    ANGRY = "ANGRY"
    SAD = "SAD"
    DISGUST = "DISGUST"
    SURPRISE = "SURPRISE"

class Status(str, Enum):
    PROCESS = "PROCESS"
    PUBLISH = "PUBLISH"

class VideoModel(BaseModel):
    id: str
    filename: str
    title: str
    caption: str
    videoUrl: str
    emotion: Emotion = None
    status: Status
    isAds: bool
    processingUrl: str = ''
    emotionLength: List[List[float]] = []
    similarVideo: str = ''
    uploadBy: str
    uploadDate: str