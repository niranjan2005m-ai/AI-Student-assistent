import api from "./axios";

export async function generateQuiz(documentId) {
  const response = await api.post("/quiz", {
    document_id: documentId,
  });

  return response.data;
}