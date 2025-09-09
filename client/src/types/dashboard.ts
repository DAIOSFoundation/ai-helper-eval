export interface OverallProgressSummary {
  total_users_count: number;
  started_test_users_count: number;
  completed_test_users_count: number;
  avg_overall_progress_percentage: number;
}

// 다른 타입들도 추가
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  created_at: string;
}

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