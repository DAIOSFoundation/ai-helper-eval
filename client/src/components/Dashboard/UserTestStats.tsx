import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../../api/dashboard';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { getTestTypeLabel } from '../../utils/helpers'; // 유틸리티 함수 임포트

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

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
  test_type: string;
  status: string;
  total_score: number;
  completed_questions: number;
  total_questions: number;
  started_at: string;
  completed_at?: string;
  session_round: number;
}

interface UserTestStatsProps {
  user: User;
  onBack: () => void;
}

const UserTestStats: React.FC<UserTestStatsProps> = ({ user, onBack }) => {
  const [sessions, setSessions] = useState<TestSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadUserSessions();
  }, [user.id]);

  const loadUserSessions = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.getUserSessions(user.id);
      setSessions(response);
    } catch (err: any) {
      console.error('Error loading user sessions:', err);
      setError('세션 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 기존 getTestTypeLabel 함수 제거 (유틸리티 사용)
  // const getTestTypeLabel = (testType: string) => {
  //   switch (testType.toLowerCase()) {
  //     case 'cdi': return 'CDI (아동 우울 척도)';
  //     case 'rcmas': return 'RCMAS (아동 불안 척도)';
  //     case 'bdi': return 'BDI (벡 우울 척도)';
  //     default: return testType.toUpperCase();
  //   }
  // };

  const getScoreColor = (score: number) => {
    if (score >= 4.0) return 'text-green-600';
    if (score >= 3.0) return 'text-lime-600';
    if (score >= 2.0) return 'text-yellow-600';
    if (score >= 1.0) return 'text-orange-600';
    return 'text-red-600';
  };

  // 테스트 타입별로 그룹화
  const groupedSessions = sessions.reduce((acc, session) => {
    if (!acc[session.test_type]) {
      acc[session.test_type] = [];
    }
    acc[session.test_type].push(session);
    return acc;
  }, {} as { [key: string]: TestSession[] });

  // 각 테스트 타입별로 회차순으로 정렬
  Object.keys(groupedSessions).forEach(testType => {
    groupedSessions[testType].sort((a, b) => a.session_round - b.session_round);
  });

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">로딩 중...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={onBack}
              className="btn-unified btn-unified-primary btn-unified-sm"
            >
              돌아가기
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="btn-unified btn-unified-ghost btn-unified-sm"
          >
            ← 돌아가기
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            {user.full_name || user.username}님의 테스트 통계
          </h1>
        </div>
      </div>

      {/* 메인 컨텐츠 */}
      <div>
          
          {/* 전체 통계 요약 */}
          <div className="bg-white rounded-xl p-6 mb-6 shadow-md border border-gray-200">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">📊 전체 통계 요약</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center p-3 bg-indigo-50 rounded-lg border border-indigo-200">
                <div className="text-3xl font-bold text-indigo-600">{sessions.length}</div>
                <div className="text-sm text-gray-600">총 세션 수</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg border border-green-200">
                <div className="text-3xl font-bold text-green-600">
                  {Object.keys(groupedSessions).length}
                </div>
                <div className="text-sm text-gray-600">완료된 테스트 타입</div>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg border border-purple-200">
                <div className="text-3xl font-bold text-purple-600">
                  {sessions.length > 0 ? (sessions.reduce((sum, s) => sum + s.total_score, 0) / sessions.length).toFixed(1) : '0.0'}
                </div>
                <div className="text-sm text-gray-600">평균 점수</div>
              </div>
              <div className="text-center p-3 bg-orange-50 rounded-lg border border-orange-200">
                <div className="text-3xl font-bold text-orange-600">
                  {Math.max(...Object.values(groupedSessions).map(sessions => sessions.length), 0)}
                </div>
                <div className="text-sm text-gray-600">최대 회차</div>
              </div>
            </div>
          </div>

          {/* 테스트 타입별 상세 통계 */}
          {Object.entries(groupedSessions).map(([testType, testSessions]) => (
            <div key={testType} className="bg-white rounded-xl p-6 mb-6 shadow-md border border-gray-200">
              <h3 className="text-xl font-bold mb-4 text-gray-800">
                📈 {getTestTypeLabel(testType)} - 회차별 분석
              </h3>
              
              {/* 회차별 점수 변화 그래프 */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold mb-4 text-gray-700">점수 변화 추이</h4>
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <div className="h-80">
                    <Line
                      data={{
                        labels: testSessions.map(session => 
                          `${session.session_round}회차\n${new Date(session.completed_at || session.started_at).toLocaleDateString('ko-KR', {
                            month: 'short',
                            day: 'numeric'
                          })}`
                        ),
                        datasets: [
                          {
                            label: '점수',
                            data: testSessions.map(session => session.total_score),
                            borderColor: '#4f46e5', // indigo-600
                            backgroundColor: 'rgba(79, 70, 229, 0.1)', // indigo-600 with 0.1 opacity
                            borderWidth: 3,
                            pointBackgroundColor: '#4f46e5', // indigo-600
                            pointBorderColor: '#ffffff',
                            pointBorderWidth: 2,
                            pointRadius: 6,
                            pointHoverRadius: 8,
                            fill: false,
                            tension: 0.2, // 곡선 완화
                          }
                        ]
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: false
                          },
                          tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#4f46e5', // indigo-600
                            borderWidth: 1,
                            callbacks: {
                              title: function(context) {
                                return context[0].label.replace('\n', ' - ');
                              },
                              label: function(context) {
                                return `점수: ${context.parsed.y.toFixed(1)}`;
                              }
                            }
                          }
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                            max: Math.max(5, Math.ceil(Math.max(...testSessions.map(s => s.total_score)) * 1.1)),
                            min: 0,
                            ticks: {
                              stepSize: 1,
                              color: '#6B7280',
                              font: {
                                size: 12
                              }
                            },
                            grid: {
                              color: '#E5E7EB',
                              lineWidth: 1
                            },
                            border: {
                              color: '#D1D5DB'
                            }
                          },
                          x: {
                            ticks: {
                              color: '#6B7280',
                              font: {
                                size: 11
                              },
                              maxRotation: 0
                            },
                            grid: {
                              display: false
                            },
                            border: {
                              color: '#D1D5DB'
                            }
                          }
                        },
                        interaction: {
                          intersect: false,
                          mode: 'index'
                        },
                        elements: {
                          point: {
                            hoverBackgroundColor: '#3730a3' // indigo-800
                          }
                        }
                      }}
                    />
                  </div>
                  
                  {/* 범례 */}
                  <div className="mt-4 text-center">
                    <div className="inline-flex items-center text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded-lg border border-gray-200">
                      <span className="inline-block w-3 h-3 bg-indigo-600 rounded-full mr-2"></span>
                      점수 범위: 0.0 ~ {Math.max(5, Math.ceil(Math.max(...testSessions.map(s => s.total_score)) * 1.1))}.0
                    </div>
                  </div>
                </div>
              </div>

              {/* 회차별 상세 정보 */}
              <div className="space-y-3">
                <h4 className="text-lg font-semibold text-gray-700">회차별 상세 정보</h4>
                {testSessions.map((session) => (
                  <div key={session.id} className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-4">
                        <div className="text-center">
                          <div className="text-lg font-bold text-indigo-600">{session.session_round}회차</div>
                          <div className="text-xs text-gray-500">회차</div>
                        </div>
                        <div className="text-center">
                          <div className={`text-2xl font-bold ${getScoreColor(session.total_score)}`}>
                            {session.total_score.toFixed(1)}
                          </div>
                          <div className="text-xs text-gray-500">점수</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-bold text-green-600">
                            {session.completed_questions}/{session.total_questions}
                          </div>
                          <div className="text-xs text-gray-500">완료율</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-600">
                          시작: {new Date(session.started_at).toLocaleString('ko-KR')}
                        </div>
                        {session.completed_at && (
                          <div className="text-sm text-gray-600">
                            완료: {new Date(session.completed_at).toLocaleString('ko-KR')}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* 테스트가 없는 경우 */}
          {sessions.length === 0 && (
            <div className="bg-white rounded-xl p-8 text-center shadow-md border border-gray-200">
              <div className="text-6xl mb-4 text-indigo-400">📊</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">아직 완료된 테스트가 없습니다</h3>
              <p className="text-gray-600 mb-4">
                AI 상담사와 대화를 시작하여 진단 테스트를 완료해보세요.
              </p>
              <button
                onClick={onBack}
                className="btn-unified btn-unified-primary btn-unified-lg"
              >
                대화 시작하기
              </button>
            </div>
          )}
      </div>
    </div>
  );
};

export default UserTestStats;