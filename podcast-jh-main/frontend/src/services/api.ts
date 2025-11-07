import axios from 'axios';

// 네트워크 상태 체크용 헬퍼 함수
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const isNetworkError = (error: any): boolean => {
  return !error.response && (
    error.code === 'ECONNRESET' ||
    error.code === 'ETIMEDOUT' ||
    error.code === 'ECONNREFUSED' ||
    error.code === 'NETWORK_ERROR' ||
    error.message?.includes('Network Error')
  );
};

const API_BASE_URL = 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2분 타임아웃
  withCredentials: false, // CORS credentials
});

export interface PodcastRequest {
  topic?: string; // 주제 기반 팟캐스트 생성
  url?: string; // URL 기반 팟캐스트 생성
  duration_minutes?: number; // 팟캐스트 길이 (분)
  language?: string;
  tts_engine?: string;
  num_speakers?: number; // 화자 수 (2 또는 3)
  custom_voices?: Record<string, string>; // 사용자 정의 화자 매핑 (예: {"화자A": "rachel", "화자B": "adam"})
  style?: 'casual' | 'professional' | 'educational' | 'storytelling'; // 팟캐스트 스타일
}

export interface Speaker {
  id: string;
  name: string;
  gender: string;
  description: string;
  suitable_for: string;
}

export interface VoicesResponse {
  speakers: Record<string, Speaker>;
  description: string;
}

export interface PodcastResponse {
  podcast_id: string;
  status: string;
  message: string;
  script_path?: string;
  audio_path?: string;
}

export interface PodcastStatus {
  podcast_id: string;
  status: 'processing' | 'completed' | 'failed';
  message: string;
  script_path?: string;
  audio_path?: string;
  created_at?: string;
  updated_at?: string;
}

export interface DialogueMetadata {
  index: number;
  speaker: string;
  speaker_name: string;
  gender: string;
  text: string;
  start_time: number; // 초 단위
  end_time: number; // 초 단위
  duration: number; // 초 단위
}

export interface PodcastMetadata {
  podcast_id: string;
  total_duration: number;
  dialogue_count: number;
  dialogues: DialogueMetadata[];
}

export const podcastApi = {
  createPodcast: async (data: PodcastRequest): Promise<PodcastResponse> => {
    const response = await api.post('/podcasts/generate', data);
    return response.data;
  },

  createPodcastFromPDF: async (
    pdfFile: File,
    duration_minutes: number,
    language: string,
    tts_engine: string,
    num_speakers: number,
    custom_voices: Record<string, string>,
    style: string = 'casual'
  ): Promise<PodcastResponse> => {
    const formData = new FormData();
    formData.append('pdf_file', pdfFile);
    formData.append('duration_minutes', duration_minutes.toString());
    formData.append('language', language);
    formData.append('tts_engine', tts_engine);
    formData.append('num_speakers', num_speakers.toString());
    formData.append('custom_voices', JSON.stringify(custom_voices));
    formData.append('style', style);

    const response = await axios.post(
      `${API_BASE_URL}/podcasts/generate-from-pdf`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 180000, // PDF 처리는 더 긴 타임아웃 (3분)
      }
    );
    return response.data;
  },

  getStatus: async (podcastId: string, retryCount: number = 0): Promise<PodcastStatus> => {
    try {
      const response = await api.get(`/podcasts/status/${podcastId}`, {
        timeout: 15000, // 상태 확인은 더 짧은 타임아웃
      });
      return response.data;
    } catch (error) {
      // 네트워크 오류나 타임아웃 시 재시도
      if (retryCount < 2 && (
        axios.isAxiosError(error) && (
          isNetworkError(error) || !error.response
        )
      )) {
        // 지수 백오프로 재시도
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, retryCount) * 1000));
        return podcastApi.getStatus(podcastId, retryCount + 1);
      }
      throw error;
    }
  },

  listPodcasts: async (): Promise<{podcasts: PodcastStatus[]}> => {
    const response = await api.get('/podcasts/list');
    return response.data;
  },

  downloadAudio: (podcastId: string): string => {
    return `${API_BASE_URL}/podcasts/download/${podcastId}/audio`;
  },

  downloadScript: (podcastId: string): string => {
    return `${API_BASE_URL}/podcasts/download/${podcastId}/script`;
  },

  getMetadata: async (podcastId: string): Promise<PodcastMetadata> => {
    const response = await api.get(`/podcasts/download/${podcastId}/metadata`);
    return response.data;
  },

  getVoices: async (): Promise<VoicesResponse> => {
    const response = await api.get('/voices');
    return response.data;
  },
};

export default api;