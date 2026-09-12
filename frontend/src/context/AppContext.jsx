import { createContext, useContext, useState } from "react";

const AppContext = createContext();

function createSessionId() {
  return (
    crypto.randomUUID?.() ||
    `session-${Date.now()}-${Math.random().toString(36).slice(2)}`
  );
}

export function AppProvider({ children }) {
  // ==========================================================
  // CORE APP STATE
  // ==========================================================
  const [uploadedFile, setUploadedFile] = useState(null);
  const [documentInfo, setDocumentInfo] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("idle");
  const [chatHistory, setChatHistory] = useState([]);
  const [selectedTool, setSelectedTool] = useState("chat");
  const [theme, setTheme] = useState("light");
  const [messageToSend, setMessageToSend] = useState(null);
  const [activeTool, setActiveTool] = useState(null);
  const [quizData, setQuizData] = useState(null);
  const [documentId, setDocumentId] = useState(null);
  

  // ==========================================================
  // AI AGENT SESSION & STUDY TRACKING
  // ==========================================================
  const [agentSessionId, setAgentSessionId] = useState(createSessionId);
  
  // MOVED INSIDE THE COMPONENT:
  const [studySession, setStudySession] = useState(null);
  const [flashcardData, setFlashcardData] = useState(null);

  const value = {
    uploadedFile,
    setUploadedFile,

    documentInfo,
    setDocumentInfo,

    uploadStatus,
    setUploadStatus,

    chatHistory,
    setChatHistory,

    selectedTool,
    setSelectedTool,

    theme,
    setTheme,

    messageToSend,
    setMessageToSend,

    activeTool,
    setActiveTool,

    flashcardData,
    setFlashcardData,

    quizData,
    setQuizData,

    documentId,
    setDocumentId,

    agentSessionId,
    setAgentSessionId,

    // EXPOSED TO THE REST OF THE APP:
    studySession,
    setStudySession,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  return useContext(AppContext);
}