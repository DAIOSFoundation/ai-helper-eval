import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../../api/dashboard';
import AdminUserProgress from './AdminUserProgress'; // AdminUserProgress 임포트

// 타입 정의를 인라인으로 이동
interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  created_at: string;
}

interface OverallProgressSummary {
  total_users_count: number;
  started_test_users_count: number;
  completed_test_users_count: number;
  avg_overall_progress_percentage: number;
}

// OverallProgressSummary 인터페이스는 src/types/dashboard.ts로 이동되었으므로 여기서는 삭제합니다.
// interface OverallProgressSummary {
//   total_users_count: number;
//   started_test_users_count: number;
//   completed_test_users_count: number;
//   avg_overall_progress_percentage: number;
// }

interface DashboardStatsType {
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
  recent_sessions: Array<{ // 이 데이터는 더 이상 렌더링되지 않지만, API 응답 타입에 포함될 수 있으므로 유지
    id: string;
    user_id: string;
    test_type: string;
    status: string;
    total_questions: number;
    completed_questions: number;
    total_score: number;
    started_at: string;
    completed_at?: string;
    username: string;
    full_name?: string;
    session_round: number;
  }>;
  overall_progress_summary?: OverallProgressSummary; // 추가: 전체 사용자 진행률 요약
}

// User 인터페이스는 src/types/dashboard.ts로 이동
// interface User {
//   id: string;
//   username: string;
//   email: string;
//   full_name?: string;
//   role: string;
//   created_at: string;
// }

interface DashboardStatsProps {
  user: User;
  onViewDetailedReport?: (sessionId: string) => void;
  onViewUserStats: (user: User) => void; // AdminUserProgress로 전달하기 위한 prop 추가
}

