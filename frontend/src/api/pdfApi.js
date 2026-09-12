import api from "./axios";

export const uploadPDF = async (file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/upload/", formData, {
    onUploadProgress: (progressEvent) => {
      if (!onProgress || !progressEvent.total) return;

      const percent = Math.round(
        (progressEvent.loaded * 100) / progressEvent.total
      );

      onProgress(percent);
    },
  });

  return response.data;
};