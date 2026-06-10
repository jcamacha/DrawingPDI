import apiClient from './api';

const BASE = import.meta.env.VITE_API_URL;

export async function triggerAnalysis(analysisId) {
  const { data } = await apiClient.post(`/api/v1/images/${analysisId}/analyze`);
  return data.data;
}

export const getPdfUrl = (id) => `${BASE}/api/v1/reports/${id}/pdf`;
export const getJsonUrl = (id) => `${BASE}/api/v1/reports/${id}/json`;
