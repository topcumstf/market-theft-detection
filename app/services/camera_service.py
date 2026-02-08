import cv2


class CameraService:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None

    @staticmethod
    def list_available(max_index: int = 5):
        available = []
        for idx in range(max_index):
            cap = cv2.VideoCapture(idx)
            if cap is not None and cap.isOpened():
                available.append(idx)
                cap.release()
            else:
                try:
                    cap.release()
                except Exception:
                    pass
        return available

    def set_index(self, camera_index: int) -> None:
        self.camera_index = camera_index

    def start(self) -> None:
        if self.cap is not None:
            return

        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            self.cap = None
            raise RuntimeError(
                f"Kamera açılamadı (camera_index={self.camera_index}). "
                "Kamera listesinde görünen başka bir index deneyin."
            )

    def read(self):
        if self.cap is None:
            return None
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame

    def stop(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None