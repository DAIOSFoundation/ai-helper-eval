import apiClient from './client';

export interface TestSession {
  id: string;
  user_id: string;
  test_type: string;
  status: string;
  total_questions: number;
  completed_questions: number;
  total_score: number;
  started_at: string;
  completed_at?: string;
  session_round: number; // 추가: 회차 정보
}

export interface TestResponse {
  id: string;
  session_id: string;
  question_id: string;
  question_text: string;
  user_response: string;
  detected_intent: string;
  calculated_score: number;
  expert_score?: number;
  keywords: string;
  created_at: string;
}

export interface ExpertFeedback {
  id: string;
  response_id: string;
  expert_id: string;
  feedback_score: number;
  feedback_comment?: string;
  keywords_suggested?: string;
  created_at: string;
  expert_username: string;
}

export interface DashboardStats {
  overall_stats: {
    total_sessions: number;
    total_users: number;
    avg_score: number;
    total_responses: number;
  };
  test_type_stats: Array<{
    test_type: string;
    session_count: number;
    avg_score: number;
    completed_count: number;
  }>;
  recent_sessions: Array<TestSession & {
    username: string;
    full_name?: string;
  }>;
}

export const dashboardAPI = {
  getStats: async (userId?: string): Promise<DashboardStats | { user_sessions: TestSession[]; total_sessions: number }> => {
    const params = userId ? { user_id: userId } : {};
    const response = await apiClient.get('/dashboard/stats', { params });
    return response.data;
  },

  getUserSessions: async (userId: string, limit: number = 50): Promise<TestSession[]> => {
    console.log('API: Getting user sessions for:', userId);
    const response = await apiClient.get('/dashboard/sessions', {
      params: { user_id: userId, limit }
    });
    console.log('API: User sessions response:', response.data);
    return response.data;
  },

  getAllSessions: async (limit: number = 100): Promise<Array<TestSession & {
    username: string;
    email: string;
    full_name?: string;
  }>> => {
    console.log('API: Getting all sessions');
    const response = await apiClient.get('/admin/all-sessions', {
      params: { limit }
    });
    console.log('API: All sessions response:', response.data);
    return response.data;
  },

  getUserProgress: async (userId: string): Promise<{
    user_id: string;
    overall_progress: {
      completed_questions: number;
      total_questions: number;
      progress_percentage: number;
    };
    test_progress: {
      [key: string]: {
        completed_questions: number;
        total_questions: number;
        progress_percentage: number;
        is_completed: boolean;
        last_activity: string;
      };
    };
  }> => {
    const response = await apiClient.get(`/dashboard/progress/${userId}`);
    return response.data;
  },

  getAllUsersProgress: async (): Promise<{
    users: Array<{
      id: string;
      username: string;
      email: string;
      full_name?: string;
      role: string;
      created_at: string;
      progress: {
        overall_progress: {
          completed_questions: number;
          total_questions: number;
          progress_percentage: number;
        };
        test_progress: {
          [key: string]: {
            completed_questions: number;
            total_questions: number;
            progress_percentage: number;
            is_completed: boolean;
            last_activity: string;
          };
        };
      };
    }>;
    total_users: number;
  }> => {
    const response = await apiClient.get('/admin/all-users-progress');
    return response.data;
  },

  getSessionDetails: async (sessionId: string): Promise<{
    session: TestSession;
    responses: TestResponse[];
  }> => {
    const response = await apiClient.get(`/dashboard/session/${sessionId}`);
    return response.data;
  },

  getSessionGroupedScores: async (sessionId: string): Promise<{
    grouped_scores: Array<{
      question_group: number;
      question_category: string;
      question_count: number;
      avg_ai_score: number;
      avg_expert_score?: number; // 전문가 점수가 없을 수도 있으므로 optional
      total_ai_score: number;
      total_expert_score?: number; // 전문가 점수가 없을 수도 있으므로 optional
    }>;
    overall_stats: {
      total_questions: number;
      overall_avg_ai_score: number;
      overall_avg_expert_score?: number; // 전문가 점수가 없을 수도 있으므로 optional
      overall_total_ai_score: number;
      overall_total_expert_score?: number; // 전문가 점수가 없을 수도 있으므로 optional
    };
  }> => {
    const response = await apiClient.get(`/dashboard/session/${sessionId}/grouped-scores`);
    return response.data;
  },

  getExpertFeedback: async (responseId: string): Promise<{ feedback: ExpertFeedback[] }> => {
    const response = await apiClient.get(`/expert/feedback/${responseId}`);
    return response.data;
  },

  updateExpertScore: async (responseId: string, score: number): Promise<{ message: string }> => {
    console.log(`API: Updating expert score for response ${responseId} with score: ${score}`);
    const response = await apiClient.put(`/expert/score/${responseId}`, { score });
    console.log('API: Expert score update response:', response.data);
    return response.data;
  }
};
