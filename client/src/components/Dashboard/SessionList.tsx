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

interface TestSession {
  id: string;
  user_id: string;
  test_type: string;
  status: string;
  total_questions: number;
  completed_questions: number;
  total_score: number;
  started_at: string;
  completed_at?: string;
  username?: string;
  email?: string;
  full_name?: string;
}
import DetailedReport from '../Reporting/DetailedReport';

interface SessionListProps {
  user: User;
  onViewDetailedReport?: (sessionId: string) => void; // App.tsx에서 전달받기 위함
}

const SessionList: React.FC<SessionListProps> = ({ user, onViewDetailedReport }) => {
  const [sessions, setSessions] = useState<TestSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  // const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null); // App.tsx에서 관리

  useEffect(() => {
    loadSessions();
  }, [user.id]);

  const loadSessions = async () => {
    try {
      setLoading(true);
      console.log('Loading sessions for user:', user.id, 'role:', user.role);
      
      let sessions;
      if (user.role === 'admin' || user.role === 'expert') {
        // 관리자와 전문가는 모든 사용자의 세션을 볼 수 있음
        sessions = await dashboardAPI.getAllSessions();
        console.log('All sessions loaded:', sessions);
      } else {
        // 일반 사용자는 자신의 세션만 볼 수 있음
        sessions = await dashboardAPI.getUserSessions(user.id);
        console.log('User sessions loaded:', sessions);
      }
      
      setSessions(sessions);
    } catch (err: any) {
      console.error('Error loading sessions:', err);
      setError(err.response?.data?.error || '세션 목록을 불러오는데 실패했습니다.');
      setSessions([]); // 오류 시 빈 배열로 설정
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">완료</span>;
      case 'in_progress':
        return <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">진행중</span>;
      default:
        return <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">{status}</span>;
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
          onClick={loadSessions}
          className="btn-unified btn-unified-secondary btn-unified-sm mt-2"
        >
          다시 시도
        </button>
      </div>
    );
  }

  const tableHeaders = [
    (user.role === 'admin' || user.role === 'expert') && { label: '사용자', key: 'user' },
    { label: '테스트 타입', key: 'test_type' },
    { label: '진행률', key: 'progress' },
    { label: '상태', key: 'status' },
    { label: '점수', key: 'score' },
    { label: '시작 시간', key: 'started_at' },
    { label: '완료 시간', key: 'completed_at' },
    { label: '상세 리포트', key: 'detailed_report' }
  ].filter(Boolean); // null 또는 false 값을 제거합니다.

  return (
    <div className="bg-white shadow-md rounded-lg border border-gray-200">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            {user.role === 'admin' || user.role === 'expert' ? '모든 사용자 테스트 세션' : '내 테스트 세션'}
          </h3>
          <button
            onClick={loadSessions}
            className="btn-unified btn-unified-ghost btn-unified-sm"
          >
            새로고침
          </button>
        </div>

        {sessions.length === 0 ? (
          <div className="text-center py-8">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">테스트 세션이 없습니다</h3>
            <p className="mt-1 text-sm text-gray-500">새로운 테스트를 시작해보세요.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full w-full divide-y divide-gray-200"> {/* w-full 클래스 추가 */}
              <thead className="bg-gray-50">
                <tr>
                  {tableHeaders.map(header => (
                    <th key={header.key} className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                      {header.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sessions.map((session) => (
                  <tr key={session.id} className="hover:bg-gray-50">
                    {(user.role === 'admin' || user.role === 'expert') && (
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div>
                          <div className="font-medium">{session.full_name || session.username || 'Unknown'}</div>
                          <div className="text-gray-500">{session.email}</div>
                        </div>
                      </td>
                    )}
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {getTestTypeLabel(session.test_type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            className="bg-indigo-600 h-2 rounded-full"
                            style={{
                              width: `${(session.completed_questions / session.total_questions) * 100}%`
                            }}
                          ></div>
                        </div>
                        <span className="text-xs">
                          {session.completed_questions}/{session.total_questions}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(session.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {session.total_score ? session.total_score.toFixed(1) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(session.started_at).toLocaleString('ko-KR')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {session.completed_at 
                        ? new Date(session.completed_at).toLocaleString('ko-KR')
                        : '-'
                      }
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button
                        onClick={() => onViewDetailedReport?.(session.id)}
                        className="btn-unified btn-unified-outline btn-unified-sm"
                      >
                        상세 보기
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 상세 리포트 모달 (App.tsx에서 렌더링하도록 변경) */}
      {/* {selectedSessionId && (
        <DetailedReport
          user={user}
          sessionId={selectedSessionId}
          onClose={() => setSelectedSessionId(null)}
        />
      )} */}
    </div>
  );
};

export default SessionList;