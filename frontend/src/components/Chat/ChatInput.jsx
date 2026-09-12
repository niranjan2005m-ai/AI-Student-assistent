import { useRef, useState, useEffect } from "react";
import { Plus, Mic, ArrowUp, Loader2, FileText } from "lucide-react";
import { uploadPDF } from "../../api/pdfApi";
import { streamAgent } from "../../api/chatApi";
import { useApp } from "../../context/AppContext";

function ChatInput() {
  const fileInputRef = useRef(null);

  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const {
    uploadedFile,
    setUploadedFile,
    setDocumentInfo,
    setUploadStatus,
    uploadStatus,
    chatHistory,
    setChatHistory,
    messageToSend,
    setMessageToSend,
    documentId,
    setDocumentId,
    agentSessionId,
  } = useApp();

  // ==========================================================
  // REMOVE FILE
  // ==========================================================
  const handleRemoveFile = () => {
    setUploadedFile(null);
    setDocumentInfo(null);
    setDocumentId(null);
    setUploadStatus("idle");
    setProgress(0);
    
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // ==========================================================
  // UPLOAD PDF
  // ==========================================================
  const handleFileChange = async (e) => {
    const file = e.target.files[0];

    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Please select a PDF.");
      return;
    }

    try {
      setUploadedFile(file);
      setUploadStatus("uploading");
      setProgress(0);

      const data = await uploadPDF(file, setProgress);

      setDocumentInfo(data);
      setDocumentId(data.document_id);
      
      setUploadStatus("ready");
      setProgress(0);
      
    } catch (err) {
      console.error(err);
      setUploadStatus("error");
      setProgress(0);
    }
  };

  // ==========================================================
  // SEND MESSAGE TO AI AGENT
  // ==========================================================
 const sendToAgent = async (prompt, actionDocumentId = documentId) => {
  if (!prompt?.trim() || loading) {
    return;
  }

  const attachment = uploadedFile
    ? {
        fileName: uploadedFile.name,
        status: "Indexed successfully",
      }
    : null;

  const userMessage = {
    role: "user",
    content: prompt,
    attachment,
  };

  const updatedHistory = [...chatHistory, userMessage];

  setChatHistory(updatedHistory);
  setLoading(true);

  setUploadedFile(null);
  setMessage("");

  setChatHistory((prev) => [
    ...prev,
    {
      role: "assistant",
      content: "",
    },
  ]);

  // IMPORTANT:
  // Keep the document ID separate from the user's question.
  const backendPrompt = prompt;

  const backendHistory = updatedHistory;

  try {
    await streamAgent(
      backendPrompt,
      backendHistory,
      agentSessionId,
      actionDocumentId,
      (chunk) => {
        setChatHistory((prev) => {
          if (prev.length === 0) {
            return prev;
          }

          const updated = [...prev];
          const lastIndex = updated.length - 1;

          updated[lastIndex] = {
            ...updated[lastIndex],
            content: (updated[lastIndex].content || "") + chunk,
          };

          return updated;
        });
      }
    );
  } catch (error) {
    console.error("Agent error:", error);

    setChatHistory((prev) => {
      const updated = [...prev];
      const lastIndex = updated.length - 1;

      updated[lastIndex] = {
        ...updated[lastIndex],
        content: `⚠️ ${error.message || "Agent error."}`,
      };

      return updated;
    });
  } finally {
    setLoading(false);
  }
};

  // ==========================================================
  // NORMAL SEND
  // ==========================================================
  const handleSend = async () => {
    if (!message.trim() || (uploadedFile && uploadStatus !== "ready") || loading) {
      return;
    }

    const prompt = message.trim();
    await sendToAgent(prompt);
  };

  // ==========================================================
  // QUICK ACTIONS
  // ==========================================================
  useEffect(() => {
    if (!messageToSend) {
      return;
    }

    const prompt =
      typeof messageToSend === "string"
        ? messageToSend
        : messageToSend.prompt;

    const actionDocumentId =
      typeof messageToSend === "string"
        ? documentId
        : messageToSend.documentId;

    setMessageToSend(null);

    sendToAgent(prompt, actionDocumentId);
  }, [messageToSend]);

  return (
    <div className="bg-transparent px-4 py-3">
      <div className="mx-auto w-full max-w-3xl">

        <div className="mt-1 w-full rounded-2xl border border-slate-700 bg-slate-800 shadow-sm transition focus-within:border-indigo-500 focus-within:shadow-md">

          {/* Pending PDF attachment inside composer */}
          {uploadedFile && (
            <div className="px-3 pt-3">
              <div className="inline-flex items-center gap-3 rounded-xl border border-slate-600 bg-slate-900 px-3 py-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/15">
                  <FileText size={17} className="text-indigo-400" />
                </div>

                <div className="min-w-0">
                  <p className="max-w-[220px] truncate text-xs font-medium text-slate-200">
                    {uploadedFile.name}
                  </p>

                  <p className="text-[11px] text-emerald-400">
                    {uploadStatus === "uploading"
                      ? "Uploading..."
                      : uploadStatus === "ready"
                      ? "Indexed successfully"
                      : uploadStatus === "error"
                      ? "Upload failed"
                      : "PDF"}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={handleRemoveFile}
                  className="ml-1 text-slate-500 hover:text-slate-200"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {/* Message row */}
          <div className="flex items-center gap-2 px-3 py-2">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-slate-400 transition hover:bg-slate-700 hover:text-slate-200 disabled:opacity-50"
            >
              <Plus size={19} />
            </button>

            <textarea
              rows={1}
              placeholder={
                uploadedFile && uploadStatus !== "ready"
                  ? "Upload a PDF to start..."
                  : "Ask anything..."
              }
              className="min-h-[38px] max-h-32 flex-1 resize-none overflow-y-auto bg-transparent px-1 py-2 text-sm text-white outline-none placeholder:text-slate-400"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              disabled={loading || (uploadedFile && uploadStatus !== "ready")}
            />

            <button
              type="button"
              disabled
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-slate-400 hover:bg-slate-700 hover:text-slate-200"
            >
              <Mic size={18} />
            </button>

            <button
              type="button"
              onClick={handleSend}
              disabled={
                loading || 
                (uploadedFile && uploadStatus !== "ready") || 
                (!message.trim() && !uploadedFile)
              }
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-white transition hover:bg-indigo-500 disabled:bg-indigo-900/50 disabled:text-slate-400"
            >
              {loading ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <ArrowUp size={17} />
              )}
            </button>
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          hidden
          onChange={handleFileChange}
        />

      </div>
    </div>
  );
}

export default ChatInput;