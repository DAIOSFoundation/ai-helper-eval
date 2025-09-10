import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { authAPI } from './api/auth';

interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  created_at: string;
}
import LoginForm from './components/Auth/LoginForm';
import RegisterForm from './components/Auth/RegisterForm';
import Sidebar from './components/Layout/Sidebar';
import HomePage from './components/Dashboard/HomePage';
import ConversationTest from './components/Conversation/ConversationTest';
import AIModelManagement from './components/Admin/AIModelManagement';
import SettingsPage from './components/Settings/SettingsPage';
import UserTestStats from './components/Dashboard/UserTestStats';
import DetailedReport from './components/Reporting/DetailedReport';
import './App.css';

const queryClient = new QueryClient();

type View = 'login' | 'register' | 'home' | 'conversation' | 'ai-management' | 'settings' | 'user-stats' | 'detailed-report';

function App() {
  const [currentView, setCurrentView] = useState<View>('login');
  const [user, setUser] = useState<User | null>(null);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [selectedUserForStats, setSelectedUserForStats] = useState<User | null>(null); // 추가: 관리자가 선택한 사용자 정보

  useEffect(() => {
    const savedUser = authAPI.getCurrentUser();
    if (savedUser) {
      setUser(savedUser);
      setCurrentView('home');
    }
  }, []);

  const handleLoginSuccess = (userData: User) => {
    setUser(userData);
    setCurrentView('home');
  };

  const handleLogout = () => {
    authAPI.logout();
    setUser(null);
    setCurrentView('login');
  };

  const handleRegisterSuccess = () => {
    setCurrentView('login');
  };

  const handleNavigate = (view: string) => {
    // AI 관리 페이지는 관리자만 접근 가능
    if (view === 'ai-management' && user?.role !== 'admin') {
      console.warn('AI 관리 페이지는 관리자만 접근할 수 있습니다.');
      return;
    }
    
    // '내 통계'로 이동할 경우, 다른 사용자를 보고 있던 상태를 초기화
    if (view === 'user-stats') {
      setSelectedUserForStats(null);
    }
    setCurrentView(view as View);
  };

  const handleViewDetailedReport = (sessionId: string) => {
    console.log('handleViewDetailedReport called with sessionId:', sessionId);
    setSelectedSessionId(sessionId);
    setCurrentView('detailed-report');
    console.log('Current view set to:', 'detailed-report');
    console.log('Selected session ID set to:', sessionId);
  };

  const handleBackFromDetailedReport = () => {
    setSelectedSessionId(null);
    setCurrentView('home');
  };

  // 추가: AdminUserProgress에서 특정 사용자 통계 보기를 요청했을 때
  const handleViewUserStats = (userToView: User) => {
    setSelectedUserForStats(userToView);
    setCurrentView('user-stats');
  };

  // 추가: UserTestStats에서 '돌아가기' 버튼을 눌렀을 때
  const handleBackFromUserStats = () => {
    setSelectedUserForStats(null); // 선택된 사용자 초기화
    setCurrentView('home');
  };

  const handleTestComplete = (result: any) => {
    // 테스트 완료 후 홈으로 돌아가기
    setTimeout(() => {
      setCurrentView('home');
    }, 3000);
  };

  const renderContent = () => {
    switch (currentView) {
      case 'login':
        return (
          <LoginForm
            onLoginSuccess={handleLoginSuccess}
            onSwitchToRegister={() => setCurrentView('register')}
          />
        );
      case 'register':
        return (
          <RegisterForm
            onRegisterSuccess={handleRegisterSuccess}
            onSwitchToLogin={() => setCurrentView('login')}
          />
        );
      case 'home':
      case 'conversation':
      case 'ai-management':
      case 'settings':
      case 'user-stats':
      case 'detailed-report':
        return user ? (
          <div className="min-h-screen bg-gray-50 flex">
            {/* 사이드바 */}
            <Sidebar currentView={currentView} onNavigate={handleNavigate} user={user} />
            
            {/* 메인 컨텐츠 영역 */}
            <div className="flex-1 flex flex-col">
              {/* 상단 네비게이션 */}
              <nav className="bg-gradient-to-r from-indigo-600 to-indigo-700 shadow-lg border-b border-indigo-200">
                <div className="px-6 py-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <h1 className="text-xl font-semibold text-white">
                        {currentView === 'home' && '홈'}
                        {currentView === 'conversation' && '대화형 테스트'}
                        {currentView === 'ai-management' && 'AI 모델 관리'}
                        {currentView === 'settings' && '설정'}
                        {currentView === 'user-stats' && '사용자 통계'}
                        {currentView === 'detailed-report' && '상세 진단 리포트'}
                      </h1>
                    </div>
                    <div className="flex items-center space-x-4">
                      <button
                        onClick={() => {
                          setSelectedUserForStats(null); // '내 통계' 클릭 시 다른 사용자 통계 보기 초기화
                          setCurrentView('user-stats');
                        }}
                        className="btn-unified btn-unified-sm bg-white text-indigo-600 hover:bg-indigo-100 hover:text-indigo-700"
                      >
                        📊 내 통계
                      </button>
                      <span className="text-sm text-white font-medium">
                        안녕하세요, {user.full_name || user.username}님
                      </span>
                      <button
                        onClick={handleLogout}
                        className="btn-unified btn-unified-secondary btn-unified-sm"
                      >
                        로그아웃
                      </button>
                    </div>
                  </div>
                </div>
              </nav>

              {/* 페이지 컨텐츠 */}
              <div className={`flex-1 overflow-y-auto ${currentView === 'conversation' ? 'h-full' : ''}`}>
                {currentView === 'home' && (
                  <HomePage 
                    user={user} 
                    onNavigate={handleNavigate} 
                    onViewDetailedReport={handleViewDetailedReport}
                    onViewUserStats={handleViewUserStats} // 추가: prop 전달
                  />
                )}
                {currentView === 'conversation' && (
                  <ConversationTest user={user} onTestComplete={handleTestComplete} />
                )}
                {currentView === 'ai-management' && user.role === 'admin' && (
                  <AIModelManagement user={user} />
                )}
                {currentView === 'settings' && (
                  <SettingsPage user={user} onLogout={handleLogout} />
                )}
                {currentView === 'user-stats' && (
                  <UserTestStats
                    user={selectedUserForStats || user} // 선택된 사용자가 있으면 해당 사용자, 없으면 로그인한 사용자
                    onBack={handleBackFromUserStats} // 수정: 돌아가기 핸들러 연결
                  />
                )}
                {(() => {
                  console.log('Render condition check:', {
                    currentView,
                    selectedSessionId,
                    user: !!user,
                    condition: currentView === 'detailed-report' && selectedSessionId && user
                  });
                  return currentView === 'detailed-report' && selectedSessionId && user;
                })() && (
                  <DetailedReport
                    user={user}
                    sessionId={selectedSessionId}
                    onBack={handleBackFromDetailedReport}
                  />
                )}
              </div>
            </div>
          </div>
        ) : null;
      default:
        return null;
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="App">
        {renderContent()}
      </div>
    </QueryClientProvider>
  );
}

export default App;