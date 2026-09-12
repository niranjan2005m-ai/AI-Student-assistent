import api from "./axios";

// ============================================================
// EXISTING NON-STREAMING RAG CHAT
// ============================================================

export const askQuestion = async (
  question,
  chatHistory = []
) => {
  const response = await api.post("/chat/", {
    question,
    chat_history: chatHistory,
  });

  return response.data;
};

// ============================================================
// EXISTING RAG STREAMING
// ============================================================

export async function streamQuestion(
  question,
  chatHistory,
  onChunk
) {
  const response = await fetch(
    "http://127.0.0.1:8000/chat/stream",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
        chat_history: chatHistory,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      `Request failed: ${response.status}`
    );
  }

  if (!response.body) {
    throw new Error(
      "Streaming not supported."
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } =
      await reader.read();

    if (done) break;

    onChunk(
      decoder.decode(value, {
        stream: true,
      })
    );
  }
}

// ============================================================
// NEW: AI AGENT STREAMING (Server-Sent Events)
// ============================================================

export async function streamAgent(
  question,
  chatHistory,
  sessionId,
  documentId,
  onChunk
) {
  const response = await fetch(
    "http://127.0.0.1:8000/chat/agent/stream",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
        chat_history: chatHistory,
        session_id: sessionId,
        document_id: documentId,
      }),
    }
  );

  if (!response.ok) {
    let errorMessage = `Agent request failed: ${response.status}`;

    try {
      const errorData = await response.json();

      if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(errorMessage);
  }

  if (!response.body) {
    throw new Error(
      "Agent streaming is not supported."
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    
    // Split the buffer by the SSE event delimiter
    const events = buffer.split("\n\n");
    
    // Keep the last partial event in the buffer (in case it got cut off mid-network chunk)
    buffer = events.pop() || "";

    for (const event of events) {
      // Find the line that actually contains the data
      const line = event.split("\n").find((line) => line.startsWith("data: "));
      
      if (!line) continue;
      
      const data = line.slice(6);
      
      // Check for our completion signal
      if (data === "[DONE]") {
        return;
      }
      
      try {
        const chunk = JSON.parse(data);
        if (chunk) {
          onChunk(chunk);
        }
      } catch {
        // Ignore malformed/incomplete SSE events
      }
    }
  }
}

export const askAgent = async (
  question,
  chatHistory = [],
  sessionId,
  documentId
) => {
  const response = await api.post("/chat/agent", {
    question,
    chat_history: chatHistory,
    session_id: sessionId,
    document_id: documentId,
  });

  return response.data;
};