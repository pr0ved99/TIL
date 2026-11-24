"""Track the newest measurement for one SIM-06 DiagnosticStatus name."""


class DiagnosticSample:
    STALE_AFTER_NS = 1_500_000_000

    def __init__(self, name):
        self.name = name
        self.stamp_ns = None
        self.valid = "unknown"

    def receive(self, msg, now_ns):
        matches = [status for status in msg.status if status.name == self.name]
        if not matches:
            return
        stamp = msg.header.stamp
        stamp_ns = stamp.sec * 1_000_000_000 + stamp.nanosec
        if not 0 < stamp_ns <= now_ns:
            return
        if self.stamp_ns is not None and stamp_ns <= self.stamp_ns <= now_ns:
            return

        self.stamp_ns = stamp_ns
        self.valid = "unknown"
        if len(matches) == 1:
            flags = [item.value for item in matches[0].values if item.key == "valid"]
            if len(flags) == 1 and flags[0] in ("true", "false"):
                self.valid = flags[0]

    def state(self, now_ns):
        if self.stamp_ns is None or self.stamp_ns > now_ns:
            self.stamp_ns = None
            self.valid = "unknown"
            return "WAITING", "WAITING"
        age_ns = now_ns - self.stamp_ns
        freshness = "STALE" if age_ns >= self.STALE_AFTER_NS else "FRESH"
        return freshness, f"{freshness} valid={self.valid} age={age_ns / 1e9:.3f} s"
