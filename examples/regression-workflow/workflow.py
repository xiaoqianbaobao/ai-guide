"""A single-process model of a regression workflow, not a production scheduler."""
from dataclasses import dataclass, field


TRANSITIONS = {
    ("investigating", "diagnosis_ready"): "awaiting_review",
    ("awaiting_review", "review_approved"): "awaiting_deployment",
    ("awaiting_deployment", "deployment_finished"): "verifying",
    ("verifying", "recovered"): "resolved",
    ("verifying", "still_regressed"): "investigating",
}


@dataclass
class Task:
    id: str
    state: str = "investigating"
    findings: list[str] = field(default_factory=list)
    seen_events: dict[str, str] = field(default_factory=dict)

    def apply(self, event_id: str, event: str) -> bool:
        if not event_id:
            raise ValueError("event id is required")
        if event_id in self.seen_events:
            if self.seen_events[event_id] != event:
                raise ValueError("event id reused with different event")
            return False
        next_state = TRANSITIONS.get((self.state, event))
        if next_state is None:
            raise ValueError(f"event {event!r} is invalid in {self.state!r}")
        self.state = next_state
        self.seen_events[event_id] = event
        return True


if __name__ == "__main__":
    task = Task("alert-demo")
    task.findings.append("示例：延迟在版本变更后上升；原因尚待确认。")
    for event_id, event in [("1", "diagnosis_ready"), ("2", "review_approved"),
                            ("3", "deployment_finished"), ("4", "still_regressed")]:
        task.apply(event_id, event)
        print(event, "→", task.state)
