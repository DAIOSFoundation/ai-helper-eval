# -*- coding: utf-8 -*-
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from modules.entities import EntityTracker
from modules.bow import BoW_encoder
from modules.rnn_gru_net import RNN_GRU_net
from modules.embed import UtteranceEmbed
from modules.actions import ActionTracker
from modules.similarity_scorer import SimilarityScorer
from database import db
import modules.util as util
import numpy as np
import torch
import uuid
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# JSON 인코딩 설정 - 한글 유니코드 이스케이프 방지
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# 전역 변수로 세션 관리
sessions = {}

# 20개 테스트 질문 목록
TEST_QUESTIONS = [
    "야, 요즘 공부는 어때? 어떤 기분이야?",
    "친구들이나 다른 애들이랑 있을 때 어떤 느낌이야?",
    "요즘 잠은 잘 자? 잠자리는 어때?",
    "학교에서 선생님이나 어른들과 이야기할 때는 어때?",
    "혼자 있을 때 어떤 기분이야? 외롭지 않아?",
    "요즘 우울하거나 슬픈 기분이 자주 들어?",
    "친구들과 놀 때 재미있어? 아니면 힘들어?",
    "공부할 때 집중이 잘 돼? 아니면 어려워?",
    "요즘 많이 울어? 눈물이 자주 나와?",
    "밥은 잘 먹어? 식욕은 어때?",
    "몸이 피곤하거나 아픈 곳 있어?",
    "새로운 일을 시작할 때 두려워?",
    "다른 애들보다 못하다고 생각해?",
    "미래에 대해 걱정이 많아?",
    "가족들과 잘 지내? 집에서 편해?",
    "요즘 스트레스 받는 일이 많아?",
    "기분이 자주 변해? 갑자기 화나거나?",
    "혹시 자해하거나 죽고 싶은 생각 해봤어?",
    "마지막으로, 요즘 가장 힘든 일이 뭐야?",
    "그럼 마지막 질문이야. 앞으로 어떻게 하고 싶어?"
]

