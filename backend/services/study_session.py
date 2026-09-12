from dataclasses import dataclass, field


@dataclass
class StudySession:
    session_id: str

    current_topic: str | None = None

    current_question: str | None = None

    last_score: int | None = None

    attempts: int = 0
    curriculum: list[str] = field(default_factory=list)
    curriculum_index: int = 0

    weak_topics: list[str] = field(
        default_factory=list
    )

    mastered_topics: list[str] = field(
        default_factory=list
    )


# Temporary in-memory session store.
# Later we can move this to Redis/database.
_sessions: dict[str, StudySession] = {}


def get_or_create_session(
    session_id: str
) -> StudySession:

    if session_id not in _sessions:

        _sessions[session_id] = StudySession(
            session_id=session_id
        )

    return _sessions[session_id]


def update_from_evaluation(
    session: StudySession,
    evaluation: dict
):

    score = evaluation.get(
        "score"
    )

    if isinstance(score, int):
        session.last_score = score

    session.attempts += 1

    weak_topics = evaluation.get(
        "weak_topics",
        []
    )

    if not isinstance(
        weak_topics,
        list
    ):
        weak_topics = [
            str(weak_topics)
        ]

    for topic in weak_topics:

        topic = str(topic).strip()

        if (
            topic
            and topic not in session.weak_topics
        ):
            session.weak_topics.append(
                topic
            )

    # Treat 7/10 as the initial mastery threshold.
    if (
        isinstance(score, int)
        and score >= 7
    ):
        current_topic = session.current_topic

        if (
            current_topic
            and current_topic not in session.mastered_topics
        ):
            session.mastered_topics.append(
                current_topic
            )

        # Remove only the primary topic from weak topics.
        if (
            current_topic
            and current_topic in session.weak_topics
        ):
            session.weak_topics.remove(
                current_topic
            )


def set_topic(
    session: StudySession,
    topic: str
):
    """
    Start a new primary study topic.
    """

    session.current_topic = topic
    session.current_question = None
    session.last_score = None
    session.attempts = 0


def set_question(
    session: StudySession,
    question: str
):

    session.current_question = question


def session_summary(
    session: StudySession
) -> dict:

    return {
        "session_id": session.session_id,
        "current_topic": session.current_topic,
        "current_question": session.current_question,
        "last_score": session.last_score,
        "attempts": session.attempts,
        "weak_topics": session.weak_topics,
        "mastered_topics": session.mastered_topics,
        "curriculum": session.curriculum,
        "curriculum_index": session.curriculum_index
    }

def set_question(
    session,
    question: str | None,
    expected_points: list[str] | None = None,
):
    session.current_question = question
    session.current_expected_points = (
        expected_points or []
    )