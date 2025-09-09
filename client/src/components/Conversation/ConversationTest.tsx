import React from 'react';
import TestInterface from '../Test/TestInterface';

interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  created_at: string;
}

interface ConversationTestProps {
  user: User;
  onTestComplete: (result: any) => void;
}

const ConversationTest: React.FC<ConversationTestProps> = ({ user, onTestComplete }) => {
  return (
    <div className="w-full h-full flex flex-col">

      {/* 안내 섹션 */}
      <div className="p-6 bg-gray-50 border-b border-gray-200">
        <div className="w-full">
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h1 className="text-3xl font-bold text-gray-900 mb-3 flex items-center">
              <span className="text-2xl mr-2 text-indigo-600">💬</span>
              AI 상담사와 대화하기
            </h1>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200 shadow-sm">
                <div className="flex items-center mb-2">
                  <span className="text-2xl mr-2 text-indigo-600">🔍</span>
                  <h4 className="font-semibold text-indigo-900">자동 감지</h4>
                </div>
                <p className="text-indigo-800 text-sm">
                  대화 중 특정 키워드가 감지되면 자동으로 진단 테스트가 시작됩니다
                </p>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg border border-green-200 shadow-sm">
                <div className="flex items-center mb-2">
                  <span className="text-2xl mr-2 text-green-600">📋</span>
                  <h4 className="font-semibold text-green-900">진단 순서</h4>
                </div>
                <p className="text-green-800 text-sm">
                  CDI (아동 우울 척도), RCMAS (아동 불안 척도), BDI (벡 우울 척도) 순서로 진행됩니다
                </p>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200 shadow-sm">
                <div className="flex items-center mb-2">
                  <span className="text-2xl mr-2 text-purple-600">📊</span>
                  <h4 className="font-semibold text-purple-900">테스트 구성</h4>
                </div>
                <p className="text-purple-800 text-sm">
                  각 테스트는 20개 질문으로 구성되어 있습니다
                </p>
              </div>
            </div>
            
          </div>
        </div>
      </div>

      {/* 대화 인터페이스 섹션 */}
      <div className="flex-1 p-4 bg-gray-50">
        <div className="w-full h-full">
          <div className="bg-white rounded-lg shadow-md h-full flex flex-col border border-gray-200">
            <TestInterface
              user={user}
              testType="conversation"
              onTestComplete={onTestComplete}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationTest;