class APISession:
    def __init__(self, session_id, user_id=None, test_type="cdi"):
        self.session_id = session_id
        self.user_id = user_id
        self.test_type = test_type
        self.et = EntityTracker()
        self.bow_enc = BoW_encoder()
        self.emb = UtteranceEmbed()
        self.at = ActionTracker(self.et)
        self.similarity_scorer = SimilarityScorer()
        
        # 네트워크 초기화
        obs_size = self.emb.dim + self.bow_enc.vocab_size + self.et.num_features
        self.action_templates = self.at.get_action_templates()
        action_size = self.at.action_size
        nb_hidden = 128
        
        self.net = RNN_GRU_net(obs_size=obs_size,
                               action_size=action_size,
                               nb_hidden=nb_hidden)
        
        # 체크포인트 복원
        self.net.restore()
        
        # 대화 히스토리
        self.conversation_history = []
        
        # 테스트 질문 관리
        self.current_question_index = 0
        self.total_questions = len(TEST_QUESTIONS)
        self.answered_questions = set()
        
        # 데이터베이스 세션 생성
        if user_id:
            self.db_session_id = db.create_test_session(user_id, test_type, self.total_questions)
        else:
            self.db_session_id = None
    
    def process_message(self, user_message):
        """사용자 메시지 처리 (3개 액션 모델 + 20개 질문 관리)"""
        # 이전 시스템 질문 가져오기
        last_system_question = getattr(self, '_last_system_question', None)
        
        # 사용자 의도 분석
        intent = self.similarity_scorer.analyze_user_intent(user_message, last_system_question)
        
        # 응답 생성 및 질문 진행 관리
        response, is_complete = self._handle_conversation_flow(intent, user_message)
        
        # 시스템 질문 저장 (다음 의도 분석을 위해)
        self._last_system_question = response
        
        # 대화 히스토리에 추가
        self.conversation_history.append({
            'user': user_message,
            'system': response,
            'intent': intent,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # 데이터베이스에 응답 저장 (답변 의도인 경우)
        if self.db_session_id and intent == 'answer' and self.current_question_index > 0:
            question_text = TEST_QUESTIONS[self.current_question_index - 1]
            
            # 키워드 추출
            keywords = db.extract_and_update_keywords(self.test_type, str(self.current_question_index), user_message)
            
            # 응답 저장
            response_id = db.save_test_response(
                session_id=self.db_session_id,
                question_id=str(self.current_question_index),
                question_text=question_text,
                user_response=user_message,
                detected_intent=intent,
                calculated_score=0,  # 간단한 점수 계산
                keywords=json.dumps(keywords, ensure_ascii=False)
            )
        
        # 세션 완료 시 데이터베이스 업데이트
        if is_complete and self.db_session_id:
            db.update_test_session(
                self.db_session_id,
                status='completed',
                completed_questions=len(self.answered_questions),
                total_score=len(self.answered_questions),  # 간단한 점수
                completed_at=datetime.now().isoformat()
            )
        
        return {
            'response': response,
            'intent': intent,
            'is_complete': is_complete,
            'diagnosis_result': self._get_diagnosis_result() if is_complete else None
        }
    
    def _handle_conversation_flow(self, intent, user_message):
        """대화 흐름 관리 (3개 액션 + 20개 질문)"""
        if intent == 'greeting':
            # 인사에는 인사로 응답하고 첫 번째 질문으로
            self.current_question_index = 1
            return self.action_templates[0], False
            
        elif intent == 'ready':
            # 준비됨 의도에는 현재 질문 또는 다음 질문으로
            if self.current_question_index == 0:
                self.current_question_index = 1
                return TEST_QUESTIONS[0], False
            elif self.current_question_index < self.total_questions:
                return TEST_QUESTIONS[self.current_question_index - 1], False
            else:
                return self.action_templates[2], True  # 마무리
                
        elif intent == 'answer':
            # 답변 의도에는 답변을 기록하고 다음 질문으로
            if self.current_question_index > 0 and self.current_question_index <= self.total_questions:
                self.answered_questions.add(self.current_question_index)
                
                # 다음 질문으로 진행
                if self.current_question_index < self.total_questions:
                    self.current_question_index += 1
                    return TEST_QUESTIONS[self.current_question_index - 1], False
                else:
                    return self.action_templates[2], True  # 마무리
            else:
                return "죄송해, 다시 말해줄 수 있어?", False
                
        elif intent == 'confused':
            # 혼란 의도에는 다음 질문으로 진행
            if self.current_question_index < self.total_questions:
                self.current_question_index += 1
                return TEST_QUESTIONS[self.current_question_index - 1], False
            else:
                return self.action_templates[2], True  # 마무리
                
        elif intent == 'refuse':
            # 거부 의도에는 종료
            return self.action_templates[2], True
            
        else:
            # 알 수 없는 의도
            return "죄송해, 이해하지 못했어. 다시 말해줄 수 있어?", False
    
    def _extract_features(self, utterance):
        """발화에서 특성 추출 (주관식 평가 포함)"""
        # 엔티티 추출 (유사도 평가 포함)
        u_ent, u_entities = self.et.extract_entities(utterance, is_test=True, similarity_scorer=self.similarity_scorer)
        u_ent_features = self.et.context_features()
        
        # 임베딩
        u_emb = self.emb.encode(utterance)
        u_bow = self.bow_enc.encode(utterance)
        
        # 특성 결합
        features = np.concatenate((u_ent_features, u_emb, u_bow), axis=0)
        
        return features  # numpy 배열로 반환 (GRU_net에서 텐서로 변환)
    
    def _select_action_by_intent(self, intent, user_input):
        """의도에 따른 액션 선택"""
        current_question_index = self.et.entities['current_question_index']
        answered_questions = self.et.entities['answered_questions']
        
        if intent == 'greeting':
            # 인사에는 인사로 응답
            return 0
        elif intent == 'ready':
            # 준비됨 의도에는 다음 질문으로 진행
            if current_question_index == 0:
                return 1  # 첫 번째 질문
            elif current_question_index < 19:  # 20개 질문 (1-19)
                return current_question_index + 1  # 다음 질문
            else:
                return len(self.action_templates) - 1  # 결과 출력
        elif intent == 'answer':
            # 답변 의도에는 답변을 평가하고 다음 질문으로
            # 현재 질문에 대한 평가 항목이 설정되어 있는지 확인
            if self.et.entities['current_evaluation'] and current_question_index not in answered_questions:
                # 답변 평가 수행
                category, subcategory = self.et.entities['current_evaluation']
                score = self.similarity_scorer.calculate_similarity_score(
                    user_input, category, subcategory
                )
                
                # 평가 히스토리에 추가
                evaluation_record = {
                    'category': category,
                    'subcategory': subcategory,
                    'response': user_input,
                    'score': score,
                    'question_index': current_question_index
                }
                self.et.entities['evaluation_history'].append(evaluation_record)
                
                # 점수 업데이트
                if category == 'cdi':
                    if self.et.entities['cdi_score'] is None:
                        self.et.entities['cdi_score'] = 0
                    self.et.entities['cdi_score'] += score
                elif category == 'rcmas':
                    if self.et.entities['rcmas_score'] is None:
                        self.et.entities['rcmas_score'] = 0
                    self.et.entities['rcmas_score'] += score
                elif category == 'bdi':
                    if self.et.entities['bdi_score'] is None:
                        self.et.entities['bdi_score'] = 0
                    self.et.entities['bdi_score'] += score
                
                # 답변한 질문으로 표시
                answered_questions.add(current_question_index)
            
            # 다음 질문으로 진행 (20개 질문)
            if current_question_index < 19:  # 20개 질문 (1-19)
                return current_question_index + 1
            else:
                return len(self.action_templates) - 1  # 결과 출력
        elif intent == 'confused':
            # 혼란 의도에는 다음 질문으로 진행 (반복하지 않음)
            if current_question_index < 19:  # 20개 질문 (1-19)
                return current_question_index + 1
            else:
                return len(self.action_templates) - 1  # 결과 출력
        elif intent == 'refuse':
            # 거부 의도에는 종료
            return len(self.action_templates) - 1
        else:
            # 기본값: 다음 질문으로 진행
            if current_question_index < 3:
                return current_question_index + 1
            else:
                return len(self.action_templates) - 1
    
    def _generate_response(self, prediction):
        """예측된 액션에 따른 응답 생성"""
        if prediction < len(self.action_templates):
            response = self.action_templates[prediction]
            
            # 진단 결과 출력인 경우
            if prediction == len(self.action_templates) - 1:  # 마지막 액션 (결과 출력)
                result = self._get_diagnosis_result()
                response += f"\n\n=== 진단 완료 ===\n"
                response += f"CDI (아동 우울 척도) 점수: {result['cdi_score']}\n"
                response += f"RCMAS (아동 불안 척도) 점수: {result['rcmas_score']}\n"
                response += f"BDI (벡 우울 척도) 점수: {result['bdi_score']}\n\n"
                response += f"각 점수는 해당 영역의 심각도를 나타냅니다.\n"
                response += f"점수가 높을수록 해당 증상이 더 심각할 수 있습니다.\n"
                response += f"※ 이 결과는 참고용이며, 전문적인 진단을 위해서는 전문의와 상담하시기 바랍니다."
            
            return response
        else:
            return "죄송합니다. 이해하지 못했습니다. 다시 말씀해 주세요."
    
    def _is_diagnosis_complete(self):
        """진단 완료 여부 확인 - 20개 질문 모두 답변했는지 확인"""
        return len(self.answered_questions) >= self.total_questions
    
    def _get_diagnosis_result(self):
        """진단 결과 반환"""
        answered_count = len(self.answered_questions)
        return {
            'cdi_score': answered_count,
            'rcmas_score': answered_count,
            'bdi_score': answered_count,
            'interpretation': {
                'cdi': f"총 {answered_count}개 질문에 답변했습니다.",
                'rcmas': f"답변 완료율: {answered_count}/{self.total_questions}",
                'bdi': "테스트가 완료되었습니다."
            }
        }
    
    def reset(self):
        """세션 초기화"""
        self.et = EntityTracker()
        self.at = ActionTracker(self.et)
        self.net.reset_state()
        self.conversation_history = []

# API 엔드포인트들

@app.route('/api/start_session', methods=['POST'])
def start_session():
    """새 세션 시작"""
    data = request.get_json() or {}
    user_id = data.get('user_id')
    test_type = data.get('test_type', 'cdi')
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = APISession(session_id, user_id, test_type)
    
    response_data = {
        'session_id': session_id,
        'message': '새 세션이 시작되었습니다.',
        'welcome_message': '안녕하세요! 아동 및 청소년의 정서 상태를 알아보는 몇 가지 질문을 드릴게요.'
    }
    return Response(
        json.dumps(response_data, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )

@app.route('/api/message', methods=['POST'])
def process_message():
    """메시지 처리"""
    data = request.get_json()
    session_id = data.get('session_id')
    message = data.get('message', '').strip()
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': '유효하지 않은 세션 ID입니다.'}), 400
    
    if not message:
        return jsonify({'error': '메시지가 비어있습니다.'}), 400
    
    session = sessions[session_id]
    result = session.process_message(message)
    
    response_data = {
        'session_id': session_id,
        'response': result['response'],
        'intent': result['intent'],
        'is_complete': result['is_complete'],
        'diagnosis_result': result['diagnosis_result']
    }
    return Response(
        json.dumps(response_data, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )

@app.route('/api/reset_session', methods=['POST'])
def reset_session():
    """세션 초기화"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': '유효하지 않은 세션 ID입니다.'}), 400
    
    sessions[session_id].reset()
    
    return jsonify({
        'session_id': session_id,
        'message': '세션이 초기화되었습니다.'
    })

@app.route('/api/session_history', methods=['GET'])
def get_session_history():
    """세션 히스토리 조회"""
    session_id = request.args.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': '유효하지 않은 세션 ID입니다.'}), 400
    
    session = sessions[session_id]
    
    return jsonify({
        'session_id': session_id,
        'conversation_history': session.conversation_history
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(sessions)
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """시스템 상태 조회"""
    session_id = request.args.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': '유효하지 않은 세션 ID입니다.'}), 400
    
    session = sessions[session_id]
    
    return jsonify({
        'session_id': session_id,
        'is_diagnosis_complete': session._is_diagnosis_complete(),
        'current_scores': {
            'cdi_score': session.et.entities['cdi_score'],
            'rcmas_score': session.et.entities['rcmas_score'],
            'bdi_score': session.et.entities['bdi_score']
        }
    })

# 사용자 인증 관련 API
@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """사용자 회원가입"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': '필수 필드가 누락되었습니다.'}), 400
    
    try:
        user_id = db.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name'),
            role=data.get('role', 'user')
        )
        
        return jsonify({
            'user_id': user_id,
            'message': '회원가입이 완료되었습니다.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    """사용자 로그인"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'error': '사용자명과 비밀번호를 입력해주세요.'}), 400
    
    user = db.authenticate_user(data['username'], data['password'])
    
    if user:
        return jsonify({
            'user': user,
            'message': '로그인 성공'
        })
    else:
        return jsonify({'error': '잘못된 사용자명 또는 비밀번호입니다.'}), 401

# 대시보드 관련 API
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """대시보드 통계 조회"""
    user_id = request.args.get('user_id')
    
    if user_id:
        # 특정 사용자의 통계
        sessions_data = db.get_user_test_sessions(user_id)
        return jsonify({
            'user_sessions': sessions_data,
            'total_sessions': len(sessions_data)
        })
    else:
        # 전체 통계
        dashboard_data = db.get_dashboard_data()
        return jsonify(dashboard_data)

@app.route('/api/dashboard/sessions', methods=['GET'])
def get_user_sessions():
    """사용자 테스트 세션 목록 조회"""
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 50))
    
    if not user_id:
        return jsonify({'error': '사용자 ID가 필요합니다.'}), 400
    
    sessions_data = db.get_user_test_sessions(user_id, limit)
    return jsonify({'sessions': sessions_data})

@app.route('/api/dashboard/session/<session_id>', methods=['GET'])
def get_session_details(session_id):
    """특정 세션 상세 정보 조회"""
    session_data = db.get_test_session(session_id)
    
    if not session_data:
        return jsonify({'error': '세션을 찾을 수 없습니다.'}), 404
    
    responses = db.get_test_responses(session_id)
    
    return jsonify({
        'session': session_data,
        'responses': responses
    })

# 전문가 피드백 관련 API
@app.route('/api/expert/feedback', methods=['POST'])
def submit_expert_feedback():
    """전문가 피드백 제출"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['response_id', 'expert_id', 'feedback_score']):
        return jsonify({'error': '필수 필드가 누락되었습니다.'}), 400
    
    try:
        feedback_id = db.save_expert_feedback(
            response_id=data['response_id'],
            expert_id=data['expert_id'],
            feedback_score=data['feedback_score'],
            feedback_comment=data.get('feedback_comment'),
            keywords_suggested=data.get('keywords_suggested')
        )
        
        return jsonify({
            'feedback_id': feedback_id,
            'message': '피드백이 저장되었습니다.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/expert/feedback/<response_id>', methods=['GET'])
def get_expert_feedback(response_id):
    """응답에 대한 전문가 피드백 조회"""
    feedback_data = db.get_expert_feedback(response_id)
    return jsonify({'feedback': feedback_data})

if __name__ == '__main__':
    print("Flask API 서버를 시작합니다...")
    print("API 엔드포인트:")
    print("=== 세션 관리 ===")
    print("  POST /api/start_session - 새 세션 시작")
    print("  POST /api/message - 메시지 처리")
    print("  POST /api/reset_session - 세션 초기화")
    print("  GET /api/session_history - 세션 히스토리 조회")
    print("  GET /api/status - 세션 상태 조회")
    print("  GET /api/health - 헬스 체크")
    print("=== 사용자 인증 ===")
    print("  POST /api/auth/register - 사용자 회원가입")
    print("  POST /api/auth/login - 사용자 로그인")
    print("=== 대시보드 ===")
    print("  GET /api/dashboard/stats - 대시보드 통계")
    print("  GET /api/dashboard/sessions - 사용자 세션 목록")
    print("  GET /api/dashboard/session/<id> - 세션 상세 정보")
    print("=== 전문가 피드백 ===")
    print("  POST /api/expert/feedback - 전문가 피드백 제출")
    print("  GET /api/expert/feedback/<id> - 피드백 조회")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
