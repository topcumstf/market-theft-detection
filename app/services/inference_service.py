from ultralytics import YOLO


class InferenceService:
    def __init__(self, model_path: str = "yolov8n.pt", conf: float = 0.45):
        self.model = YOLO(model_path)
        self.conf = conf
        self.classes = [0, 39]  # person=0, bottle=39

    def set_conf(self, conf: float) -> None:
        self.conf = float(conf)

    def track(self, frame_bgr):
        results = self.model.track(
            frame_bgr,
            conf=self.conf,
            classes=self.classes,
            persist=True,
            verbose=False
        )
        return results