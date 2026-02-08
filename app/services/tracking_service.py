class TrackingService:
    def __init__(self):
        self.tracks = {}

    def update(self, results):
        tracked = []

        boxes = results[0].boxes
        if boxes is None:
            return tracked

        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()

            track_id = int(box.id[0]) if box.id is not None else None

            tracked.append({
                "track_id": track_id,
                "cls_id": cls_id,
                "conf": conf,
                "bbox": xyxy
            })

        return tracked