# -*- coding: utf-8 -*-
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import ollama
import json
import uuid
from datetime import datetime
from database import db
from modules.similarity_scorer import SimilarityScorer

app = Flask(__name__)
CORS(app)

# JSON 인코딩 설정 - 한글 유니코드 이스케이프 방지
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# 전역 변수로 세션 관리
similarity_scorer = SimilarityScorer()
sessions = {}

# 트리거 키워드 (진단 테스트 시작 조건)
TRIGGER_KEYWORDS = [
    '우울', '슬프', '힘들', '어려', '걱정', '불안', '스트레스', '피곤', '외로',
    '자살', '죽고', '끝내', '포기', '의미없', '희망없', '절망', '괴로', '고통'
]

# 3가지 테스트 질문 (각 20개)
TEST_QUESTIONS = {
    'cdi': [
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
    ],
    'rcmas': [
        "새로운 상황에 들어갈 때 얼마나 긴장돼?",
        "다른 사람들이 너를 어떻게 생각하는지 걱정돼?",
        "시험을 볼 때 얼마나 불안해?",
        "새로운 친구를 사귈 때 어려워?",
        "선생님 앞에서 발표할 때 떨려?",
        "다른 애들보다 못하다고 생각해?",
        "실수를 하면 얼마나 부끄러워?",
        "새로운 일을 시작할 때 두려워?",
        "다른 사람들이 너를 비웃을까 걱정돼?",
        "혼자 있을 때 불안해?",
        "새로운 환경에 적응하기 어려워?",
        "다른 사람들과 비교될 때 스트레스받아?",
        "실패할까봐 걱정돼?",
        "다른 사람들의 시선이 부담스러워?",
        "새로운 도전을 피하고 싶어?",
        "다른 사람들이 너를 어떻게 볼지 걱정돼?",
        "새로운 사람들과 만날 때 어색해?",
        "다른 애들보다 뒤처질까 걱정돼?",
        "새로운 상황에서 실수할까봐 두려워?",
        "마지막으로, 가장 불안한 상황이 뭐야?"
    ],
    'bdi': [
        "요즘 기분이 어떤가?",
        "미래에 대해 어떻게 생각해?",
        "실패했다고 느낄 때가 있어?",
        "만족스럽지 않은 일이 많아?",
        "죄책감을 느낄 때가 있어?",
        "벌을 받을 것 같다고 생각해?",
        "자신에 대해 실망해?",
        "자신을 비난할 때가 있어?",
        "자살에 대해 생각해본 적 있어?",
        "요즘 많이 울어?",
        "짜증이 자주 나?",
        "다른 사람들에게 관심이 없어?",
        "결정하기 어려워?",
        "자신이 못생겼다고 생각해?",
        "일하기 어려워?",
        "잠을 잘 못 자?",
        "피곤해?",
        "식욕이 없어?",
        "몸무게가 많이 변했어?",
        "건강에 대해 걱정돼?"
    ]
}

