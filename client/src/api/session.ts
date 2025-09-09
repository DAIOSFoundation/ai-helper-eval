import apiClient from './client';

export interface SessionStartRequest {
  user_id?: string;
  test_type?: string;
}

export interface SessionStartResponse {
  session_id: string;
  message: string;
  welcome_message: string;
}

export interface MessageRequest {
  session_id: string;
  message: string;
}

export interface MessageResponse {
  session_id: string;
  response: string;
  intent: string;
  is_complete: boolean;
  diagnosis_result?: {
    cdi_score: number;
    rcmas_score: number;
    bdi_score: number;
    interpretation: {
      cdi: string;
      rcmas: string;
      bdi: string;
    };
  };
}

export interface SessionHistory {
  session_id: string;
  conversation_history: Array<{
    user: string;
    system: string;
    intent: string;
    timestamp: string;
  }>;
}

export interface SessionStatus {
  session_id: string;
  is_diagnosis_complete: boolean;
  current_scores: {
    cdi_score: number | null;
    rcmas_score: number | null;
    bdi_score: number | null;
  };
}

export const sessionAPI = {
  startSession: async (data: SessionStartRequest = {}): Promise<SessionStartResponse> => {
    console.log('API: Starting session with data:', JSON.stringify(data, null, 2));
    try {
      const response = await apiClient.post('/start_session', data);
      console.log('API: Session start response:', JSON.stringify(response.data, null, 2));
      return response.data;
    } catch (error) {
      console.error('API: Session start error:', error);
      throw error;
    }
  },

  sendMessage: async (data: MessageRequest): Promise<MessageResponse> => {
    console.log('API: Sending message with data:', JSON.stringify(data, null, 2));
    const response = await apiClient.post('/message', data);
    console.log('API: Message response:', JSON.stringify(response.data, null, 2));
    return response.data;
  },

  resetSession: async (sessionId: string): Promise<{ session_id: string; message: string }> => {
    const response = await apiClient.post('/reset_session', { session_id: sessionId });
    return response.data;
  },

  getSessionHistory: async (sessionId: string): Promise<SessionHistory> => {
    const response = await apiClient.get('/session_history', {
      params: { session_id: sessionId }
    });
    return response.data;
  },

  getSessionStatus: async (sessionId: string): Promise<SessionStatus> => {
    const response = await apiClient.get('/status', {
      params: { session_id: sessionId }
    });
    return response.data;
  },

  healthCheck: async (): Promise<{ status: string; active_sessions: number }> => {
    const response = await apiClient.get('/health');
    return response.data;
  }
};
