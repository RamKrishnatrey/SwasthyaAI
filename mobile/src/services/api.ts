import axios, { type AxiosInstance } from 'axios';
import Constants from 'expo-constants';
import * as SecureStore from 'expo-secure-store';

function resolveApiBaseUrl(): string {
  const configured = process.env.EXPO_PUBLIC_API_URL;
  if (configured) return configured.replace(/\/$/, '');
  const hostUri = Constants.expoConfig?.hostUri;
  const host = hostUri?.split(':')[0];
  // Expo Go's host is the developer computer's LAN IP, reachable from a phone.
  if (host) return `http://${host}:8000`;
  return 'http://127.0.0.1:8000';
}

const client: AxiosInstance = axios.create({
  baseURL: resolveApiBaseUrl(),
  timeout: 20000,
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  response => response,
  error => {
    const detail = error?.response?.data?.detail;
    if (typeof detail === 'string') error.message = detail;
    else if (!error?.response) error.message = 'Cannot reach SwasthyaAI backend. Check that Backend 2 is running and the phone and computer share Wi-Fi.';
    return Promise.reject(error);
  },
);

const api = {
  baseURL: resolveApiBaseUrl(),

  async register(data: { email: string; password: string; full_name: string; phone?: string; role?: string; language?: string }) {
    const { data: result } = await client.post('/api/auth/register', data);
    await this.saveTokens(result);
    return result;
  },
  async login(email: string, password: string) {
    const { data } = await client.post('/api/auth/login', { email, password });
    await this.saveTokens(data);
    return data;
  },
  async saveTokens(result: any) {
    if (result?.access_token) await SecureStore.setItemAsync('access_token', result.access_token);
    if (result?.refresh_token) await SecureStore.setItemAsync('refresh_token', result.refresh_token);
    if (result?.user) await SecureStore.setItemAsync('user', JSON.stringify(result.user));
  },
  async logout() {
    try { await client.post('/api/auth/logout'); } catch { /* Local sign-out must still work. */ }
    await Promise.all([
      SecureStore.deleteItemAsync('access_token'),
      SecureStore.deleteItemAsync('refresh_token'),
      SecureStore.deleteItemAsync('user'),
    ]);
  },
  async refreshToken() {
    const refresh_token = await SecureStore.getItemAsync('refresh_token');
    if (!refresh_token) throw new Error('Please sign in again.');
    const { data } = await client.post('/api/auth/refresh', { refresh_token });
    if (data?.access_token) await SecureStore.setItemAsync('access_token', data.access_token);
    return data?.access_token;
  },
  async getCurrentUser() {
    const { data } = await client.get('/api/auth/me');
    return data?.user ?? data;
  },
  async getPatientProfile() {
    const { data } = await client.get('/api/auth/me/patient-profile');
    return data?.profile ?? data;
  },
  async updateProfile(payload: Record<string, unknown>) {
    const { data } = await client.put('/api/auth/me', payload);
    return data?.user ?? data;
  },
  async createConversation(payload: Record<string, unknown>) {
    const { data } = await client.post('/api/conversations', payload);
    return { conversation: data };
  },
  async getConversationMessages(id: string, limit = 50) {
    const { data } = await client.get(`/api/conversations/${encodeURIComponent(id)}/messages`, { params: { page_size: limit } });
    return data;
  },
  async sendMessage(id: string, payload: { content: string; content_type?: string }) {
    const { data } = await client.post(`/api/conversations/${encodeURIComponent(id)}/messages`, {
      role: 'user', content: payload.content, content_type: payload.content_type ?? 'text',
    });
    return data;
  },
  async startSymptomAssessment(payload: Record<string, unknown>) {
    const { data } = await client.post('/api/intake', payload);
    return data;
  },
  async submitFollowUpAnswers(id: string, answers: Record<string, string>) {
    const { data } = await client.post('/api/intake/followup', answers, { params: { session_id: id } });
    return data;
  },
  async getTriageResult(id: string) {
    const { data } = await client.post('/api/triage', { session_id: id, confirmed_summary: { original_text: '', symptoms: [] }, language: 'en' });
    return data;
  },
  async getUpcomingAppointments(limit = 10) {
    const { data } = await client.get('/api/appointments/upcoming', { params: { limit } });
    return data;
  },
  async getAppointments(params: Record<string, unknown> = {}) {
    const { data } = await client.get('/api/appointments', { params });
    return data;
  },
  async searchClinicians(params: Record<string, unknown>) {
    const { data } = await client.post('/api/match', params);
    return data;
  },
  async getAvailableSlots(clinicianId: string, days = 30) {
    const { data } = await client.get('/api/appointments/clinician/available-slots', { params: { clinician_id: clinicianId, days } });
    return data;
  },
  async bookAppointment(payload: Record<string, unknown>) {
    const { data } = await client.post('/api/appointments', payload);
    return data;
  },
  async cancelAppointment(id: string, reason: string) {
    const { data } = await client.delete(`/api/appointments/${encodeURIComponent(id)}`, { params: { reason } });
    return data;
  },
  async getUpcomingReminders(hours = 24) {
    const { data } = await client.get('/api/reminders/upcoming', { params: { hours } });
    return data;
  },
};

export default api;
