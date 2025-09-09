import React from 'react';
import DashboardStats from './DashboardStats';
import UserProgress from './UserProgress';
// import AdminUserProgress from './AdminUserProgress'; // AdminUserProgress 임포트 제거
import SessionList from './SessionList'; // SessionList 추가

interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  created_at: string;
}

interface HomePageProps {
  user: User;
  onNavigate: (view: string) => void;
  onViewDetailedReport?: (sessionId: string) => void;
  onViewUserStats: (user: User) => void; // 추가: 특정 사용자의 통계를 보기 위한 prop
}

const HomePage: React.FC<HomePageProps> = ({ user, onNavigate, onViewDetailedReport, onViewUserStats }) => {
  return (
    <div className="p-6">
      <div className="mb-8">
        <div className="bg-gray-50 rounded-xl p-6 text-gray-900 shadow-md border border-gray-200">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mr-4">
              <span className="text-2xl">👋</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Home</h1>
              <p className="text-gray-700 text-lg">
                {user.full_name || user.username}님! AI Helper Admin 대시보드 입니다.
              </p>
            </div>
          </div>
          <div className="flex items-center text-gray-600">
            <span className="text-sm mr-2">🕒</span>
            <span className="text-sm">
              {new Date().toLocaleDateString('ko-KR', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                weekday: 'long'
              })}
            </span>
          </div>
        </div>
      </div>


      {/* 관리자용 빠른 액션 카드 */}
      {user.role === 'admin' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                <span className="text-2xl">🤖</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">AI 모델 관리</h3>
                <p className="text-sm text-gray-600">AI 모델 설정 및 관리</p>
              </div>
            </div>
            <button
              onClick={() => onNavigate('ai-management')}
              className="btn-unified btn-unified-primary btn-unified-md btn-full"
            >
              관리하기
            </button>
          </div>
        </div>
      )}

      {/* 관리자용 전체 사용자 진행률 - DashboardStats 내부로 이동 */}
      {/* {user.role === 'admin' && (
        <div className="my-12">
          <AdminUserProgress currentUser={user} onViewUserStats={onViewUserStats} />
        </div>
      )} */}

      {/* 사용자별 진행률 - 관리자가 아닌 경우에만 */}
      {user.role !== 'admin' && (
        <div className="mb-8">
          <UserProgress user={user} />
        </div>
      )}

      {/* 대시보드 통계 */}
      <div className="mb-8">
        <DashboardStats user={user} onViewDetailedReport={onViewDetailedReport} onViewUserStats={onViewUserStats} />
      </div>

      {/* 세션 목록 */}
      <div className="mb-8">
        <SessionList user={user} onViewDetailedReport={onViewDetailedReport} />
      </div>
    </div>
  );
};

export default HomePage;