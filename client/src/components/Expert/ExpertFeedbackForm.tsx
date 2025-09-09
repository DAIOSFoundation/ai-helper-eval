import React, { useState } from 'react';
import { dashboardAPI } from '../../api/dashboard';

interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  created_at: string;
}

interface ExpertFeedbackFormProps {
  responseId: string;
  expert: User;
  onFeedbackSubmitted: () => void;
  onClose: () => void;
}

const ExpertFeedbackForm: React.FC<ExpertFeedbackFormProps> = ({
  responseId,
  expert,
  onFeedbackSubmitted,
  onClose
}) => {
  const [feedbackScore, setFeedbackScore] = useState<number>(0);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [keywordsSuggested, setKeywordsSuggested] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 점수 범위 조정: 0-5로 변경 (DetailedReport의 ExpertScoreInput과 통일)
    if (feedbackScore < 0 || feedbackScore > 5) {
      setError('점수는 0-5 사이의 값이어야 합니다.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // API 호출은 updateExpertScore를 사용하고, comment/keywords는 현재 백엔드에 없으므로 제외
      await dashboardAPI.updateExpertScore(responseId, feedbackScore);
      // await dashboardAPI.submitExpertFeedback({ // 현재 백엔드 API에 없음
      //   response_id: responseId,
      //   expert_id: expert.id,
      //   feedback_score: feedbackScore,
      //   feedback_comment: feedbackComment || undefined,
      //   keywords_suggested: keywordsSuggested || undefined
      // });

      onFeedbackSubmitted();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.error || '피드백 제출에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-hidden shadow-xl">
        {/* 헤더 */}
        <div className="bg-indigo-600 text-white px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-semibold">전문가 피드백</h2>
          <button
            onClick={onClose}
            className="text-indigo-100 hover:text-white text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6 custom-scrollbar overflow-y-auto">
          {/* 점수 입력 */}
          <div>
            <label htmlFor="feedbackScore" className="block text-sm font-medium text-gray-700 mb-2">
              평가 점수 (0-5)
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="number"
                id="feedbackScore"
                min="0"
                max="5" // 0-5로 변경
                step="0.1"
                value={feedbackScore}
                onChange={(e) => setFeedbackScore(parseFloat(e.target.value) || 0)}
                className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
              <div className="flex-1">
                <input
                  type="range"
                  min="0"
                  max="5" // 0-5로 변경
                  step="0.1"
                  value={feedbackScore}
                  onChange={(e) => setFeedbackScore(parseFloat(e.target.value))}
                  className="w-full h-2 bg-indigo-200 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:bg-indigo-600 [&::-moz-range-thumb]:bg-indigo-600"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0 (낮음)</span>
                  <span>2.5 (보통)</span>
                  <span>5 (높음)</span>
                </div>
              </div>
            </div>
          </div>

          {/* 점수 해석 */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">점수 해석 (0-5점 척도)</h4>
            <div className="text-sm text-gray-600 space-y-1">
              <p><strong>0-1:</strong> 매우 낮은 수준</p>
              <p><strong>1.1-2:</strong> 낮은 수준</p>
              <p><strong>2.1-3:</strong> 중간 수준</p>
              <p><strong>3.1-4:</strong> 높은 수준</p>
              <p><strong>4.1-5:</strong> 매우 높은 수준</p>
            </div>
          </div>

          {/* 피드백 코멘트 (현재 백엔드에서 지원하지 않아 주석 처리) */}
          {/* <div>
            <label htmlFor="feedbackComment" className="block text-sm font-medium text-gray-700 mb-2">
              피드백 코멘트
            </label>
            <textarea
              id="feedbackComment"
              value={feedbackComment}
              onChange={(e) => setFeedbackComment(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="응답에 대한 전문가 의견을 입력하세요..."
            />
          </div> */}

          {/* 제안 키워드 (현재 백엔드에서 지원하지 않아 주석 처리) */}
          {/* <div>
            <label htmlFor="keywordsSuggested" className="block text-sm font-medium text-gray-700 mb-2">
              제안 키워드
            </label>
            <input
              type="text"
              id="keywordsSuggested"
              value={keywordsSuggested}
              onChange={(e) => setKeywordsSuggested(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="쉼표로 구분하여 키워드를 입력하세요 (예: 우울, 슬픔, 절망)"
            />
            <p className="text-xs text-gray-500 mt-1">
              이 키워드들은 향후 평가 템플릿 개선에 사용됩니다.
            </p>
          </div> */}

          {/* 에러 메시지 */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="text-red-800 text-sm">{error}</div>
            </div>
          )}

          {/* 버튼 */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="btn-unified btn-unified-secondary btn-unified-md"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-unified btn-unified-primary btn-unified-md disabled:opacity-50"
            >
              {loading ? '제출 중...' : '피드백 제출'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ExpertFeedbackForm;