class ConversationSession:
    def __init__(self, session_id, user_id=None):
        self.session_id = session_id
        self.user_id = user_id
        self.conversation_history = []
        self.current_mode = 'chat'  # 'chat' 또는 'test'
        self.current_test = None  # 'cdi', 'rcmas', 'bdi'
        self.current_question_index = 0
        self.test_results = {}
        self.db_session_id = None
        
    def detect_trigger(self, user_message):
        """트리거 키워드 감지"""
        user_message_lower = user_message.lower()
        for keyword in TRIGGER_KEYWORDS:
            if keyword in user_message_lower:
                return True
        return False
    
    def _get_subcategory_for_question(self, test_type, question_index):
        """질문 인덱스를 적절한 subcategory로 매핑"""
        if test_type == 'cdi':
            subcategories = [
                'academic_achievement', 'social_interaction', 'sleep_problems', 'adult_interaction',
                'loneliness', 'depression', 'social_interaction', 'academic_achievement', 'crying',
                'appetite', 'fatigue', 'academic_achievement', 'academic_achievement', 'friendship',
                'fatigue', 'crying', 'crying', 'fatigue', 'fatigue', 'fatigue'
            ]
        elif test_type == 'rcmas':
            subcategories = [
                'anxiety', 'social_anxiety', 'anxiety', 'social_anxiety', 'anxiety',
                'self_esteem', 'anxiety', 'anxiety', 'social_anxiety', 'anxiety',
                'anxiety', 'self_esteem', 'anxiety', 'social_anxiety', 'anxiety',
                'social_anxiety', 'social_anxiety', 'anxiety', 'anxiety', 'anxiety'
            ]
        elif test_type == 'bdi':
            subcategories = [
                'sleep_pattern', 'sleep_pattern', 'sleep_pattern', 'sleep_pattern', 'sleep_pattern',
                'sleep_pattern', 'sleep_pattern', 'sleep_pattern', 'sleep_pattern', 'sleep_pattern',
                'sleep_pattern', 'sleep_pattern', 'sleep_pattern', 'appearance', 'sleep_pattern',
                'sleep_pattern', 'sleep_pattern', 'weight_change', 'weight_change', 'sleep_pattern'
            ]
        else:
            return 'general'
        
        if question_index < len(subcategories):
            return subcategories[question_index]
        return 'general'
    
    def start_test(self, test_type):
        """진단 테스트 시작"""
        self.current_mode = 'test'
        self.current_test = test_type
        self.current_question_index = 0
        
        # 데이터베이스 세션 생성
        if self.user_id:
            self.db_session_id = db.create_test_session(
                self.user_id, test_type, len(TEST_QUESTIONS[test_type])
            )
        
        return TEST_QUESTIONS[test_type][0]
    
    def process_test_response(self, user_message):
        """테스트 응답 처리"""
        if self.current_test is None:
            return "테스트가 시작되지 않았습니다.", False
        
        # 현재 질문에 대한 응답 저장
        if self.db_session_id:
            question_text = TEST_QUESTIONS[self.current_test][self.current_question_index]
            keywords = db.extract_and_update_keywords(
                self.current_test, str(self.current_question_index), user_message
            )
            
            # 실제 점수 계산 - 질문 ID를 적절한 subcategory로 매핑
            subcategory = self._get_subcategory_for_question(self.current_test, self.current_question_index)
            calculated_score = similarity_scorer.calculate_similarity_score(
                user_message, self.current_test, subcategory
            )
            
            # 테스트 타입에 따른 그룹과 카테고리 설정
            test_group_mapping = {
                'cdi': (1, 'CDI'),
                'rcmas': (2, 'RCMAS'),
                'bdi': (3, 'BDI')
            }
            question_group, question_category = test_group_mapping.get(self.current_test, (1, 'UNKNOWN'))
            
            db.save_test_response(
                session_id=self.db_session_id,
                question_id=str(self.current_question_index),
                question_text=question_text,
                user_response=user_message,
                detected_intent='answer',
                calculated_score=calculated_score,
                keywords=json.dumps(keywords, ensure_ascii=False),
                question_group=question_group,
                question_category=question_category
            )
        
        # 다음 질문으로 진행
        self.current_question_index += 1
        
        # 진행률 업데이트
        if self.db_session_id:
            db.update_test_session(
                self.db_session_id,
                status='in_progress',
                completed_questions=self.current_question_index,
                total_score=self.current_question_index
            )
        
        if self.current_question_index < len(TEST_QUESTIONS[self.current_test]):
            return TEST_QUESTIONS[self.current_test][self.current_question_index], False
        else:
            # 테스트 완료
            self.test_results[self.current_test] = {
                'completed': True,
                'total_questions': len(TEST_QUESTIONS[self.current_test])
            }
            
            # 데이터베이스 업데이트
            if self.db_session_id:
                db.update_test_session(
                    self.db_session_id,
                    status='completed',
                    completed_questions=len(TEST_QUESTIONS[self.current_test]),
                    total_score=len(TEST_QUESTIONS[self.current_test]),
                    completed_at=datetime.now().isoformat()
                )
            
            # 다음 테스트 확인
            if self.current_test == 'cdi':
                self.current_test = 'rcmas'
                self.current_question_index = 0
                return f"CDI 테스트가 완료되었습니다. 이제 RCMAS 테스트를 시작할게요.\n\n{TEST_QUESTIONS['rcmas'][0]}", False
            elif self.current_test == 'rcmas':
                self.current_test = 'bdi'
                self.current_question_index = 0
                return f"RCMAS 테스트가 완료되었습니다. 이제 BDI 테스트를 시작할게요.\n\n{TEST_QUESTIONS['bdi'][0]}", False
            else:
                # 모든 테스트 완료
                self.current_mode = 'chat'
                self.current_test = None
                return "모든 진단 테스트가 완료되었습니다. 대화를 계속할 수 있어요.", True

