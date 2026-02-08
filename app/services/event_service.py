import time


class EventService:
    """
    - bottle kişinin yanında en az near_required_time saniye kesintisiz görünürse ARMED olur.
    - ARMED olduktan sonra bottle disappear_time saniye görünmezse event üretir.
    """

    def __init__(self, near_required_time: float = 3.0, disappear_time: float = 3.0):
        self.near_required_time = near_required_time
        self.disappear_time = disappear_time

        self.last_seen_ts = {}   # bottle_id -> son görüldüğü zaman
        self.near_start_ts = {}  # bottle_id -> yakınlık başlangıç
        self.armed = {}          # bottle_id -> True

    def set_near_required_time(self, t: float) -> None:
        self.near_required_time = float(t)

    def set_disappear_time(self, t: float) -> None:
        self.disappear_time = float(t)

    def get_armed_ids(self):
        return set(self.armed.keys())

    @staticmethod
    def _center(bbox):
        x1, y1, x2, y2 = bbox
        return (x1 + x2) / 2, (y1 + y2) / 2

    @staticmethod
    def _point_in_bbox(pt, bbox):
        x, y = pt
        x1, y1, x2, y2 = bbox
        return x1 <= x <= x2 and y1 <= y <= y2

    def update(self, tracked):
        events = []
        now = time.time()

        persons = [d for d in tracked if d.get("cls_id") == 0 and d.get("track_id") is not None]
        bottles = [d for d in tracked if d.get("cls_id") == 39 and d.get("track_id") is not None]

        current_bottle_ids = set()

        for b in bottles:
            bid = b["track_id"]
            current_bottle_ids.add(bid)
            self.last_seen_ts[bid] = now

            b_center = self._center(b["bbox"])

            is_near = False
            for p in persons:
                if self._point_in_bbox(b_center, p["bbox"]):
                    is_near = True
                    break

            if is_near:
                if bid not in self.near_start_ts:
                    self.near_start_ts[bid] = now

                near_duration = now - self.near_start_ts[bid]
                if near_duration >= self.near_required_time:
                    self.armed[bid] = True
            else:
                # yakınlık zinciri kırılırsa armed sıfırlansın
                self.near_start_ts.pop(bid, None)
                self.armed.pop(bid, None)

        # kaybolanlar
        for bid in list(self.last_seen_ts.keys()):
            if bid not in current_bottle_ids:
                if not self.armed.get(bid, False):
                    if now - self.last_seen_ts[bid] > 10:
                        self.last_seen_ts.pop(bid, None)
                        self.near_start_ts.pop(bid, None)
                        self.armed.pop(bid, None)
                    continue

                if now - self.last_seen_ts[bid] >= self.disappear_time:
                    events.append(f"ŞÜPHELİ OLAY: bottle ID {bid} kayboldu!")
                    self.last_seen_ts.pop(bid, None)
                    self.near_start_ts.pop(bid, None)
                    self.armed.pop(bid, None)

        return events