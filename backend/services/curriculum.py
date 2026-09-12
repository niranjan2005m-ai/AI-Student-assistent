from dataclasses import dataclass, field


@dataclass
class Curriculum:
    topics: list[str] = field(default_factory=list)
    current_index: int = 0

    @property
    def current_topic(self) -> str | None:
        if 0 <= self.current_index < len(self.topics):
            return self.topics[self.current_index]
        return None

    def advance(self) -> str | None:
        if self.current_index + 1 >= len(self.topics):
            return None

        self.current_index += 1
        return self.current_topic


_curriculums: dict[str, Curriculum] = {}


def get_curriculum(session_id: str) -> Curriculum:
    if session_id not in _curriculums:
        _curriculums[session_id] = Curriculum()

    return _curriculums[session_id]


def set_curriculum(
    session_id: str,
    topics: list[str],
):
    _curriculums[session_id] = Curriculum(
        topics=topics,
        current_index=0,
    )