def get_chat_response(user_message, conversation_history):
    """Gemma3:27b를 사용한 일반 대화 응답"""
    try:
        # 대화 히스토리 구성
        messages = [
            {
                'role': 'system',
                'content': '당신은 친근하고 공감적인 10대 청소년 상담사입니다. 자연스럽고 따뜻하게 대화하세요.'
            }
        ]
        
        # 최근 대화 히스토리 추가 (최대 10개)
        for msg in conversation_history[-10:]:
            messages.append({
                'role': 'user' if msg['type'] == 'user' else 'assistant',
                'content': msg['content']
            })
        
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        response = ollama.chat(
            model='gemma2:2b',
            messages=messages,
            options={
                'temperature': 0.7,
                'top_p': 0.9
            }
        )
        
        return response['message']['content']
        
    except Exception as e:
        print(f"대화 응답 생성 오류: {e}")
        return "죄송해, 지금 응답하기 어려워. 다시 말해줄 수 있어?"

@app.route('/api/start_session', methods=['POST'])
def start_session():
    """새 세션 시작"""
    data = request.get_json() or {}
    user_id = data.get('user_id')
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = ConversationSession(session_id, user_id)
    
    response_data = {
        'session_id': session_id,
        'message': '새 세션이 시작되었습니다.',
        'welcome_message': '안녕! 오늘 기분은 어때? 편하게 이야기해보자.'
    }
    return Response(
        json.dumps(response_data, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )

@app.route('/api/message', methods=['POST'])
def process_message():
    """메시지 처리"""
    data = request.get_json()
    
    if not data or 'session_id' not in data or 'message' not in data:
        return jsonify({'error': '세션 ID와 메시지가 필요합니다.'}), 400
    
    session_id = data['session_id']
    user_message = data['message']
    
    if session_id not in sessions:
        return jsonify({'error': '유효하지 않은 세션 ID입니다.'}), 400
    
    session = sessions[session_id]
    
    # 대화 히스토리에 사용자 메시지 추가
    session.conversation_history.append({
        'type': 'user',
        'content': user_message,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    if session.current_mode == 'chat':
        # 일반 대화 모드
        if session.detect_trigger(user_message):
            # 트리거 감지 - CDI 테스트 시작
            response = session.start_test('cdi')
            session.conversation_history.append({
                'type': 'assistant',
                'content': response,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            return Response(
                json.dumps({
                    'session_id': session_id,
                    'response': response,
                    'intent': 'test_start',
                    'is_complete': False,
                    'diagnosis_result': None
                }, ensure_ascii=False),
                mimetype='application/json; charset=utf-8'
            )
        else:
            # 일반 대화
            response = get_chat_response(user_message, session.conversation_history)
            session.conversation_history.append({
                'type': 'assistant',
                'content': response,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            return Response(
                json.dumps({
                    'session_id': session_id,
                    'response': response,
                    'intent': 'chat',
                    'is_complete': False,
                    'diagnosis_result': None
                }, ensure_ascii=False),
                mimetype='application/json; charset=utf-8'
            )
    
    else:
        # 테스트 모드
        response, is_complete = session.process_test_response(user_message)
        session.conversation_history.append({
            'type': 'assistant',
            'content': response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        diagnosis_result = None
        if is_complete:
            diagnosis_result = {
                'cdi_score': session.test_results.get('cdi', {}).get('total_questions', 0),
                'rcmas_score': session.test_results.get('rcmas', {}).get('total_questions', 0),
                'bdi_score': session.test_results.get('bdi', {}).get('total_questions', 0),
                'interpretation': {
                    'cdi': f"CDI 테스트 완료: {session.test_results.get('cdi', {}).get('total_questions', 0)}개 질문",
                    'rcmas': f"RCMAS 테스트 완료: {session.test_results.get('rcmas', {}).get('total_questions', 0)}개 질문",
                    'bdi': f"BDI 테스트 완료: {session.test_results.get('bdi', {}).get('total_questions', 0)}개 질문"
                }
            }
        
        return Response(
            json.dumps({
                'session_id': session_id,
                'response': response,
                'intent': 'test',
                'is_complete': is_complete,
                'diagnosis_result': diagnosis_result
            }, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(sessions)
    })

# 사용자 인증 API
@app.route('/api/auth/register', methods=['POST'])
def register():
    """사용자 회원가입"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': '사용자명, 이메일, 비밀번호가 필요합니다.'}), 400
    
    try:
        user_id = db.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name', ''),
            role='user'
        )
        
        return jsonify({
            'message': '회원가입이 완료되었습니다.',
            'user_id': user_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    """사용자 로그인"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': '이메일과 비밀번호가 필요합니다.'}), 400
    
    try:
        user = db.authenticate_user(data['email'], data['password'])
        if user:
            return jsonify({
                'message': '로그인 성공',
                'user': user
            })
        else:
            return jsonify({'error': '이메일 또는 비밀번호가 올바르지 않습니다.'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 대시보드 API
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """대시보드 통계"""
    try:
        stats = db.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/sessions', methods=['GET'])
def get_user_sessions():
    """사용자 세션 목록"""
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 50))
    
    if not user_id:
        return jsonify({'error': '사용자 ID가 필요합니다.'}), 400
    
    try:
        sessions_data = db.get_user_sessions(user_id, limit)
        return jsonify(sessions_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/all-sessions', methods=['GET'])
def get_all_sessions():
    """모든 사용자의 세션 조회 (관리자/전문가용)"""
    try:
        limit = int(request.args.get('limit', 100))
        all_sessions = db.get_all_sessions(limit)
        return jsonify(all_sessions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/progress/<user_id>', methods=['GET'])
def get_user_progress(user_id):
    """사용자별 통합 진행률 조회"""
    try:
        progress_data = db.get_user_progress_summary(user_id)
        return jsonify(progress_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/all-users-progress', methods=['GET'])
def get_all_users_progress():
    """모든 사용자의 진행률 조회 (관리자용)"""
    try:
        # 관리자 권한 확인 (실제로는 JWT 토큰이나 세션에서 확인해야 함)
        # 여기서는 간단히 구현
        users_progress = db.get_all_users_progress()
        return jsonify({
            'users': users_progress,
            'total_users': len(users_progress)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/session/<session_id>', methods=['GET'])
def get_session_detail(session_id):
    """세션 상세 정보"""
    try:
        session_data = db.get_session_detail(session_id)
        if session_data:
            return jsonify(session_data)
        else:
            return jsonify({'error': '세션을 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/session/<session_id>/grouped-scores', methods=['GET'])
def get_session_grouped_scores(session_id):
    """세션별 그룹 점수 조회"""
    try:
        grouped_scores = db.get_session_grouped_scores(session_id)
        return jsonify(grouped_scores)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 전문가 점수 API
@app.route('/api/expert/score/<response_id>', methods=['PUT'])
def update_expert_score(response_id):
    """전문가 점수 업데이트"""
    data = request.get_json()
    
    if not data or 'score' not in data:
        return jsonify({'error': '점수가 필요합니다.'}), 400
    
    try:
        score = float(data['score'])
        if score < 0 or score > 5:
            return jsonify({'error': '점수는 0-5 사이의 값이어야 합니다.'}), 400
        
        success = db.update_expert_score(response_id, score)
        if success:
            return jsonify({'message': '전문가 점수가 업데이트되었습니다.'})
        else:
            return jsonify({'error': '응답을 찾을 수 없습니다.'}), 404
    except ValueError:
        return jsonify({'error': '유효하지 않은 점수 형식입니다.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Flask API 서버를 시작합니다...")
    print("API 엔드포인트:")
    print("=== 세션 관리 ===")
    print("  POST /api/start_session - 새 세션 시작")
    print("  POST /api/message - 메시지 처리")
    print("  GET /api/health - 헬스 체크")
    print("=== 사용자 인증 ===")
    print("  POST /api/auth/register - 사용자 회원가입")
    print("  POST /api/auth/login - 사용자 로그인")
    print("=== 대시보드 ===")
    print("  GET /api/dashboard/stats - 대시보드 통계")
    print("  GET /api/dashboard/sessions - 사용자 세션 목록")
    print("  GET /api/dashboard/session/<id> - 세션 상세 정보")
    print("  GET /api/dashboard/session/<id>/grouped-scores - 세션 그룹별 점수")
    print("=== 전문가 점수 ===")
    print("  PUT /api/expert/score/<response_id> - 전문가 점수 업데이트")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
