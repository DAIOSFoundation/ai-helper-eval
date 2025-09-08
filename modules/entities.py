# -*- coding: utf-8 -*-

import re
import numpy as np

class EntityTracker:
    def __init__(self):
        # 심리 진단 관련 엔티티들
        self.entities = {
            'cdi_score': None,      # 아동용 우울척도 점수
            'rcmas_score': None,    # 아동불안척도 점수  
            'bdi_score': None,      # 벡 우울척도 점수
            'current_question': None,  # 현재 질문 유형
            'user_response': None,     # 사용자 응답
            'question_type': None,     # 질문 유형 (cdi, rcmas, bdi)
            'question_category': None, # 질문 카테고리
            'evaluation_history': [],  # 평가 히스토리
            'current_evaluation': None, # 현재 평가 중인 항목
            'current_question_index': 0,  # 현재 질문 인덱스
            'answered_questions': set(),  # 답변한 질문들
        }
        
        # 엔티티 특성 수
        self.num_features = len(self.entities)
        
        # 질문 패턴 매칭을 위한 정규식
        self.question_patterns = {
            'cdi': r'CDI|아동용 우울척도|학업 성취|수면 문제|울음|피곤함|친구 관계|능력|잘못의 원인|외모|사람들과의 관계',
            'rcmas': r'RCMAS|아동불안척도|불안|걱정|화|피곤|속이 메슥|숨쉬기|놀라서|꼼지락|다른 사람들',
            'bdi': r'BDI|벡 우울 척도|수면 패턴|체중 변화|외모 변화|울음|자기비판|업무 능력|피로|죄책감|성에 대한 관심|자기혐오|짜증|사회적 위축'
        }
        
        # 응답 점수 매핑
        self.score_mapping = {
            'cdi': {
                'positive': 0,  # 긍정적 응답
                'moderate': 1,  # 중간 응답  
                'negative': 2   # 부정적 응답
            },
            'rcmas': {
                'no': 0,        # 아니오
                'yes': 1        # 예
            },
            'bdi': {
                'none': 0,      # 전혀 없음
                'mild': 1,      # 가벼움
                'moderate': 2,  # 중간
                'severe': 3     # 심함
            }
        }
    
    def extract_entities(self, utterance, is_test=False, similarity_scorer=None, precomputed_score=None):
        """발화에서 엔티티 추출 (점수화된 데이터 지원)"""
        utterance = utterance.strip()
        
        # 현재 질문 유형 파악
        question_type = self._identify_question_type(utterance)
        if question_type:
            self.entities['question_type'] = question_type
        
        # 사용자 응답 저장
        self.entities['user_response'] = utterance
        
        # 주관식 답변 평가 (점수화된 데이터 우선 사용)
        if not is_test and self.entities['current_evaluation']:
            category, subcategory = self.entities['current_evaluation']
            
            # 점수가 미리 계산되어 있으면 사용, 없으면 Ollama 호출
            if precomputed_score is not None:
                score = precomputed_score
                print(f"  📊 미리 계산된 점수 사용: {score}")
            elif similarity_scorer:
                score = similarity_scorer.calculate_similarity_score(utterance, category, subcategory)
                print(f"  🔍 Ollama로 점수 계산: {score}")
            else:
                score = 1  # 기본값
            
            # 평가 히스토리에 추가
            evaluation_record = {
                'category': category,
                'subcategory': subcategory,
                'response': utterance,
                'score': score,
                'timestamp': len(self.entities['evaluation_history']),
                'source': 'precomputed' if precomputed_score is not None else 'ollama'
            }
            self.entities['evaluation_history'].append(evaluation_record)
            
            # 점수 업데이트
            if category == 'cdi':
                if self.entities['cdi_score'] is None:
                    self.entities['cdi_score'] = 0
                self.entities['cdi_score'] += score
            elif category == 'rcmas':
                if self.entities['rcmas_score'] is None:
                    self.entities['rcmas_score'] = 0
                self.entities['rcmas_score'] += score
            elif category == 'bdi':
                if self.entities['bdi_score'] is None:
                    self.entities['bdi_score'] = 0
                self.entities['bdi_score'] += score
        
        return utterance, self.entities.copy()
    
    def _identify_question_type(self, utterance):
        """발화에서 질문 유형 식별"""
        utterance_lower = utterance.lower()
        
        for q_type, pattern in self.question_patterns.items():
            if re.search(pattern, utterance, re.IGNORECASE):
                return q_type
        return None
    
    def _calculate_score(self, utterance, question_type):
        """응답에서 점수 계산"""
        if not question_type:
            return None
            
        utterance_lower = utterance.lower()
        
        if question_type == 'cdi':
            # CDI 점수 계산 로직
            if any(word in utterance_lower for word in ['어렵지 않', '괜찮', '좋', '많다']):
                return 0
            elif any(word in utterance_lower for word in ['노력', '어렵', '좋지 않', '적다']):
                return 1
            elif any(word in utterance_lower for word in ['전혀', '없다', '항상', '모든']):
                return 2
                
        elif question_type == 'rcmas':
            # RCMAS 점수 계산 로직
            if '예' in utterance or 'yes' in utterance_lower:
                return 1
            elif '아니오' in utterance or 'no' in utterance_lower or '아니' in utterance:
                return 0
                
        elif question_type == 'bdi':
            # BDI 점수 계산 로직
            if '1번' in utterance or '첫번째' in utterance:
                return 0
            elif '2번' in utterance or '두번째' in utterance:
                return 1
            elif '3번' in utterance or '세번째' in utterance:
                return 2
            elif '4번' in utterance or '네번째' in utterance:
                return 3
        
        return None
    
    def context_features(self):
        """현재 컨텍스트 특성 반환"""
        features = []
        
        # 각 엔티티가 설정되었는지 여부 (0 또는 1)
        for key in self.entities:
            if self.entities[key] is not None:
                features.append(1)
            else:
                features.append(0)
        
        return np.array(features, dtype=np.float32)
    
    def reset(self):
        """엔티티 트래커 초기화"""
        for key in self.entities:
            self.entities[key] = None
