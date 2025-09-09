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
  onViewUserStats: (user: User) => void; // 추가: 특정 사용자의 통계를 보기 위한 콜백
}

const AdminUserProgress: React.FC<AdminUserProgressProps> = ({ currentUser, onViewUserStats }) => {
  const [users, setUsers] = useState<UserWithProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // 이 컴포넌트는 이제 DashboardStats 내부에 있으므로,
    // DashboardStats에서 이미 currentUser.role === 'admin'을 확인하고 렌더링 여부를 결정합니다.
    loadAllUsersProgress();
  }, [currentUser.id]); // currentUser.id 변경 시 다시 로드

  const loadAllUsersProgress = async () => {
    try {
      setLoading(true);
      console.log('Loading all users progress...');
      const response = await dashboardAPI.getAllUsersProgress();
      console.log('All users progress response:', response);
      console.log('Users count:', response.users?.length || 0);
      setUsers(response.users || []);
    } catch (err: any) {
      console.error('Error loading all users progress:', err);
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

  const getProgressColorClass = (percentage: number) => {
    if (percentage >= 100) return 'bg-green-500';
    if (percentage >= 75) return 'bg-indigo-500'; // blue-500 -> indigo-500
    if (percentage >= 50) return 'bg-yellow-500';
    if (percentage >= 25) return 'bg-orange-500';
    return 'bg-red-500';
  };

  // 이 컴포넌트는 이제 DashboardStats 내부에서만 렌더링되므로,
  // 여기서 currentUser.role 검사를 할 필요가 없습니다.
  // if (currentUser.role !== 'admin') {
  //   return null;
  // }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">사용자 진행률을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4 shadow-sm">
        <div className="text-red-800">{error}</div>
        <button
          onClick={loadAllUsersProgress}
          className="btn-unified btn-unified-ghost btn-unified-sm mt-2 text-red-600"
        >
          다시 시도
        </button>
      </div>
    );
  }

  const tableHeaders = [
    { key: 'user', label: '사용자' },
    { key: 'overall_progress', label: '전체 진행률' },
    { key: 'cdi', label: 'CDI' },
    { key: 'rcmas', label: 'RCMAS' },
    { key: 'bdi', label: 'BDI' },
    { key: 'last_activity', label: '마지막 활동' },
    { key: 'action', label: '액션' },
  ];

  return (
    // mt-6 클래스 제거: DashboardStats 내부에서 렌더링되므로 불필요
    <div className="bg-white shadow-md rounded-lg border border-gray-200">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex justify-between items-center mb-4"> {/* mb-6 -> mb-4로 변경 */}
          {/* 제목 스타일 수정: 아이콘 포함 및 텍스트 크기 조정 */}
          <h3 className="section-title flex items-center">
            <span className="text-2xl mr-3">👥</span> {/* 아이콘 */}
            <span className="text-xl font-bold text-gray-900">전체 사용자 테스트 진행률</span> {/* 텍스트 스타일 조정 */}
          </h3>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              총 {users.length}명의 사용자
            </span>
            <button
              onClick={loadAllUsersProgress}
              className="btn-unified btn-unified-ghost btn-unified-sm"
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
          <div className="overflow-x-auto"> {/* custom-scrollbar 클래스 제거 */}
            <table className="min-w-full w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {tableHeaders.map(header => (
                    <th key={header.key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {header.label}
                    </th>
                  ))}
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
                            className={`h-2 rounded-full ${getProgressColorClass(user.progress.overall_progress.progress_percentage)}`}
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
                              className={`h-2 rounded-full ${getProgressColorClass(user.progress.test_progress.cdi.progress_percentage)}`}
                              style={{
                                width: `${Math.min(user.progress.test_progress.cdi.progress_percentage, 100)}%`
                              }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-500">
                            {user.progress.test_progress.cdi.progress_percentage.toFixed(1)}% {/* toFixed(1)로 변경 */}
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
                              className={`h-2 rounded-full ${getProgressColorClass(user.progress.test_progress.rcmas.progress_percentage)}`}
                              style={{
                                width: `${Math.min(user.progress.test_progress.rcmas.progress_percentage, 100)}%`
                              }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-500">
                            {user.progress.test_progress.rcmas.progress_percentage.toFixed(1)}% {/* toFixed(1)로 변경 */}
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
                              className={`h-2 rounded-full ${getProgressColorClass(user.progress.test_progress.bdi.progress_percentage)}`}
                              style={{
                                width: `${Math.min(user.progress.test_progress.bdi.progress_percentage, 100)}%`
                              }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-500">
                            {user.progress.test_progress.bdi.progress_percentage.toFixed(1)}% {/* toFixed(1)로 변경 */}
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
                    {/* 액션 버튼 추가 */}
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button
                        onClick={() => onViewUserStats(user)} // 클릭 시 해당 사용자 정보를 전달
                        className="btn-unified btn-unified-outline btn-unified-sm"
                      >
                        상세 통계 보기
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* 요약 통계 제거됨 - DashboardStats로 이동 */}
      </div>
    </div>
  );
};

export default AdminUserProgress;