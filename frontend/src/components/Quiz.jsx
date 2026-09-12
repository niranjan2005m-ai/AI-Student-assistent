import { useState } from "react";

function Quiz({ quizData, onClose }) {
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);

  const handleSelect = (questionIndex, optionIndex) => {
    if (showResults) return; // Prevent changing after submission
    setSelectedAnswers({ ...selectedAnswers, [questionIndex]: optionIndex });
  };

  return (
    <div className="w-full max-w-3xl rounded-xl border bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-bold text-indigo-600">Document Quiz</h2>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-600">Close</button>
      </div>

      {quizData.questions.map((q, qIndex) => (
        <div key={qIndex} className="mb-6 border-b pb-4 last:border-0">
          <p className="mb-3 font-medium text-slate-800">{qIndex + 1}. {q.question}</p>
          
          <div className="flex flex-col gap-2">
            {q.options.map((option, oIndex) => {
              const isSelected = selectedAnswers[qIndex] === oIndex;
              const isCorrect = q.correctAnswerIndex === oIndex;
              
              // Styling for when results are shown
              let resultStyle = "bg-slate-50 hover:bg-slate-100 border-slate-200";
              if (showResults) {
                if (isCorrect) resultStyle = "bg-green-50 border-green-500 text-green-700";
                else if (isSelected && !isCorrect) resultStyle = "bg-red-50 border-red-500 text-red-700";
                else resultStyle = "bg-slate-50 opacity-50";
              } else if (isSelected) {
                resultStyle = "bg-indigo-50 border-indigo-500 text-indigo-700";
              }

              return (
                <label 
                  key={oIndex} 
                  className={`flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-colors ${resultStyle}`}
                >
                  <input
                    type="radio"
                    name={`question-${qIndex}`}
                    className="h-4 w-4 text-indigo-600"
                    checked={isSelected}
                    onChange={() => handleSelect(qIndex, oIndex)}
                    disabled={showResults}
                  />
                  <span>{option}</span>
                </label>
              );
            })}
          </div>

          {/* Show Explanation if submitted */}
          {showResults && (
            <div className="mt-3 rounded bg-blue-50 p-3 text-sm text-blue-800">
              <span className="font-bold">Explanation:</span> {q.explanation}
            </div>
          )}
        </div>
      ))}

      <button
        onClick={() => setShowResults(true)}
        className="mt-4 rounded-lg bg-indigo-600 px-6 py-2 font-medium text-white hover:bg-indigo-700"
      >
        Submit Quiz
      </button>
    </div>
  );
}

export default Quiz;