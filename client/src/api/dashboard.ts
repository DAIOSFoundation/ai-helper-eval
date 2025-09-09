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
    const response = await apiClient.get('/dashboard/sessions', {
      params: { user_id: userId, limit }
    });
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

  getExpertFeedback: async (responseId: string): Promise<{ feedback: ExpertFeedback[] }> => {
    const response = await apiClient.get(`/expert/feedback/${responseId}`);
    return response.data;
  },

  submitExpertFeedback: async (feedbackData: {
    response_id: string;
    expert_id: string;
    feedback_score: number;
    feedback_comment?: string;
    keywords_suggested?: string;
  }): Promise<{ feedback_id: string; message: string }> => {
    const response = await apiClient.post('/expert/feedback', feedbackData);
    return response.data;
  }
};
