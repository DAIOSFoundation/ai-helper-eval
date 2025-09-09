"""
AI Helper Evaluation System - Database Module
SQLite 데이터베이스를 사용한 사용자 계정 및 테스트 히스토리 관리
"""

import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
import hashlib
import os

class DatabaseManager:
    def __init__(self, db_path: str = "ai_helper_eval.db"):
        """데이터베이스 매니저 초기화"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 테이블 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 사용자 계정 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 테스트 세션 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    test_type TEXT NOT NULL,
                    status TEXT DEFAULT 'in_progress',
                    total_questions INTEGER DEFAULT 0,
                    completed_questions INTEGER DEFAULT 0,
                    total_score REAL DEFAULT 0.0,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # 테스트 문항 응답 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_responses (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    user_response TEXT NOT NULL,
                    detected_intent TEXT,
                    calculated_score REAL,
                    expert_score REAL,
                    keywords TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES test_sessions (id)
                )
            """)
            
            # 전문가 피드백 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expert_feedback (
                    id TEXT PRIMARY KEY,
                    response_id TEXT NOT NULL,
                    expert_id TEXT NOT NULL,
                    feedback_score REAL NOT NULL,
                    feedback_comment TEXT,
                    keywords_suggested TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (response_id) REFERENCES test_responses (id),
                    FOREIGN KEY (expert_id) REFERENCES users (id)
                )
            """)
            
            # 평가 템플릿 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluation_templates (
                    id TEXT PRIMARY KEY,
                    test_type TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    weights TEXT,
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 키워드 추출 히스토리 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS keyword_extraction_history (
                    id TEXT PRIMARY KEY,
                    test_type TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    extracted_keywords TEXT NOT NULL,
                    frequency_count INTEGER DEFAULT 1,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_type, question_id) REFERENCES evaluation_templates (test_type, question_id)
                )
            """)
            
            conn.commit()
    
    def hash_password(self, password: str) -> str:
        """비밀번호 해시화"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, full_name: str = None, role: str = "user") -> str:
        """새 사용자 생성"""
        user_id = str(uuid.uuid4())
        password_hash = self.hash_password(password)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, full_name, role)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, email, password_hash, full_name, role))
            conn.commit()
        
        return user_id
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """사용자 인증"""
        password_hash = self.hash_password(password)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email, full_name, role, created_at
                FROM users
                WHERE email = ? AND password_hash = ?
            """, (email, password_hash))
            
            user = cursor.fetchone()
            if user:
                return dict(user)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """사용자 ID로 사용자 정보 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email, full_name, role, created_at
                FROM users
                WHERE id = ?
            """, (user_id,))
            
            user = cursor.fetchone()
            if user:
                return dict(user)
        return None
    
    def create_test_session(self, user_id: str, test_type: str, total_questions: int = 0) -> str:
        """새 테스트 세션 생성"""
        session_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO test_sessions (id, user_id, test_type, total_questions)
                VALUES (?, ?, ?, ?)
            """, (session_id, user_id, test_type, total_questions))
            conn.commit()
        
        return session_id
    
    def update_test_session(self, session_id: str, **kwargs) -> bool:
        """테스트 세션 업데이트"""
        allowed_fields = ['status', 'completed_questions', 'total_score', 'completed_at']
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        values.append(session_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE test_sessions
                SET {', '.join(updates)}
                WHERE id = ?
            """, values)
            conn.commit()
            return cursor.rowcount > 0
    
    def get_test_session(self, session_id: str) -> Optional[Dict]:
        """테스트 세션 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_sessions WHERE id = ?
            """, (session_id,))
            
            session = cursor.fetchone()
            if session:
                return dict(session)
        return None
    
    def get_user_test_sessions(self, user_id: str, limit: int = 50) -> List[Dict]:
        """사용자의 테스트 세션 목록 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_sessions
                WHERE user_id = ?
                ORDER BY started_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def save_test_response(self, session_id: str, question_id: str, question_text: str, 
                          user_response: str, detected_intent: str = None, 
                          calculated_score: float = None, keywords: str = None,
                          question_group: int = None, question_category: str = None) -> str:
        """테스트 응답 저장"""
        response_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO test_responses 
                (id, session_id, question_id, question_text, user_response, 
                 detected_intent, calculated_score, keywords, question_group, question_category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (response_id, session_id, question_id, question_text, user_response,
                  detected_intent, calculated_score, keywords, question_group, question_category))
            conn.commit()
        
        return response_id
    
    def get_test_responses(self, session_id: str) -> List[Dict]:
        """테스트 세션의 모든 응답 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_responses
                WHERE session_id = ?
                ORDER BY created_at ASC
            """, (session_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def save_expert_feedback(self, response_id: str, expert_id: str, 
                           feedback_score: float, feedback_comment: str = None,
                           keywords_suggested: str = None) -> str:
        """전문가 피드백 저장"""
        feedback_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO expert_feedback
                (id, response_id, expert_id, feedback_score, feedback_comment, keywords_suggested)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (feedback_id, response_id, expert_id, feedback_score, feedback_comment, keywords_suggested))
            
            # 응답 테이블의 expert_score 업데이트
            cursor.execute("""
                UPDATE test_responses
                SET expert_score = ?
                WHERE id = ?
            """, (feedback_score, response_id))
            
            conn.commit()
        
        return feedback_id
    
    def get_expert_feedback(self, response_id: str) -> List[Dict]:
        """응답에 대한 전문가 피드백 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ef.*, u.username as expert_username
                FROM expert_feedback ef
                JOIN users u ON ef.expert_id = u.id
                WHERE ef.response_id = ?
                ORDER BY ef.created_at DESC
            """, (response_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_evaluation_template(self, test_type: str, question_id: str, 
                                 keywords: str, weights: str = None) -> str:
        """평가 템플릿 업데이트"""
        template_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 기존 템플릿 버전 확인
            cursor.execute("""
                SELECT MAX(version) FROM evaluation_templates
                WHERE test_type = ? AND question_id = ?
            """, (test_type, question_id))
            
            result = cursor.fetchone()
            version = (result[0] or 0) + 1
            
            cursor.execute("""
                INSERT INTO evaluation_templates
                (id, test_type, question_id, keywords, weights, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (template_id, test_type, question_id, keywords, weights, version))
            
            conn.commit()
        
        return template_id
    
    def get_evaluation_template(self, test_type: str, question_id: str) -> Optional[Dict]:
        """평가 템플릿 조회 (최신 버전)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM evaluation_templates
                WHERE test_type = ? AND question_id = ?
                ORDER BY version DESC
                LIMIT 1
            """, (test_type, question_id))
            
            template = cursor.fetchone()
            if template:
                return dict(template)
        return None
    
    def extract_and_update_keywords(self, test_type: str, question_id: str, 
                                   user_response: str) -> List[str]:
        """사용자 응답에서 키워드 추출 및 업데이트"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 처리 필요)
        import re
        keywords = re.findall(r'\b\w+\b', user_response.lower())
        
        # 불용어 제거 (간단한 예시)
        stop_words = {'은', '는', '이', '가', '을', '를', '에', '의', '로', '으로', '와', '과', '도', '만', '부터', '까지'}
        keywords = [kw for kw in keywords if kw not in stop_words and len(kw) > 1]
        
        # 키워드 빈도 업데이트
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for keyword in keywords:
                cursor.execute("""
                    INSERT OR REPLACE INTO keyword_extraction_history
                    (id, test_type, question_id, extracted_keywords, frequency_count, last_updated)
                    VALUES (?, ?, ?, ?, 
                        COALESCE((SELECT frequency_count FROM keyword_extraction_history 
                                 WHERE test_type = ? AND question_id = ? AND extracted_keywords = ?), 0) + 1,
                        CURRENT_TIMESTAMP)
                """, (str(uuid.uuid4()), test_type, question_id, keyword, test_type, question_id, keyword))
            
            conn.commit()
        
        return keywords
    
    def get_dashboard_data(self, user_id: str = None) -> Dict:
        """대시보드용 데이터 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 전체 통계
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT ts.id) as total_sessions,
                    COUNT(DISTINCT ts.user_id) as total_users,
                    AVG(ts.total_score) as avg_score,
                    COUNT(DISTINCT tr.id) as total_responses
                FROM test_sessions ts
                LEFT JOIN test_responses tr ON ts.id = tr.session_id
            """)
            overall_stats = dict(cursor.fetchone())
            
            # 테스트 타입별 통계
            cursor.execute("""
                SELECT 
                    test_type,
                    COUNT(*) as session_count,
                    AVG(total_score) as avg_score,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count
                FROM test_sessions
                GROUP BY test_type
            """)
            test_type_stats = [dict(row) for row in cursor.fetchall()]
            
            # 최근 세션들 (회차 정보 포함)
            cursor.execute("""
                SELECT 
                    ts.*, 
                    u.username, 
                    u.full_name,
                    ROW_NUMBER() OVER (
                        PARTITION BY ts.user_id, ts.test_type 
                        ORDER BY ts.started_at ASC
                    ) as session_round
                FROM test_sessions ts
                JOIN users u ON ts.user_id = u.id
                ORDER BY ts.started_at DESC
                LIMIT 10
            """)
            recent_sessions = [dict(row) for row in cursor.fetchall()]
            
            return {
                'overall_stats': overall_stats,
                'test_type_stats': test_type_stats,
                'recent_sessions': recent_sessions
            }
    
    def get_dashboard_stats(self) -> Dict:
        """대시보드 통계 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 전체 통계
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT ts.id) as total_sessions,
                    COUNT(DISTINCT ts.user_id) as total_users,
                    AVG(ts.total_score) as avg_score,
                    COUNT(tr.id) as total_responses
                FROM test_sessions ts
                LEFT JOIN test_responses tr ON ts.id = tr.session_id
            """)
            overall_stats = dict(cursor.fetchone())
            
            # 테스트 타입별 통계
            cursor.execute("""
                SELECT 
                    test_type,
                    COUNT(*) as session_count,
                    AVG(total_score) as avg_score,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count
                FROM test_sessions
                GROUP BY test_type
            """)
            test_type_stats = [dict(row) for row in cursor.fetchall()]
            
            # 최근 세션들 (회차 정보 포함)
            cursor.execute("""
                SELECT 
                    ts.*, 
                    u.username, 
                    u.full_name,
                    ROW_NUMBER() OVER (
                        PARTITION BY ts.user_id, ts.test_type 
                        ORDER BY ts.started_at ASC
                    ) as session_round
                FROM test_sessions ts
                JOIN users u ON ts.user_id = u.id
                ORDER BY ts.started_at DESC
                LIMIT 10
            """)
            recent_sessions = [dict(row) for row in cursor.fetchall()]
            
            return {
                'overall_stats': overall_stats,
                'test_type_stats': test_type_stats,
                'recent_sessions': recent_sessions
            }
    
    def get_user_sessions(self, user_id: str, limit: int = 50) -> List[Dict]:
        """사용자의 세션 목록 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    ts.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY ts.user_id, ts.test_type 
                        ORDER BY ts.started_at ASC
                    ) as session_round
                FROM test_sessions ts
                WHERE ts.user_id = ?
                ORDER BY ts.started_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_sessions(self, limit: int = 100) -> List[Dict]:
        """모든 사용자의 세션 목록 조회 (관리자/전문가용)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ts.*, u.username, u.email, u.full_name
                FROM test_sessions ts
                JOIN users u ON ts.user_id = u.id
                ORDER BY ts.started_at DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_progress_summary(self, user_id: str) -> Dict:
        """사용자의 전체 테스트 진행률 요약"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 각 테스트 타입별 진행률 계산
            cursor.execute("""
                SELECT 
                    test_type,
                    COUNT(*) as total_sessions,
                    SUM(completed_questions) as total_completed_questions,
                    SUM(total_questions) as total_questions,
                    MAX(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as is_completed,
                    MAX(started_at) as last_activity
                FROM test_sessions
                WHERE user_id = ?
                GROUP BY test_type
            """, (user_id,))
            
            test_progress = {}
            total_completed = 0
            total_questions = 0
            
            for row in cursor.fetchall():
                test_type = row['test_type']
                completed = row['total_completed_questions'] or 0
                questions = row['total_questions'] or 0
                
                test_progress[test_type] = {
                    'completed_questions': completed,
                    'total_questions': questions,
                    'progress_percentage': (completed / questions * 100) if questions > 0 else 0,
                    'is_completed': bool(row['is_completed']),
                    'last_activity': row['last_activity']
                }
                
                total_completed += completed
                total_questions += questions
            
            # 전체 진행률 계산
            overall_progress = (total_completed / total_questions * 100) if total_questions > 0 else 0
            
            return {
                'user_id': user_id,
                'overall_progress': {
                    'completed_questions': total_completed,
                    'total_questions': total_questions,
                    'progress_percentage': overall_progress
                },
                'test_progress': test_progress
            }
    
    def get_all_users_progress(self) -> List[Dict]:
        """모든 사용자의 진행률 조회 (관리자용)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 모든 사용자 조회
            cursor.execute("""
                SELECT id, username, email, full_name, role, created_at
                FROM users
                WHERE role != 'admin'
                ORDER BY created_at DESC
            """)
            
            users = [dict(row) for row in cursor.fetchall()]
            
            # 각 사용자별 진행률 계산
            for user in users:
                user_id = user['id']
                
                # 각 테스트 타입별 진행률 계산
                cursor.execute("""
                    SELECT 
                        test_type,
                        COUNT(*) as total_sessions,
                        SUM(completed_questions) as total_completed_questions,
                        SUM(total_questions) as total_questions,
                        MAX(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as is_completed,
                        MAX(started_at) as last_activity
                    FROM test_sessions
                    WHERE user_id = ?
                    GROUP BY test_type
                """, (user_id,))
                
                test_progress = {}
                total_completed = 0
                total_questions = 0
                
                for row in cursor.fetchall():
                    test_type = row['test_type']
                    completed = row['total_completed_questions'] or 0
                    questions = row['total_questions'] or 0
                    
                    test_progress[test_type] = {
                        'completed_questions': completed,
                        'total_questions': questions,
                        'progress_percentage': (completed / questions * 100) if questions > 0 else 0,
                        'is_completed': bool(row['is_completed']),
                        'last_activity': row['last_activity']
                    }
                    
                    total_completed += completed
                    total_questions += questions
                
                # 전체 진행률 계산
                overall_progress = (total_completed / total_questions * 100) if total_questions > 0 else 0
                
                user['progress'] = {
                    'overall_progress': {
                        'completed_questions': total_completed,
                        'total_questions': total_questions,
                        'progress_percentage': overall_progress
                    },
                    'test_progress': test_progress
                }
            
            return users
    
    def get_session_detail(self, session_id: str) -> Optional[Dict]:
        """세션 상세 정보 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 세션 정보
            cursor.execute("""
                SELECT ts.*, u.username, u.full_name
                FROM test_sessions ts
                JOIN users u ON ts.user_id = u.id
                WHERE ts.id = ?
            """, (session_id,))
            
            session = cursor.fetchone()
            if not session:
                return None
            
            session_dict = dict(session)
            
            # 세션의 응답들
            cursor.execute("""
                SELECT * FROM test_responses
                WHERE session_id = ?
                ORDER BY created_at ASC
            """, (session_id,))
            
            responses = [dict(row) for row in cursor.fetchall()]
            session_dict['responses'] = responses
            
            # 전문가 피드백 (response_id를 통해 조인)
            cursor.execute("""
                SELECT ef.*, tr.session_id
                FROM expert_feedback ef
                JOIN test_responses tr ON ef.response_id = tr.id
                WHERE tr.session_id = ?
                ORDER BY ef.created_at DESC
            """, (session_id,))
            
            feedback = [dict(row) for row in cursor.fetchall()]
            session_dict['expert_feedback'] = feedback
            
            return session_dict
    
    def create_expert_feedback(self, session_id: str, expert_name: str, 
                              feedback: str, recommendations: str = '', 
                              severity_level: str = 'medium') -> str:
        """전문가 피드백 생성"""
        feedback_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO expert_feedback (
                    id, session_id, expert_name, feedback, 
                    recommendations, severity_level, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (feedback_id, session_id, expert_name, feedback, 
                  recommendations, severity_level, datetime.now().isoformat()))
            
            conn.commit()
        
        return feedback_id
    
    def get_expert_feedback(self, feedback_id: str) -> Optional[Dict]:
        """전문가 피드백 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ef.*, ts.test_type, u.username, u.full_name
                FROM expert_feedback ef
                JOIN test_sessions ts ON ef.session_id = ts.id
                JOIN users u ON ts.user_id = u.id
                WHERE ef.id = ?
            """, (feedback_id,))
            
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def update_expert_score(self, response_id: str, score: float) -> bool:
        """전문가 점수 업데이트"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 응답이 존재하는지 확인
            cursor.execute("SELECT id FROM test_responses WHERE id = ?", (response_id,))
            if not cursor.fetchone():
                return False
            
            # 전문가 점수 업데이트
            cursor.execute("""
                UPDATE test_responses 
                SET expert_score = ? 
                WHERE id = ?
            """, (score, response_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_session_grouped_scores(self, session_id: str) -> Dict:
        """세션별 그룹 점수 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 그룹별 점수 통계
            cursor.execute("""
                SELECT 
                    question_group,
                    question_category,
                    COUNT(*) as question_count,
                    AVG(calculated_score) as avg_ai_score,
                    AVG(expert_score) as avg_expert_score,
                    SUM(calculated_score) as total_ai_score,
                    SUM(expert_score) as total_expert_score
                FROM test_responses 
                WHERE session_id = ?
                GROUP BY question_group, question_category
                ORDER BY question_group
            """, (session_id,))
            
            grouped_scores = [dict(row) for row in cursor.fetchall()]
            
            # 전체 점수
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_questions,
                    AVG(calculated_score) as overall_avg_ai_score,
                    AVG(expert_score) as overall_avg_expert_score,
                    SUM(calculated_score) as overall_total_ai_score,
                    SUM(expert_score) as overall_total_expert_score
                FROM test_responses 
                WHERE session_id = ?
            """, (session_id,))
            
            overall_stats = dict(cursor.fetchone())
            
            return {
                'grouped_scores': grouped_scores,
                'overall_stats': overall_stats
            }
    
    def close(self):
        """데이터베이스 연결 종료"""
        pass  # SQLite는 자동으로 연결을 관리함

# 전역 데이터베이스 인스턴스
db = DatabaseManager()
