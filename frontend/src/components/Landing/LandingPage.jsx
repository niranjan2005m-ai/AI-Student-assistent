import { useApp } from "../../context/AppContext";
import Hero from "./Hero";
import QuickActions from "./QuickActions";
import ChatMessages from "../Chat/ChatMessages";
import ChatInput from "../Chat/ChatInput";
import Quiz from "../Quiz";
import Flashcards from "../Flashcards";

function LandingPage() {
  const {
    uploadStatus,
    activeTool,
    setActiveTool,
    quizData,
    chatHistory,
    activeDocumentId,
    flashcardData,
  } = useApp();

  const hasMessages = chatHistory.length > 0;

  return (
    <div className="min-h-screen bg-slate-950">

      {/* Background Texture */}
      <div className="pointer-events-none fixed inset-0 opacity-[0.035]">
        <div
          className="h-full w-full"
          style={{
            backgroundImage:
              "radial-gradient(circle, #64748b 0.7px, transparent 0.7px)",
            backgroundSize: "24px 24px",
          }}
        />
      </div>

      <div className="relative z-10">

        {/* Header */}
        <div className="mx-auto flex max-w-5xl items-center px-6 py-5">
          <h1 className="text-xl font-semibold text-white">
            AI Student Assistant
          </h1>
        </div>

        {activeTool === "quiz" && quizData ? (
          
          <div className="mx-auto h-[calc(100vh-95px)] max-w-5xl overflow-y-auto">
            <Quiz
              quizData={quizData}
              onClose={() => setActiveTool("chat")}
            />
          </div>

        ) : activeTool === "flashcards" && flashcardData ? (
          
          <div className="mx-auto h-[calc(100vh-95px)] max-w-5xl overflow-y-auto">
            <Flashcards
              flashcards={flashcardData}
              onClose={() => setActiveTool("chat")}
            />
          </div>

        ) : (
          
          <div className="relative h-[calc(100vh-95px)] w-full">

            {/* Conversation only when something has been sent/uploaded */}
            {hasMessages ? (
              <div className="absolute inset-0">
                <ChatMessages />
              </div>
            ) : (
              /* Keep the exact same landing position */
              <div className="absolute inset-0 flex flex-col items-center justify-center pb-24">
                <Hero />
              </div>
            )}

            {/* Bottom controls always stay in the same position */}
            <div className="absolute bottom-0 left-0 right-0 z-30">
              <div className="bg-gradient-to-t from-slate-950 via-slate-950/95 to-transparent pb-4 pt-10">
                <div className="mx-auto max-w-3xl px-4">

                  <ChatInput />

                  <div className="mt-2">
                    <QuickActions />
                  </div>

                </div>
              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}

export default LandingPage;