const DashboardStats: React.FC<DashboardStatsProps> = ({ user, onViewDetailedReport, onViewUserStats }) => {
  const [stats, setStats] = useState<DashboardStatsType>({
    overall_stats: {
      total_sessions: 0,
      total_users: 0,
      avg_score: 0,
      total_responses: 0
    },
    test_type_stats: [],
    recent_sessions: [], // 이 데이터는 더 이상 렌더링되지 않음
    overall_progress_summary: undefined, // 초기값 설정
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStats();
  }, [user]);

  const loadStats = async () => {
    try {
      setLoading(true);
      
      // 관리자나 전문가는 모든 사용자의 통계를, 일반 사용자는 자신의 통계만 조회
      const statsData = await dashboardAPI.getStats();
      
      let overallProgressSummary: OverallProgressSummary | undefined;

      if (user.role === 'admin') {
        // 관리자인 경우에만 모든 사용자 진행률 요약 정보를 가져옴
        const allUsersProgressResponse = await dashboardAPI.getAllUsersProgress();
        const usersWithProgress = allUsersProgressResponse.users;

        const totalUsersCount = usersWithProgress.length;
        const startedTestUsersCount = usersWithProgress.filter(u => u.progress.overall_progress.progress_percentage > 0).length;
        const completedTestUsersCount = usersWithProgress.filter(u => u.progress.overall_progress.progress_percentage >= 100).length;
        const avgOverallProgressPercentage = totalUsersCount > 0 ? 
          (usersWithProgress.reduce((sum, u) => sum + u.progress.overall_progress.progress_percentage, 0) / totalUsersCount) : 0;

        overallProgressSummary = {
          total_users_count: totalUsersCount,
          started_test_users_count: startedTestUsersCount,
          completed_test_users_count: completedTestUsersCount,
          avg_overall_progress_percentage: avgOverallProgressPercentage,
        };
      }

      setStats({
        ...statsData,
        overall_progress_summary: overallProgressSummary,
      });
    } catch (err: any) {
      console.error('Error loading dashboard stats:', err);
      setError(err.response?.data?.error || '통계를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4 shadow-sm">
        <div className="text-red-800">{error}</div>
        <button
          onClick={loadStats}
          className="btn-unified btn-unified-secondary btn-unified-sm mt-2"
        >
          다시 시도
        </button>
      </div>
    );
  }

  const { overall_stats, test_type_stats, overall_progress_summary } = stats; // recent_sessions는 더 이상 구조 분해하지 않음

  return (
    <div className="space-y-6">
      {/* 전체 통계 카드 - 수평 밀도 배치 */}
      <div className="bg-white overflow-hidden shadow-md rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h3 className="section-title flex items-center">
            <span className="text-2xl mr-3">📊</span>
            전체 통계
          </h3>
        </div>
        <div className="p-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {/* 기존 전체 통계 카드 4개 */}
            {/* 총 사용자 */}
            <div className="flex items-center space-x-3 p-3 bg-indigo-50 rounded-lg border border-indigo-200 shadow-sm">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-indigo-500 rounded-md flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-indigo-600 truncate">총 사용자</p>
                <p className="text-lg font-bold text-indigo-900">{overall_stats.total_users}</p>
              </div>
            </div>

            {/* 총 세션 */}
            <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg border border-green-200 shadow-sm">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-green-600 truncate">총 세션</p>
                <p className="text-lg font-bold text-green-900">{overall_stats.total_sessions}</p>
              </div>
            </div>

            {/* 평균 점수 */}
            <div className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200 shadow-sm">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-yellow-600 truncate">평균 점수</p>
                <p className="text-lg font-bold text-yellow-900">
                  {overall_stats.avg_score ? overall_stats.avg_score.toFixed(1) : '0.0'}
                </p>
              </div>
            </div>

            {/* 총 응답 */}
            <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg border border-purple-200 shadow-sm">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-purple-600 truncate">총 응답</p>
                <p className="text-lg font-bold text-purple-900">{overall_stats.total_responses}</p>
              </div>
            </div>

            {/* 이동된 전체 사용자 진행률 요약 카드 4개 (관리자에게만 표시) */}
            {user.role === 'admin' && overall_progress_summary && (
              <>
                {/* 총 사용자 (AdminUserProgress에서 이동) */}
                <div className="flex items-center space-x-3 p-3 bg-indigo-50 rounded-lg border border-indigo-200 shadow-sm">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-indigo-500 rounded-md flex items-center justify-center">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
                    </div>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium text-indigo-600 truncate">총 사용자 (진행률)</p>
                    <p className="text-lg font-bold text-indigo-900">
                      {overall_progress_summary.total_users_count}
                    </p>
                  </div>
                </div>

                {/* 테스트 시작한 사용자 */}
                <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg border border-green-200 shadow-sm">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                    </div>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium text-green-600 truncate">테스트 시작 사용자</p>
                    <p className="text-lg font-bold text-green-900">
                      {overall_progress_summary.started_test_users_count}
                    </p>
                  </div>
                </div>

                {/* 완료한 사용자 */}
                <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg border border-purple-200 shadow-sm">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </div>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium text-purple-600 truncate">완료한 사용자</p>
                    <p className="text-lg font-bold text-purple-900">
                      {overall_progress_summary.completed_test_users_count}
                    </p>
                  </div>
                </div>

                {/* 평균 진행률 */}
                <div className="flex items-center space-x-3 p-3 bg-orange-50 rounded-lg border border-orange-200 shadow-sm">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-orange-500 rounded-md flex items-center justify-center">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.001 0 0120.488 9z"></path></svg>
                    </div>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium text-orange-600 truncate">평균 진행률</p>
                    <p className="text-lg font-bold text-orange-900">
                      {overall_progress_summary.avg_overall_progress_percentage.toFixed(1)}%
                    </p>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* 관리자용 전체 사용자 진행률 섹션 */}
      {user.role === 'admin' && (
        <AdminUserProgress 
          currentUser={user} 
          onViewUserStats={onViewUserStats} 
          overallProgressSummary={overall_progress_summary} // 추가: overall_progress_summary prop 전달
        />
      )}

      {/* 테스트 타입별 통계 */}
      <div className="bg-white shadow-md rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h3 className="section-title flex items-center">
            <span className="text-2xl mr-3">📈</span>
            테스트 타입별 통계
          </h3>
        </div>
        <div className="px-6 py-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {test_type_stats.map((stat, index) => {
              const getTestTypeInfo = (testType: string) => {
                switch (testType.toLowerCase()) {
                  case 'cdi':
                    return { name: 'CDI', fullName: '아동 우울 척도', color: 'blue', icon: '😔' };
                  case 'rcmas':
                    return { name: 'RCMAS', fullName: '아동 불안 척도', color: 'yellow', icon: '😰' };
                  case 'bdi':
                    return { name: 'BDI', fullName: '벡 우울 척도', color: 'purple', icon: '😞' };
                  default:
                    return { name: testType.toUpperCase(), fullName: testType, color: 'gray', icon: '📋' };
                }
              };

              const testInfo = getTestTypeInfo(stat.test_type);
              const completionRate = stat.session_count > 0 ? (stat.completed_count / stat.session_count) * 100 : 0;

              return (
                <div key={stat.test_type} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                  {/* 헤더 */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center mr-3 ${
                        testInfo.color === 'blue' ? 'bg-indigo-100' :
                        testInfo.color === 'yellow' ? 'bg-yellow-100' :
                        testInfo.color === 'purple' ? 'bg-purple-100' :
                        'bg-gray-100'
                      }`}>
                        <span className="text-2xl">{testInfo.icon}</span>
                      </div>
                      <div>
                        <h4 className="text-lg font-semibold text-gray-900">{testInfo.name}</h4>
                        <p className="text-sm text-gray-600">{testInfo.fullName}</p>
                      </div>
                    </div>
                  </div>

                  {/* 통계 정보 */}
                  <div className="space-y-3">
                    {/* 세션 수 */}
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-700">총 세션</span>
                      </div>
                      <span className="text-lg font-bold text-gray-900">{stat.session_count}</span>
                    </div>

                    {/* 완료 수 */}
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-700">완료 세션</span>
                      </div>
                      <span className="text-lg font-bold text-green-600">{stat.completed_count}</span>
                    </div>

                    {/* 완료율 */}
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-gray-700">완료율</span>
                        <span className="text-sm font-bold text-gray-900">{completionRate.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${Math.min(completionRate, 100)}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* 평균 점수 */}
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-700">평균 점수</span>
                      </div>
                      <span className={`text-lg font-bold ${
                        stat.avg_score >= 80 ? 'text-green-600' :
                        stat.avg_score >= 60 ? 'text-yellow-600' :
                        stat.avg_score >= 40 ? 'text-orange-600' :
                        'text-red-600'
                      }`}>
                        {stat.avg_score ? stat.avg_score.toFixed(1) : '0.0'}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardStats;