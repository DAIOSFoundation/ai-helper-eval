import React, { useState, useEffect, useRef } from 'react';
import { sessionAPI } from '../../api/session';

interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  created_at: string;
}

interface MessageResponse {
  session_id: string;
  response: string;
  intent: string;
  is_complete: boolean;
  diagnosis_result?: {
    cdi_score: number;
    rcmas_score: number;
    bdi_score: number;
    interpretation: {
      cdi: string;
      rcmas: string;
      bdi: string;
    };
  };
}

interface TestInterfaceProps {
  user: User;
  testType: string;
  onTestComplete: (result: any) => void;
}

const TestInterface: React.FC<TestInterfaceProps> = ({ user, testType, onTestComplete }) => {
  const [sessionId, setSessionId] = useState<string>('');
  const [messages, setMessages] = useState<Array<{ type: 'user' | 'system'; content: string; timestamp: string }>>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [testComplete, setTestComplete] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const hasStarted = useRef(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const focusTextarea = () => {
    textareaRef.current?.focus();
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    startTest();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const startTest = async () => {
    // 이미 세션이 시작되었으면 중복 실행 방지
    if (hasStarted.current || sessionId || loading) {
      console.log('Session already started or starting, skipping...');
      return;
    }
    
    hasStarted.current = true;
    
    try {
      setLoading(true);
      console.log('Starting conversation with:', { user_id: user.id });
      const response = await sessionAPI.startSession({
        user_id: user.id
      });
      console.log('Session started:', JSON.stringify(response, null, 2));
      
      setSessionId(response.session_id);
      setMessages([{
        type: 'system',
        content: response.welcome_message,
        timestamp: new Date().toLocaleString('ko-KR')
      }]);
      
      // 대화 시작 후 입력창에 포커스
      setTimeout(() => {
        focusTextarea();
      }, 100);
    } catch (error) {
      console.error('대화 시작 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !sessionId) return;

    const userMessage = currentMessage.trim();
    setCurrentMessage('');
    setLoading(true);

    // 사용자 메시지 추가
    setMessages(prev => [...prev, {
      type: 'user',
      content: userMessage,
      timestamp: new Date().toLocaleString('ko-KR')
    }]);

    try {
      console.log('Sending message:', { session_id: sessionId, message: userMessage });
      const response: MessageResponse = await sessionAPI.sendMessage({
        session_id: sessionId,
        message: userMessage
      });
      console.log('Received response:', JSON.stringify(response, null, 2));

      // 시스템 응답 추가
      setMessages(prev => [...prev, {
        type: 'system',
        content: response.response,
        timestamp: new Date().toLocaleString('ko-KR')
      }]);

      // 테스트 완료 확인
      if (response.is_complete && response.diagnosis_result) {
        setTestComplete(true);
        setDiagnosisResult(response.diagnosis_result);
        onTestComplete(response.diagnosis_result);
      } else {
        // 테스트가 완료되지 않았으면 입력창에 포커스
        setTimeout(() => {
          focusTextarea();
        }, 100);
      }
    } catch (error) {
      console.error('메시지 전송 실패:', error);
      setMessages(prev => [...prev, {
        type: 'system',
        content: '죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.',
        timestamp: new Date().toLocaleString('ko-KR')
      }]);
      // 에러 발생 시에도 입력창에 포커스
      setTimeout(() => {
        focusTextarea();
      }, 100);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getTestTypeLabel = (type: string) => {
    switch (type) {
      case 'conversation':
        return 'AI 상담사와 대화';
      default:
        return 'AI 상담사와 대화';
    }
  };

  if (loading && !sessionId) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-white shadow-md rounded-lg flex flex-col border border-gray-200">

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg shadow-sm ${
                message.type === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <p className={`text-xs mt-1 ${
                message.type === 'user' ? 'text-indigo-100' : 'text-gray-500'
              }`}>
                {message.timestamp}
              </p>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg shadow-sm">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                <span className="text-sm">답변 중...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 */}
      {!testComplete && (
        <div className="border-t border-gray-200 p-6 bg-gray-50">
          <div className="flex space-x-4">
            <textarea
              ref={textareaRef}
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="메시지를 입력하세요..."
              className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none custom-scrollbar"
              rows={2}
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !currentMessage.trim()}
              className="btn-unified btn-unified-primary btn-unified-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              전송
            </button>
          </div>
        </div>
      )}

      {/* 테스트 완료 결과 */}
      {testComplete && diagnosisResult && (
        <div className="border-t border-gray-200 p-6 bg-indigo-50">
          <h3 className="text-lg font-semibold text-indigo-800 mb-4">테스트 완료!</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg shadow-sm border border-indigo-200">
              <h4 className="font-medium text-gray-900">CDI (아동 우울 척도)</h4>
              <p className="text-2xl font-bold text-blue-600">{diagnosisResult.cdi_score}</p>
              <p className="text-sm text-gray-600 line-clamp-2">{diagnosisResult.interpretation.cdi}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm border border-yellow-200">
              <h4 className="font-medium text-gray-900">RCMAS (아동 불안 척도)</h4>
              <p className="text-2xl font-bold text-yellow-600">{diagnosisResult.rcmas_score}</p>
              <p className="text-sm text-gray-600 line-clamp-2">{diagnosisResult.interpretation.rcmas}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm border border-red-200">
              <h4 className="font-medium text-gray-900">BDI (벡 우울 척도)</h4>
              <p className="text-2xl font-bold text-red-600">{diagnosisResult.bdi_score}</p>
              <p className="text-sm text-gray-600 line-clamp-2">{diagnosisResult.interpretation.bdi}</p>
            </div>
          </div>
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              <strong>주의:</strong> 이 결과는 참고용이며, 전문적인 진단을 위해서는 전문의와 상담하시기 바랍니다.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestInterface;
