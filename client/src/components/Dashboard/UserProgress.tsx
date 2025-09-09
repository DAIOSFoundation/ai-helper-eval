import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../../api/dashboard';

interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  created_at: string;
}

interface TestProgress {
  completed_questions: number;
  total_questions: number;
  progress_percentage: number;
  is_completed: boolean;
  last_activity: string;
}

interface UserProgressData {
  user_id: string;
  overall_progress: {
    completed_questions: number;
    total_questions: number;
    progress_percentage: number;
  };
  test_progress: {
    [key: string]: TestProgress;
  };
}

interface UserProgressProps {
  user: User;
}

const UserProgress: React.FC<UserProgressProps> = ({ user }) => {
  const [progressData, setProgressData] = useState<UserProgressData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProgress();
  }, [user.id]);

  const loadProgress = async () => {
    try {
      setLoading(true);
      const progress = await dashboardAPI.getUserProgress(user.id);
      setProgressData(progress);
    } catch (err: any) {
      setError(err.response?.data?.error || '진행률을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const getTestTypeLabel = (testType: string) => {
    switch (testType) {
      case 'cdi':
        return 'CDI (아동 우울 척도)';
      case 'rcmas':
        return 'RCMAS (아동 불안 척도)';
      case 'bdi':
        return 'BDI (벡 우울 척도)';
      default:
        return testType.toUpperCase();
    }
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-green-500';
    if (percentage >= 75) return 'bg-blue-500';
    if (percentage >= 50) return 'bg-yellow-500';
    if (percentage >= 25) return 'bg-orange-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="text-red-800">{error}</div>
        <button
          onClick={loadProgress}
          className="mt-2 text-sm text-red-600 hover:text-red-500"
        >
          다시 시도
        </button>
      </div>
    );
  }

  if (!progressData) {
    return (
      <div className="text-center py-8">
        <h3 className="text-sm font-medium text-gray-900">진행률 데이터가 없습니다</h3>
        <p className="mt-1 text-sm text-gray-500">테스트를 시작해보세요.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            전체 테스트 진행률
          </h3>
          <button
            onClick={loadProgress}
            className="text-sm text-indigo-600 hover:text-indigo-500"
          >
            새로고침
          </button>
        </div>

        {/* 전체 진행률 */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">전체 진행률</span>
            <span className="text-sm text-gray-500">
              {progressData.overall_progress.completed_questions}/{progressData.overall_progress.total_questions} 
              ({progressData.overall_progress.progress_percentage.toFixed(1)}%)
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-300 ${getProgressColor(progressData.overall_progress.progress_percentage)}`}
              style={{
                width: `${Math.min(progressData.overall_progress.progress_percentage, 100)}%`
              }}
            ></div>
          </div>
        </div>

        {/* 각 테스트별 진행률 */}
        <div className="space-y-4">
          {Object.entries(progressData.test_progress).map(([testType, progress]) => (
            <div key={testType} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-900">
                    {getTestTypeLabel(testType)}
                  </span>
                  {progress.is_completed && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      완료
                    </span>
                  )}
                </div>
                <span className="text-sm text-gray-500">
                  {progress.completed_questions}/{progress.total_questions} 
                  ({progress.progress_percentage.toFixed(1)}%)
                </span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(progress.progress_percentage)}`}
                  style={{
                    width: `${Math.min(progress.progress_percentage, 100)}%`
                  }}
                ></div>
              </div>
              
              {progress.last_activity && (
                <p className="text-xs text-gray-500">
                  마지막 활동: {new Date(progress.last_activity).toLocaleString('ko-KR')}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* 진행률 요약 */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-600">
              {progressData.overall_progress.completed_questions}
            </div>
            <div className="text-sm text-blue-800">완료된 질문</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-green-600">
              {Object.values(progressData.test_progress).filter(p => p.is_completed).length}
            </div>
            <div className="text-sm text-green-800">완료된 테스트</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-purple-600">
              {progressData.overall_progress.progress_percentage.toFixed(1)}%
            </div>
            <div className="text-sm text-purple-800">전체 진행률</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProgress;
