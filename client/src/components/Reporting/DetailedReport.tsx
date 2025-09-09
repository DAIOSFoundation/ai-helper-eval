import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../../api/dashboard';
import ExpertScoreInput from './ExpertScoreInput';
import { getTestTypeLabel } from '../../utils/helpers'; // 유틸리티 함수 임포트

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
  onBack: () => void;
}

const DetailedReport: React.FC<DetailedReportProps> = ({ user, sessionId, onBack }) => {
  const [sessionData, setSessionData] = useState<any>(null);
  const [responses, setResponses] = useState<TestResponse[]>([]);
  const [groupedScores, setGroupedScores] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedResponse, setSelectedResponse] = useState<TestResponse | null>(null);

  useEffect(() => {
    console.log('DetailedReport sessionId:', sessionId);
    if (sessionId) {
      loadSessionDetails();
    }
  }, [sessionId]);


  const loadSessionDetails = async () => {
    try {
      setLoading(true);
      
      // 현재 세션의 정보만 가져옴
      const sessionResponse = await dashboardAPI.getSessionDetails(sessionId);
      console.log('DetailedReport API response:', sessionResponse);
      
      setSessionData(sessionResponse);
      setResponses(sessionResponse.responses || []);
      
      // 그룹 점수는 현재 세션만 사용
      const groupedScoresResponse = await dashboardAPI.getSessionGroupedScores(sessionId);
      setGroupedScores(groupedScoresResponse);
      
    } catch (err: any) {
      console.error('DetailedReport API error:', err);
      setError(err.response?.data?.error || '세션 상세 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const updateExpertScore = async (responseId: string, score: number) => {
    try {
      await dashboardAPI.updateExpertScore(responseId, score);
      // 응답 목록 업데이트
      setResponses(prev => prev.map(response => 
        response.id === responseId 
          ? { ...response, expert_score: score }
          : response
      ));
      // 그룹 점수도 다시 로드하여 업데이트 반영
      const groupedScoresResponse = await dashboardAPI.getSessionGroupedScores(sessionId);
      setGroupedScores(groupedScoresResponse);
    } catch (err: any) {
      console.error('전문가 점수 업데이트 실패:', err);
    }
  };

  // 기존 getTestTypeLabel 함수 제거 (유틸리티 사용)
  // const getTestTypeLabel = (testType: string) => {
  //   if (!testType) return '알 수 없는 테스트';
    
  //   switch (testType.toLowerCase()) {
  //     case 'cdi':
  //       return 'CDI (아동 우울 척도)';
  //     case 'rcmas':
  //       return 'RCMAS (아동 불안 척도)';
  //     case 'bdi':
  //       return 'BDI (벡 우울 척도)';
  //     default:
  //       return testType.toUpperCase();
  //   }
  // };

  const getScoreColor = (score: number) => {
    if (score >= 4) return 'text-green-600 font-bold';
    if (score >= 3) return 'text-yellow-600 font-semibold';
    if (score >= 2) return 'text-orange-600';
    return 'text-red-600';
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

  if (!sessionId) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <p className="text-red-600 mb-4">세션 ID가 없습니다.</p>
            <button
              onClick={onBack}
              className="btn-unified btn-unified-secondary btn-unified-sm"
            >
              돌아가기
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">상세 리포트를 불러오는 중...</p>
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
            <div className="flex space-x-3 justify-center">
              <button
                onClick={loadSessionDetails}
                className="btn-unified btn-unified-primary btn-unified-sm"
              >
                다시 시도
              </button>
              <button
                onClick={onBack}
                className="btn-unified btn-unified-secondary btn-unified-sm"
              >
                돌아가기
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex items-center space-x-4 mb-4">
          <button
            onClick={onBack}
            className="btn-unified btn-unified-ghost btn-unified-sm"
          >
            ← 돌아가기
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            상세 진단 리포트
          </h1>
        </div>
        <p className="text-gray-600 text-lg">
          {sessionData ? getTestTypeLabel(sessionData.test_type) : '로딩 중...'} - {user.full_name || user.username}
        </p>
      </div>

      <div>
          {/* 세션 정보 */}
          <div className="bg-white rounded-xl p-6 mb-6 shadow-md border border-gray-200">
            <h3 className="text-2xl font-bold mb-4 text-gray-800">세션 정보</h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm mb-6">
              <div className="flex flex-col">
                <span className="font-semibold text-gray-600 mb-2">시작 시간</span>
                <p className="text-gray-800 text-base">{new Date(sessionData?.started_at).toLocaleString('ko-KR')}</p>
              </div>
              <div className="flex flex-col">
                <span className="font-semibold text-gray-600 mb-2">완료 시간</span>
                <p className="text-gray-800 text-base">{sessionData?.completed_at ? new Date(sessionData.completed_at).toLocaleString('ko-KR') : '진행중'}</p>
              </div>
              <div className="flex flex-col">
                <span className="font-semibold text-gray-600 mb-2">진행률</span>
                <p className="text-gray-800 text-base">{sessionData?.completed_questions}/{sessionData?.total_questions} 문항</p>
              </div>
              <div className="flex flex-col">
                <span className="font-semibold text-gray-600 mb-2">총 점수</span>
                <p className={`text-2xl font-bold ${getScoreColor(sessionData?.total_score || 0)}`}>
                  {sessionData?.total_score?.toFixed(1) || '0.0'}
                </p>
              </div>
            </div>

            {/* 그룹별 점수 요약 */}
            {groupedScores && groupedScores.grouped_scores && (
              <div className="border-t border-gray-200 pt-6">
                <h4 className="text-lg font-bold mb-4 text-gray-800">📊 평가 영역별 점수</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {groupedScores.grouped_scores.map((group: any, index: number) => (
                    <div key={index} className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
                      <div className="flex justify-between items-center mb-2">
                        <h5 className="font-bold text-gray-900 text-sm">{group.question_category}</h5>
                        <span className="text-xs text-gray-600">{group.question_count}문항</span>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-gray-600">AI 점수:</span>
                          <span className={`font-bold ${getScoreColor(group.avg_ai_score || 0)}`}>
                            {group.avg_ai_score?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        {group.avg_expert_score != null && ( /* null과 undefined 모두 확인 */
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-gray-600">전문가 점수:</span>
                            <span className={`font-bold ${getScoreColor(group.avg_expert_score)}`}>
                              {group.avg_expert_score.toFixed(1)}
                            </span>
                          </div>
                        )}
                        <div className="flex justify-between items-center pt-1 border-t border-gray-100">
                          <span className="text-xs font-semibold text-gray-700">총점:</span>
                          <span className={`font-bold text-sm ${getScoreColor(group.total_ai_score || 0)}`}>
                            {group.total_ai_score?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* 전체 요약 */}
                {groupedScores.overall_stats && (
                  <div className="mt-4 bg-gray-50 rounded-lg p-4 border border-gray-200 shadow-sm">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-gray-800">전체 평균 점수:</span>
                      <span className={`text-xl font-bold ${getScoreColor(groupedScores.overall_stats.overall_avg_ai_score || 0)}`}>
                        {groupedScores.overall_stats.overall_avg_ai_score?.toFixed(1) || '0.0'}
                      </span>
                    </div>
                    {groupedScores.overall_stats.overall_avg_expert_score != null && ( /* null과 undefined 모두 확인 */
                      <div className="flex justify-between items-center mt-2">
                        <span className="font-bold text-gray-800">전체 전문가 평균 점수:</span>
                        <span className={`text-xl font-bold ${getScoreColor(groupedScores.overall_stats.overall_avg_expert_score || 0)}`}>
                          {groupedScores.overall_stats.overall_avg_expert_score?.toFixed(1) || '0.0'}
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* 응답 상세 분석 */}
          <div>
            <h3 className="text-2xl font-bold mb-6 text-gray-800">응답 상세 분석</h3>
            
            {/* 응답 목록 */}
            <div className="space-y-4">
              {responses.map((response, responseIndex) => (
                <div key={response.id} className="bg-white rounded-lg p-4 shadow-md border border-gray-200">
                  {/* 문항 헤더 */}
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="text-lg font-bold text-gray-900">문항 {parseInt(response.question_id) + 1}</h4>
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                        response.detected_intent === 'answer' 
                          ? 'bg-green-100 text-green-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {response.detected_intent === 'answer' ? '답변' : response.detected_intent}
                      </span>
                      <span className={`text-sm font-bold px-2 py-1 rounded-full ${getScoreColor(response.calculated_score || 0)}`}>
                        {response.calculated_score?.toFixed(1) || '0.0'}
                      </span>
                    </div>
                  </div>

                  {/* 완전 수평 레이아웃 */}
                  <div className="flex flex-wrap gap-3">
                    {/* 질문 */}
                    <div className="flex-1 min-w-[300px] bg-indigo-50 rounded-lg p-3 border border-indigo-200">
                      <h5 className="font-bold text-gray-900 mb-2 text-sm">📝 질문</h5>
                      <p className="text-gray-700 text-sm leading-snug">
                        {response.question_text}
                      </p>
                    </div>

                    {/* 사용자 응답 */}
                    <div className="flex-1 min-w-[300px] bg-green-50 rounded-lg p-3 border border-green-200">
                      <h5 className="font-bold text-gray-900 mb-2 text-sm">💬 사용자 응답</h5>
                      <p className="text-gray-700 text-sm leading-snug">
                        {response.user_response}
                      </p>
                    </div>

                    {/* AI 점수 */}
                    <div className="w-24 bg-indigo-50 border border-indigo-200 rounded-lg p-3 text-center">
                      <h5 className="font-bold text-gray-900 mb-1 text-xs">🤖 AI</h5>
                      <p className={`text-lg font-bold ${getScoreColor(response.calculated_score || 0)}`}>
                        {response.calculated_score?.toFixed(1) || '0.0'}
                      </p>
                    </div>

                    {/* 전문가 점수 */}
                    <div className="w-28 bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-center">
                      <h5 className="font-bold text-gray-900 mb-1 text-xs">👨‍⚕️ 전문가</h5>
                      {user.role === 'expert' || user.role === 'admin' ? (
                        <ExpertScoreInput
                          responseId={response.id}
                          currentScore={response.expert_score}
                          onScoreUpdate={(score) => updateExpertScore(response.id, score)}
                        />
                      ) : (
                        <p className={`text-lg font-bold ${response.expert_score ? getScoreColor(response.expert_score) : 'text-gray-500'}`}>
                          {response.expert_score !== undefined ? response.expert_score.toFixed(1) : 'N/A'}
                        </p>
                      )}
                    </div>

                    {/* 키워드 */}
                    <div className="flex-1 min-w-[200px] bg-gray-50 rounded-lg p-3 border border-gray-200">
                      <h5 className="font-bold text-gray-900 mb-1 text-xs">🔍 키워드</h5>
                      {response.keywords ? (
                        <div className="flex flex-wrap gap-1">
                          {JSON.parse(response.keywords).slice(0, 6).map((keyword: string, keywordIndex: number) => (
                            <span
                              key={keywordIndex}
                              className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-xs font-medium"
                            >
                              {keyword}
                            </span>
                          ))}
                          {JSON.parse(response.keywords).length > 6 && (
                            <span className="text-xs text-gray-500">+{JSON.parse(response.keywords).length - 6}</span>
                          )}
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">키워드 없음</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
      </div>
    </div>
  );
};

export default DetailedReport;