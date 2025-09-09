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

interface TestResponse {
  id: string;
  session_id: string;
  question_id: string;
  question_text: string;
  user_response: string;
  detected_intent: string;
  calculated_score: number;
  expert_score?: number;
  keywords: string;
  created_at: string;
}

interface ExpertFeedback {
  id: string;
  response_id: string;
  expert_id: string;
  feedback_score: number;
  feedback_comment?: string;
  keywords_suggested?: string;
  created_at: string;
  expert_username: string;
}
import ExpertFeedbackForm from '../Expert/ExpertFeedbackForm';

interface DetailedReportProps {
  user: User;
  sessionId: string;
  onClose: () => void;
}

const DetailedReport: React.FC<DetailedReportProps> = ({ user, sessionId, onClose }) => {
  const [sessionData, setSessionData] = useState<any>(null);
  const [responses, setResponses] = useState<TestResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedResponse, setSelectedResponse] = useState<TestResponse | null>(null);
  const [expertFeedback, setExpertFeedback] = useState<ExpertFeedback[]>([]);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);

  useEffect(() => {
    loadSessionDetails();
  }, [sessionId]);

  const loadSessionDetails = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.getSessionDetails(sessionId);
      setSessionData(response.session);
      setResponses(response.responses);
    } catch (err: any) {
      setError(err.response?.data?.error || '세션 상세 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const loadExpertFeedback = async (responseId: string) => {
    try {
      const response = await dashboardAPI.getExpertFeedback(responseId);
      setExpertFeedback(response.feedback);
    } catch (err: any) {
      console.error('전문가 피드백 로드 실패:', err);
    }
  };

  const handleResponseClick = (response: TestResponse) => {
    setSelectedResponse(response);
    loadExpertFeedback(response.id);
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

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-red-600 font-bold';
    if (score >= 5) return 'text-yellow-600 font-semibold';
    return 'text-green-600';
  };

  const getScoreInterpretation = (score: number, testType: string) => {
    switch (testType) {
      case 'cdi':
        if (score >= 19) return '심각한 우울';
        if (score >= 13) return '중간 정도 우울';
        if (score >= 7) return '경미한 우울';
        return '정상';
      case 'rcmas':
        if (score >= 15) return '높은 불안';
        if (score >= 10) return '중간 정도 불안';
        if (score >= 5) return '경미한 불안';
        return '정상';
      case 'bdi':
        if (score >= 29) return '심각한 우울';
        if (score >= 20) return '중간 정도 우울';
        if (score >= 14) return '경미한 우울';
        return '정상';
      default:
        return '평가 불가';
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
            <span>상세 리포트를 불러오는 중...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md">
          <div className="text-red-600 mb-4">{error}</div>
          <div className="flex space-x-3">
            <button
              onClick={loadSessionDetails}
              className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
            >
              다시 시도
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
            >
              닫기
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* 헤더 */}
        <div className="bg-indigo-600 text-white px-6 py-4 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold">상세 진단 리포트</h2>
            <p className="text-indigo-100 text-sm">
              {getTestTypeLabel(sessionData?.test_type)} - {user.full_name || user.username}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-indigo-100 hover:text-white text-2xl"
          >
            ×
          </button>
        </div>

        <div className="flex h-[calc(90vh-80px)]">
          {/* 왼쪽: 응답 목록 */}
          <div className="w-1/2 border-r overflow-y-auto">
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">테스트 응답 목록</h3>
              
              {/* 세션 정보 */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-600">시작 시간:</span>
                    <p>{new Date(sessionData?.started_at).toLocaleString('ko-KR')}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">완료 시간:</span>
                    <p>{sessionData?.completed_at ? new Date(sessionData.completed_at).toLocaleString('ko-KR') : '진행중'}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">진행률:</span>
                    <p>{sessionData?.completed_questions}/{sessionData?.total_questions} 문항</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">총 점수:</span>
                    <p className={getScoreColor(sessionData?.total_score || 0)}>
                      {sessionData?.total_score?.toFixed(1) || '0.0'}
                    </p>
                  </div>
                </div>
              </div>

              {/* 응답 목록 */}
              <div className="space-y-3">
                {responses.map((response, index) => (
                  <div
                    key={response.id}
                    onClick={() => handleResponseClick(response)}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedResponse?.id === response.id
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-gray-900">문항 {index + 1}</h4>
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm px-2 py-1 rounded ${
                          response.detected_intent === 'answer' 
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {response.detected_intent === 'answer' ? '답변' : response.detected_intent}
                        </span>
                        <span className={`text-sm font-medium ${getScoreColor(response.calculated_score || 0)}`}>
                          {response.calculated_score?.toFixed(1) || '0.0'}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                      {response.question_text}
                    </p>
                    <p className="text-sm text-gray-800 line-clamp-2">
                      <strong>답변:</strong> {response.user_response}
                    </p>
                    {response.expert_score && (
                      <p className="text-xs text-blue-600 mt-1">
                        전문가 점수: {response.expert_score.toFixed(1)}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 오른쪽: 선택된 응답 상세 */}
          <div className="w-1/2 overflow-y-auto">
            {selectedResponse ? (
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">응답 상세 분석</h3>
                
                {/* 질문 정보 */}
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <h4 className="font-medium text-gray-900 mb-2">질문</h4>
                  <p className="text-gray-700">{selectedResponse.question_text}</p>
                </div>

                {/* 사용자 응답 */}
                <div className="bg-blue-50 rounded-lg p-4 mb-4">
                  <h4 className="font-medium text-gray-900 mb-2">사용자 응답</h4>
                  <p className="text-gray-700">{selectedResponse.user_response}</p>
                </div>

                {/* 점수 분석 */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="bg-white border rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">AI 계산 점수</h4>
                    <p className={`text-2xl font-bold ${getScoreColor(selectedResponse.calculated_score || 0)}`}>
                      {selectedResponse.calculated_score?.toFixed(1) || '0.0'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {getScoreInterpretation(selectedResponse.calculated_score || 0, sessionData?.test_type)}
                    </p>
                  </div>
                  {selectedResponse.expert_score && (
                    <div className="bg-white border rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-2">전문가 점수</h4>
                      <p className={`text-2xl font-bold ${getScoreColor(selectedResponse.expert_score)}`}>
                        {selectedResponse.expert_score.toFixed(1)}
                      </p>
                      <p className="text-sm text-gray-600">
                        {getScoreInterpretation(selectedResponse.expert_score, sessionData?.test_type)}
                      </p>
                    </div>
                  )}
                </div>

                {/* 키워드 분석 */}
                {selectedResponse.keywords && (
                  <div className="bg-yellow-50 rounded-lg p-4 mb-4">
                    <h4 className="font-medium text-gray-900 mb-2">추출된 키워드</h4>
                    <div className="flex flex-wrap gap-2">
                      {JSON.parse(selectedResponse.keywords).map((keyword: string, index: number) => (
                        <span
                          key={index}
                          className="bg-yellow-200 text-yellow-800 px-2 py-1 rounded text-sm"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* 전문가 피드백 */}
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-4">
                    <h4 className="font-medium text-gray-900">전문가 피드백</h4>
                    {user.role === 'expert' || user.role === 'admin' ? (
                      <button
                        onClick={() => setShowFeedbackForm(true)}
                        className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                      >
                        피드백 추가
                      </button>
                    ) : null}
                  </div>
                  
                  {expertFeedback.length > 0 ? (
                    expertFeedback.map((feedback, index) => (
                      <div key={index} className="border-l-4 border-green-400 pl-4 mb-3">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium text-gray-900">{feedback.expert_username}</span>
                          <span className="text-sm text-gray-500">
                            {new Date(feedback.created_at).toLocaleDateString('ko-KR')}
                          </span>
                        </div>
                        <p className="text-gray-700 mb-2">{feedback.feedback_comment}</p>
                        <div className="flex items-center space-x-4 text-sm">
                          <span className="text-gray-600">
                            점수: <span className="font-medium">{feedback.feedback_score.toFixed(1)}</span>
                          </span>
                          {feedback.keywords_suggested && (
                            <span className="text-gray-600">
                              제안 키워드: {feedback.keywords_suggested}
                            </span>
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-sm">아직 전문가 피드백이 없습니다.</p>
                  )}
                </div>
              </div>
            ) : (
              <div className="p-6 flex items-center justify-center h-full">
                <div className="text-center text-gray-500">
                  <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p>왼쪽에서 응답을 선택하면 상세 분석을 볼 수 있습니다.</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 전문가 피드백 폼 */}
        {showFeedbackForm && selectedResponse && (
          <ExpertFeedbackForm
            responseId={selectedResponse.id}
            expert={user}
            onFeedbackSubmitted={() => {
              loadExpertFeedback(selectedResponse.id);
              setShowFeedbackForm(false);
            }}
            onClose={() => setShowFeedbackForm(false)}
          />
        )}
      </div>
    </div>
  );
};

export default DetailedReport;
