import apiClient from './api';

export async function uploadImage(file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await apiClient.post('/api/v1/images/upload', formData);
  return data.data.analysis_id;
}
