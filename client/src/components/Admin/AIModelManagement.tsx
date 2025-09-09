import React from 'react';

interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  created_at: string;
}

interface AIModelManagementProps {
  user: User;
}

const AIModelManagement: React.FC<AIModelManagementProps> = ({ user }) => {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI 모델 관리</h1>
        <p className="text-gray-600">
          AI 모델의 설정과 성능을 관리할 수 있습니다.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 모델 설정 */}
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">모델 설정</h3>
          <div className="space-y-4">
            <div>
              <label htmlFor="modelVersion" className="block text-sm font-medium text-gray-700 mb-2">
                모델 버전
              </label>
              <select 
                id="modelVersion" 
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option>v1.0.0</option>
                <option>v1.1.0</option>
                <option>v2.0.0</option>
              </select>
            </div>
            <div>
              <label htmlFor="responseTemperature" className="block text-sm font-medium text-gray-700 mb-2">
                응답 온도
              </label>
              <input
                id="responseTemperature"
                type="range"
                min="0"
                max="1"
                step="0.1"
                defaultValue="0.7"
                className="w-full h-2 bg-indigo-200 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:bg-indigo-600 [&::-moz-range-thumb]:bg-indigo-600"
              />
              <div className="text-sm text-gray-500 mt-1">0.7 (권장)</div>
            </div>
            <div>
              <label htmlFor="maxTokens" className="block text-sm font-medium text-gray-700 mb-2">
                최대 토큰 수
              </label>
              <input
                id="maxTokens"
                type="number"
                defaultValue="1000"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
          <button className="btn-unified btn-unified-primary btn-unified-md btn-full mt-6">
            설정 저장
          </button>
        </div>

        {/* 성능 모니터링 */}
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">성능 모니터링</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg shadow-sm">
              <span className="text-sm font-medium text-gray-700">평균 응답 시간</span>
              <span className="text-sm font-semibold text-green-600">1.2초</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg shadow-sm">
              <span className="text-sm font-medium text-gray-700">일일 요청 수</span>
              <span className="text-sm font-semibold text-indigo-600">1,234</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg shadow-sm">
              <span className="text-sm font-medium text-gray-700">성공률</span>
              <span className="text-sm font-semibold text-green-600">99.8%</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg shadow-sm">
              <span className="text-sm font-medium text-gray-700">에러율</span>
              <span className="text-sm font-semibold text-red-600">0.2%</span>
            </div>
          </div>
          <button className="btn-unified btn-unified-success btn-unified-md btn-full mt-6">
            상세 보고서 보기
          </button>
        </div>
      </div>

      {/* 모델 학습 데이터 */}
      <div className="mt-6 bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">학습 데이터 관리</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-indigo-50 rounded-lg border border-indigo-200 shadow-sm">
            <div className="text-2xl font-bold text-indigo-600">1,250</div>
            <div className="text-sm text-gray-600">총 대화 세션</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200 shadow-sm">
            <div className="text-2xl font-bold text-green-600">850</div>
            <div className="text-sm text-gray-600">완료된 테스트</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg border border-purple-200 shadow-sm">
            <div className="text-2xl font-bold text-purple-600">95.2%</div>
            <div className="text-sm text-gray-600">정확도</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIModelManagement;
