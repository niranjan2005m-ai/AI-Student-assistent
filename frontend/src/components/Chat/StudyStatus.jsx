import { useApp } from "../../context/AppContext";

function StudyStatus() {
  const {
    studySession,
  } = useApp();

  if (!studySession) {
    return null;
  }

  return (
    <div className="mb-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">

        <div>
          <p className="text-xs font-medium uppercase text-slate-400">
            Current Topic
          </p>
          <p className="mt-1 font-semibold text-slate-800">
            {studySession.current_topic || "—"}
          </p>
        </div>

        <div>
          <p className="text-xs font-medium uppercase text-slate-400">
            Last Score
          </p>
          <p className="mt-1 font-semibold text-slate-800">
            {studySession.last_score !== null
              ? `${studySession.last_score}/10`
              : "—"}
          </p>
        </div>

        <div>
          <p className="text-xs font-medium uppercase text-slate-400">
            Attempts
          </p>
          <p className="mt-1 font-semibold text-slate-800">
            {studySession.attempts ?? 0}
          </p>
        </div>

        <div>
          <p className="text-xs font-medium uppercase text-slate-400">
            Mastered
          </p>
          <p className="mt-1 font-semibold text-slate-800">
            {studySession.mastered_topics?.length ?? 0}
          </p>
        </div>

      </div>
    </div>
  );
}

export default StudyStatus;