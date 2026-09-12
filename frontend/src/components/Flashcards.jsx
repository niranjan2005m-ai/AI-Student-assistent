import { useState } from "react";
import { ChevronLeft, ChevronRight, RotateCcw, X } from "lucide-react";

function Flashcards({ flashcards, onClose }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);

  if (!flashcards || flashcards.length === 0) {
    return (
      <div className="mx-auto w-full max-w-3xl rounded-2xl border border-slate-700 bg-slate-900 p-6 text-center text-slate-300">
        No flashcards available.
      </div>
    );
  }

  const currentCard = flashcards[currentIndex];

  const goNext = () => {
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex((prev) => prev + 1);
      setFlipped(false);
    }
  };

  const goPrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
      setFlipped(false);
    }
  };

  const resetCard = () => {
    setFlipped(false);
  };

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-6">
      {/* Header */}
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">
            Flashcards
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Card {currentIndex + 1} of {flashcards.length}
          </p>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-800 hover:text-white"
        >
          <X size={16} />
          Close
        </button>
      </div>

      {/* Progress */}
      <div className="mb-5 h-1.5 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-indigo-500 transition-all duration-300"
          style={{
            width: `${((currentIndex + 1) / flashcards.length) * 100}%`,
          }}
        />
      </div>

      {/* Flashcard */}
      <button
        type="button"
        onClick={() => setFlipped((prev) => !prev)}
        className="group relative min-h-[320px] w-full rounded-2xl border border-slate-700 bg-slate-800 p-8 text-left shadow-xl transition hover:border-indigo-500/60 hover:bg-slate-750"
      >
        <div className="flex min-h-[280px] flex-col justify-center">
          <p className="mb-4 text-xs font-semibold uppercase tracking-wider text-indigo-400">
            {flipped ? "Answer" : "Question"}
          </p>

          <p className="text-xl font-medium leading-8 text-white">
            {flipped
              ? currentCard.back
              : currentCard.front}
          </p>

          <p className="mt-8 text-xs text-slate-500">
            Click the card to {flipped ? "see the question" : "reveal the answer"}
          </p>
        </div>
      </button>

      {/* Controls */}
      <div className="mt-5 flex items-center justify-center gap-3">
        <button
          type="button"
          onClick={goPrevious}
          disabled={currentIndex === 0}
          className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2.5 text-sm font-medium text-slate-200 transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <ChevronLeft size={17} />
          Previous
        </button>

        <button
          type="button"
          onClick={resetCard}
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-700 bg-slate-800 text-slate-300 transition hover:bg-slate-700 hover:text-white"
          title="Reset card"
        >
          <RotateCcw size={16} />
        </button>

        <button
          type="button"
          onClick={goNext}
          disabled={currentIndex === flashcards.length - 1}
          className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Next
          <ChevronRight size={17} />
        </button>
      </div>
    </div>
  );
}

export default Flashcards;