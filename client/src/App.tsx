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
import DashboardStats from './components/Dashboard/DashboardStats';
import SessionList from './components/Dashboard/SessionList';
import UserProgress from './components/Dashboard/UserProgress';
import AdminUserProgress from './components/Dashboard/AdminUserProgress';
import TestInterface from './components/Test/TestInterface';
import './App.css';

const queryClient = new QueryClient();

type View = 'login' | 'register' | 'dashboard' | 'test';

function App() {
  const [currentView, setCurrentView] = useState<View>('login');
  const [user, setUser] = useState<User | null>(null);
  const [selectedTestType, setSelectedTestType] = useState<string>('conversation');

  useEffect(() => {
    const savedUser = authAPI.getCurrentUser();
    if (savedUser) {
      setUser(savedUser);
      setCurrentView('dashboard');
    }
  }, []);

  const handleLoginSuccess = (userData: User) => {
    setUser(userData);
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    authAPI.logout();
    setUser(null);
    setCurrentView('login');
  };

  const handleRegisterSuccess = () => {
    setCurrentView('login');
  };

  const handleStartConversation = () => {
    setSelectedTestType('conversation');
    setCurrentView('test');
  };

  const handleTestComplete = (result: any) => {
    // 테스트 완료 후 대시보드로 돌아가기
    setTimeout(() => {
      setCurrentView('dashboard');
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
      case 'dashboard':
        return (
          <div className="min-h-screen bg-gray-50">
            {/* 네비게이션 */}
            <nav className="bg-white shadow">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                  <div className="flex items-center">
                    <h1 className="text-xl font-semibold text-gray-900">
                      AI Helper Evaluation System
                    </h1>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-700">
                      안녕하세요, {user?.full_name || user?.username}님
                    </span>
                    <button
                      onClick={handleLogout}
                      className="text-sm text-indigo-600 hover:text-indigo-500"
                    >
                      로그아웃
                    </button>
                  </div>
                </div>
              </div>
            </nav>

            {/* 메인 컨텐츠 */}
            <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
              <div className="px-4 py-6 sm:px-0">
                {/* 대화 시작 버튼 */}
                <div className="mb-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">AI 상담사와 대화하기</h2>
                  <div className="max-w-md">
                    <button
                      onClick={handleStartConversation}
                      className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold py-6 px-8 rounded-lg transition duration-200 shadow-lg hover:shadow-xl"
                    >
                      <div className="text-center">
                        <h3 className="text-xl font-semibold mb-2">💬 대화 시작하기</h3>
                        <p className="text-sm opacity-90">
                          AI 상담사와 자연스럽게 대화하세요.<br/>
                          필요시 자동으로 진단 테스트가 진행됩니다.
                        </p>
                      </div>
                    </button>
                  </div>
                  <div className="mt-4 text-sm text-gray-600">
                    <p>💡 <strong>진단 테스트 안내:</strong></p>
                    <ul className="list-disc list-inside mt-2 space-y-1">
                      <li>대화 중 특정 키워드가 감지되면 자동으로 진단 테스트가 시작됩니다</li>
                      <li>CDI (아동 우울 척도), RCMAS (아동 불안 척도), BDI (벡 우울 척도) 순서로 진행됩니다</li>
                      <li>각 테스트는 20개 질문으로 구성되어 있습니다</li>
                    </ul>
                  </div>
                </div>

                {/* 관리자용 전체 사용자 진행률 */}
                {user && user.role === 'admin' && (
                  <div className="mb-8">
                    <AdminUserProgress currentUser={user} />
                  </div>
                )}

                {/* 사용자별 진행률 */}
                {user && user.role !== 'admin' && (
                  <div className="mb-8">
                    <UserProgress user={user} />
                  </div>
                )}

                {/* 대시보드 통계 */}
                <div className="mb-8">
                  <DashboardStats stats={{
                    overall_stats: {
                      total_sessions: 0,
                      total_users: 0,
                      avg_score: 0,
                      total_responses: 0
                    },
                    test_type_stats: [],
                    recent_sessions: []
                  }} />
                </div>

                {/* 사용자 세션 목록 */}
                {user && <SessionList user={user} />}
              </div>
            </div>
          </div>
        );
      case 'test':
        return user ? (
          <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="mb-6">
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className="text-indigo-600 hover:text-indigo-500 text-sm"
                >
                  ← 대시보드로 돌아가기
                </button>
              </div>
              <TestInterface
                user={user}
                testType={selectedTestType}
                onTestComplete={handleTestComplete}
              />
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
