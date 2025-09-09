import React, { useState } from 'react';

interface ExpertScoreInputProps {
  responseId: string;
  currentScore?: number;
  onScoreUpdate: (score: number) => void;
}

const ExpertScoreInput: React.FC<ExpertScoreInputProps> = ({ responseId, currentScore, onScoreUpdate }) => {
  const [score, setScore] = useState<number>(currentScore || 0);
  const [isEditing, setIsEditing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSave = async () => {
    if (score < 0 || score > 5) {
      alert('점수는 0-5 사이의 값이어야 합니다.');
      return;
    }

    setIsSubmitting(true);
    try {
      await onScoreUpdate(score);
      setIsEditing(false);
    } catch (error) {
      console.error('점수 업데이트 실패:', error);
      alert('점수 업데이트에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setScore(currentScore || 0);
    setIsEditing(false);
  };

  const getScoreColor = (score: number) => {
    if (score >= 4) return 'text-green-600';
    if (score >= 3) return 'text-yellow-600';
    if (score >= 2) return 'text-orange-600';
    return 'text-red-600';
  };

  if (isEditing) {
    return (
      <div className="space-y-2">
        <div className="flex items-center space-x-2">
          <input
            type="number"
            min="0"
            max="5"
            step="0.1"
            value={score}
            onChange={(e) => setScore(parseFloat(e.target.value) || 0)}
            className="w-16 px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="0.0"
            autoFocus
          />
          <span className="text-xs text-gray-500">/ 5.0</span>
        </div>
        <div className="flex space-x-1">
          <button
            onClick={handleSave}
            disabled={isSubmitting}
            className="btn-unified btn-unified-success btn-unified-sm disabled:opacity-50"
          >
            {isSubmitting ? '저장중...' : '저장'}
          </button>
          <button
            onClick={handleCancel}
            className="btn-unified btn-unified-secondary btn-unified-sm"
          >
            취소
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="text-center">
      {currentScore !== undefined && currentScore > 0 ? (
        <div>
          <p className={`text-2xl font-bold ${getScoreColor(currentScore)}`}>
            {currentScore.toFixed(1)}
          </p>
          <button
            onClick={() => setIsEditing(true)}
            className="text-xs text-indigo-600 hover:text-indigo-700 underline mt-1 btn-ghost-indigo"
          >
            수정
          </button>
        </div>
      ) : (
        <div>
          <p className="text-gray-500 text-xs mb-2">점수 미입력</p>
          <button
            onClick={() => setIsEditing(true)}
            className="btn-unified btn-unified-primary btn-unified-sm"
          >
            점수 입력
          </button>
        </div>
      )}
    </div>
  );
};

export default ExpertScoreInput;
