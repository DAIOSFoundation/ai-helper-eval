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

interface UserWithProgress extends User {
  progress: {
    overall_progress: {
      completed_questions: number;
      total_questions: number;
      progress_percentage: number;
    };
    test_progress: {
      [key: string]: TestProgress;
    };
  };
}

interface AdminUserProgressProps {
  currentUser: User;
}

const AdminUserProgress: React.FC<AdminUserProgressProps> = ({ currentUser }) => {
  const [users, setUsers] = useState<UserWithProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (currentUser.role === 'admin') {
      loadAllUsersProgress();
    }
  }, [currentUser.role]);

  const loadAllUsersProgress = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.getAllUsersProgress();
      setUsers(response.users);
    } catch (err: any) {
      setError(err.response?.data?.error || '사용자 진행률을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const getTestTypeLabel = (testType: string) => {
    switch (testType) {
      case 'cdi':
        return 'CDI';
      case 'rcmas':
        return 'RCMAS';
      case 'bdi':
        return 'BDI';
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

  if (currentUser.role !== 'admin') {
    return null;
  }

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
          onClick={loadAllUsersProgress}
          className="mt-2 text-sm text-red-600 hover:text-red-500"
        >
          다시 시도
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            전체 사용자 테스트 진행률
          </h3>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              총 {users.length}명의 사용자
            </span>
            <button
              onClick={loadAllUsersProgress}
              className="text-sm text-indigo-600 hover:text-indigo-500"
            >
              새로고침
            </button>
          </div>
        </div>

        {users.length === 0 ? (
          <div className="text-center py-8">
            <h3 className="text-sm font-medium text-gray-900">사용자가 없습니다</h3>
            <p className="mt-1 text-sm text-gray-500">아직 등록된 사용자가 없습니다.</p>
          </div>
        ) : (
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    사용자
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    전체 진행률
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    CDI
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    RCMAS
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    BDI
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    마지막 활동
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {user.full_name || user.username}
                        </div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            className={`h-2 rounded-full ${getProgressColor(user.progress.overall_progress.progress_percentage)}`}
                            style={{
                              width: `${Math.min(user.progress.overall_progress.progress_percentage, 100)}%`
                            }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-500">
                          {user.progress.overall_progress.progress_percentage.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user.progress.test_progress.cdi ? (
                        <div className="flex items-center">
                          <div className="w-12 bg-gray-200 rounded-full h-2 mr-2">
                            <div
                              className={`h-2 rounded-full ${getProgressColor(user.progress.test_progress.cdi.progress_percentage)}`}
                              style={{
                                width: `${Math.min(user.progress.test_progress.cdi.progress_percentage, 100)}%`
                              }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-500">
                            {user.progress.test_progress.cdi.progress_percentage.toFixed(0)}%
                          </span>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user.progress.test_progress.rcmas ? (
                        <div className="flex items-center">
                          <div className="w-12 bg-gray-200 rounded-full h-2 mr-2">
                            <div
                              className={`h-2 rounded-full ${getProgressColor(user.progress.test_progress.rcmas.progress_percentage)}`}
                              style={{
                                width: `${Math.min(user.progress.test_progress.rcmas.progress_percentage, 100)}%`
                              }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-500">
                            {user.progress.test_progress.rcmas.progress_percentage.toFixed(0)}%
                          </span>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user.progress.test_progress.bdi ? (
                        <div className="flex items-center">
                          <div className="w-12 bg-gray-200 rounded-full h-2 mr-2">
                            <div
                              className={`h-2 rounded-full ${getProgressColor(user.progress.test_progress.bdi.progress_percentage)}`}
                              style={{
                                width: `${Math.min(user.progress.test_progress.bdi.progress_percentage, 100)}%`
                              }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-500">
                            {user.progress.test_progress.bdi.progress_percentage.toFixed(0)}%
                          </span>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.progress.overall_progress.total_questions > 0 ? (
                        Object.values(user.progress.test_progress)
                          .map(t => t.last_activity)
                          .filter(Boolean)
                          .sort()
                          .pop() ? 
                        new Date(
                          Object.values(user.progress.test_progress)
                            .map(t => t.last_activity)
                            .filter(Boolean)
                            .sort()
                            .pop()!
                        ).toLocaleDateString('ko-KR') : '-'
                      ) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* 요약 통계 */}
        {users.length > 0 && (
          <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-blue-600">
                {users.length}
              </div>
              <div className="text-sm text-blue-800">총 사용자</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-green-600">
                {users.filter(u => u.progress.overall_progress.progress_percentage > 0).length}
              </div>
              <div className="text-sm text-green-800">테스트 시작한 사용자</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-purple-600">
                {users.filter(u => u.progress.overall_progress.progress_percentage >= 100).length}
              </div>
              <div className="text-sm text-purple-800">완료한 사용자</div>
            </div>
            <div className="bg-orange-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-orange-600">
                {users.length > 0 ? 
                  (users.reduce((sum, u) => sum + u.progress.overall_progress.progress_percentage, 0) / users.length).toFixed(1) : 0}%
              </div>
              <div className="text-sm text-orange-800">평균 진행률</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminUserProgress;
