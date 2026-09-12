import { useState } from "react";
import { generateQuiz } from "../../api/quizApi";
import {
  NotebookPen,
  FileText,
  Brain,
  GraduationCap,
} from "lucide-react";
import { useApp } from "../../context/AppContext";

const actions = [
  {
    icon: NotebookPen,
    title: "Generate Notes",
    prompt: `Generate Notes`,
  },
  {
    icon: FileText,
    title: "Summary",
    prompt: `Summary`,
  },
  {
    icon: GraduationCap,
    title: "Quiz",
    prompt: `Quiz Prompt`, 
  },
  {
    icon: Brain,
    title: "Flashcards",
    prompt: `Flashcards`,
  },
];

function QuickActions() {
  const { 
    documentId, 
    setMessageToSend, 
    uploadStatus, 
    setActiveTool, 
    setQuizData, 
    setFlashcardData 
  } = useApp();
  
  const [isLoading, setIsLoading] = useState(false);

  const handleActionClick = async (action) => {
    if (!documentId) {
      alert("Please upload a document first.");
      return;
    }

    if (action.title === "Quiz") {
      setIsLoading(true);

      try {
        const quiz = await generateQuiz(documentId);
        setQuizData(quiz);
        setActiveTool("quiz");
      } catch (error) {
        console.error(error);
        alert(
          error.response?.data?.detail ||
            "Failed to generate quiz."
        );
      } finally {
        setIsLoading(false);
      }

      return;
    }

    if (action.title === "Flashcards") {
      setIsLoading(true);

      try {
        const response = await fetch(
          "http://127.0.0.1:8000/chat/agent",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              question: "Flashcards",
              chat_history: [],
              session_id: "default",
              document_id: documentId,
            }),
          }
        );

        if (!response.ok) {
          throw new Error("Failed to generate flashcards.");
        }

        const data = await response.json();

        // Backend returns JSON text inside answer
        const flashcards =
          typeof data.answer === "string"
            ? JSON.parse(data.answer)
            : data.answer;

        setFlashcardData(flashcards);
        setActiveTool("flashcards");
      } catch (error) {
        console.error(error);
        alert(
          error.message ||
            "Failed to generate flashcards."
        );
      } finally {
        setIsLoading(false);
      }

      return;
    }

    setMessageToSend({
      prompt: action.prompt,
      documentId,
    });

    setActiveTool("chat");
  };

  return (
    <div className="mt-2 flex flex-wrap justify-center gap-2">
      {actions.map((action) => {
        const Icon = action.icon;
        
        // Updated to show "Generating..." for both Quiz and Flashcards
        const isCurrentlyLoading = 
          isLoading && (action.title === "Quiz" || action.title === "Flashcards");

        return (
          <button
            key={action.title}
            disabled={uploadStatus !== "ready" || isLoading}
            onClick={() => handleActionClick(action)}
            className="group inline-flex items-center gap-2 rounded-xl border border-slate-600 bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-100 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-indigo-400 hover:bg-slate-700 hover:text-white hover:shadow-md disabled:cursor-not-allowed disabled:border-slate-700 disabled:bg-slate-800 disabled:text-slate-400 disabled:opacity-60"
          >
            <Icon 
              size={16} 
              strokeWidth={2} 
              className="text-slate-300 group-hover:text-indigo-300" 
            />
            <span className="whitespace-nowrap text-slate-100">
              {isCurrentlyLoading ? "Generating..." : action.title}
            </span>
          </button>
        );
      })}
    </div>
  );
}

export default QuickActions;