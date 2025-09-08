# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
from modules.entities import EntityTracker
from modules.bow import BoW_encoder
from modules.rnn_gru_net import RNN_GRU_net
from modules.embed import UtteranceEmbed
from modules.actions import ActionTracker
from modules.similarity_scorer import SimilarityScorer
import modules.util as util
import numpy as np
import torch
import uuid
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# JSON 응답에서 한글 유니코드 이스케이프 방지
app.config['JSON_AS_ASCII'] = False

# 전역 변수로 세션 관리
sessions = {}

class APISession:
    def __init__(self, session_id):
        self.session_id = session_id
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
    
    def process_message(self, user_message):
        """사용자 메시지 처리 (의도 분석 포함)"""
        # 이전 시스템 질문 가져오기
        last_system_question = getattr(self, '_last_system_question', None)
        
        # 사용자 의도 분석 (Ollama 기반, 시스템 질문 맥락 포함)
        intent = self.similarity_scorer.analyze_user_intent(user_message, last_system_question)
        
        # 의도에 따른 액션 선택
        prediction = self._select_action_by_intent(intent, user_message)
        
        # 현재 질문에 대한 평가 항목 설정
        self.at.set_current_evaluation(prediction)
        
        # 응답 생성
        response = self._generate_response(prediction)
        
        # 시스템 질문 저장 (다음 의도 분석을 위해)
        self._last_system_question = response
        
        # 대화 히스토리에 추가
        self.conversation_history.append({
            'user': user_message,
            'system': response,
            'intent': intent,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # 진단 완료 여부 확인
        is_complete = self._is_diagnosis_complete()
        
        return {
            'response': response,
            'intent': intent,
            'is_complete': is_complete,
            'diagnosis_result': self._get_diagnosis_result() if is_complete else None
        }
    
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
                return 1  # 첫 번째 CDI 질문
            elif current_question_index < 3:
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
            
            # 다음 질문으로 진행 (3개 질문만)
            if current_question_index < 3:
                return current_question_index + 1
            else:
                return len(self.action_templates) - 1  # 결과 출력
        elif intent == 'confused':
            # 혼란 의도에는 현재 질문 반복
            if current_question_index == 0:
                return 1  # 첫 번째 질문
            else:
                return min(current_question_index, len(self.action_templates) - 2)
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
        """진단 완료 여부 확인"""
        return (self.et.entities['cdi_score'] is not None and 
                self.et.entities['rcmas_score'] is not None and 
                self.et.entities['bdi_score'] is not None)
    
    def _get_diagnosis_result(self):
        """진단 결과 반환"""
        return {
            'cdi_score': self.et.entities['cdi_score'] or 0,
            'rcmas_score': self.et.entities['rcmas_score'] or 0,
            'bdi_score': self.et.entities['bdi_score'] or 0,
            'interpretation': {
                'cdi': util._interpret_cdi_score(self.et.entities['cdi_score']),
                'rcmas': util._interpret_rcmas_score(self.et.entities['rcmas_score']),
                'bdi': util._interpret_bdi_score(self.et.entities['bdi_score'])
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
    session_id = str(uuid.uuid4())
    sessions[session_id] = APISession(session_id)
    
    return jsonify({
        'session_id': session_id,
        'message': '새 세션이 시작되었습니다.',
        'welcome_message': '안녕하세요! 아동 및 청소년의 정서 상태를 알아보는 몇 가지 질문을 드릴게요.'
    })

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
    
    return jsonify({
        'session_id': session_id,
        'response': result['response'],
        'intent': result['intent'],
        'is_complete': result['is_complete'],
        'diagnosis_result': result['diagnosis_result']
    })

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

if __name__ == '__main__':
    print("Flask API 서버를 시작합니다...")
    print("API 엔드포인트:")
    print("  POST /api/start_session - 새 세션 시작")
    print("  POST /api/message - 메시지 처리")
    print("  POST /api/reset_session - 세션 초기화")
    print("  GET /api/session_history - 세션 히스토리 조회")
    print("  GET /api/status - 세션 상태 조회")
    print("  GET /api/health - 헬스 체크")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
