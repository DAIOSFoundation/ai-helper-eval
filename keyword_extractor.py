"""
AI Helper Evaluation System - Keyword Extractor Module
사용자 자연어 답변에서 키워드를 자동 추출하고 평가 템플릿을 업데이트하는 시스템
"""

import re
import json
from collections import Counter, defaultdict
from typing import List, Dict, Tuple
import sqlite3
from database import db

class KeywordExtractor:
    def __init__(self):
        """키워드 추출기 초기화"""
        self.stop_words = {
            # 한국어 불용어
            '은', '는', '이', '가', '을', '를', '에', '의', '로', '으로', '와', '과', 
            '도', '만', '부터', '까지', '에서', '에게', '한테', '께', '보다', '처럼',
            '같이', '같은', '같은데', '같지만', '같으면서', '같은데도', '같은데도',
            '그리고', '그런데', '하지만', '그러나', '또한', '또는', '또', '그래서',
            '그러므로', '따라서', '그런', '이런', '저런', '어떤', '무엇', '누구',
            '언제', '어디', '왜', '어떻게', '얼마나', '몇', '몇몇', '많은', '적은',
            '좋은', '나쁜', '큰', '작은', '높은', '낮은', '빠른', '느린', '많이',
            '조금', '아주', '매우', '정말', '진짜', '완전', '너무', '꽤', '상당히',
            '그냥', '단지', '오직', '다만', '뿐', '만', '조차', '마저', '까지도',
            '나', '너', '우리', '그들', '그녀', '그', '이', '저', '이것', '그것', '저것',
            '여기', '거기', '저기', '어디', '언제', '왜', '어떻게', '무엇', '누구',
            '있다', '없다', '하다', '되다', '가다', '오다', '보다', '듣다', '말하다',
            '생각하다', '느끼다', '알다', '모르다', '좋다', '나쁘다', '크다', '작다',
            '많다', '적다', '빠르다', '느리다', '높다', '낮다', '길다', '짧다',
            '넓다', '좁다', '두껍다', '얇다', '무겁다', '가볍다', '따뜻하다', '차갑다',
            '뜨겁다', '시원하다', '달다', '쓰다', '맵다', '짜다', '시다', '쓴다',
            '맵다', '짜다', '시다', '쓴다', '맵다', '짜다', '시다', '쓴다'
        }
        
        # 감정 관련 키워드 패턴
        self.emotion_patterns = {
            'depression': [
                '우울', '슬픔', '절망', '무기력', '의욕', '관심', '기쁨', '행복',
                '미래', '희망', '자살', '죽음', '끝', '포기', '의미없', '쓸모없',
                '실패', '잘못', '문제', '걱정', '불안', '두려움', '걱정', '근심'
            ],
            'anxiety': [
                '불안', '걱정', '근심', '두려움', '무서움', '긴장', '스트레스',
                '압박', '부담', '초조', '안절부절', '조급', '성급', '조심',
                '경계', '주의', '신경', '민감', '예민', '과민', '민감'
            ],
            'sleep': [
                '잠', '수면', '자다', '잠들', '깨다', '깨어', '아침', '밤', '밤에',
                '잠들어', '잠들지', '잠들', '잠들어', '잠들지', '잠들', '잠들어',
                '잠들지', '잠들', '잠들어', '잠들지', '잠들', '잠들어', '잠들지'
            ]
        }
    
    def extract_keywords(self, text: str, min_length: int = 2) -> List[str]:
        """텍스트에서 키워드 추출"""
        # 한글, 영문, 숫자만 추출
        words = re.findall(r'[가-힣a-zA-Z0-9]+', text.lower())
        
        # 불용어 제거 및 최소 길이 필터링
        keywords = [
            word for word in words 
            if word not in self.stop_words and len(word) >= min_length
        ]
        
        return keywords
    
    def extract_emotion_keywords(self, text: str, category: str) -> List[str]:
        """특정 카테고리의 감정 키워드 추출"""
        keywords = self.extract_keywords(text)
        emotion_keywords = []
        
        if category in self.emotion_patterns:
            for keyword in keywords:
                for pattern in self.emotion_patterns[category]:
                    if pattern in keyword or keyword in pattern:
                        emotion_keywords.append(keyword)
        
        return emotion_keywords
    
    def calculate_keyword_weights(self, keywords: List[str], responses: List[str]) -> Dict[str, float]:
        """키워드 가중치 계산 (TF-IDF 기반)"""
        # 키워드 빈도 계산
        keyword_counts = Counter(keywords)
        total_keywords = len(keywords)
        
        # 문서별 키워드 존재 여부
        doc_keyword_presence = defaultdict(set)
        for i, response in enumerate(responses):
            response_keywords = self.extract_keywords(response)
            for keyword in response_keywords:
                doc_keyword_presence[keyword].add(i)
        
        # TF-IDF 계산
        keyword_weights = {}
        total_docs = len(responses)
        
        for keyword, count in keyword_counts.items():
            # TF (Term Frequency)
            tf = count / total_keywords
            
            # IDF (Inverse Document Frequency)
            docs_with_keyword = len(doc_keyword_presence[keyword])
            idf = 1.0 if docs_with_keyword == 0 else total_docs / docs_with_keyword
            idf = 1.0 + (idf if idf > 0 else 1.0)
            
            # TF-IDF
            keyword_weights[keyword] = tf * idf
        
        return keyword_weights
    
    def update_evaluation_template(self, test_type: str, question_id: str, 
                                 new_responses: List[str]) -> Dict[str, any]:
        """평가 템플릿 업데이트"""
        # 기존 템플릿 조회
        existing_template = db.get_evaluation_template(test_type, question_id)
        
        # 새로운 키워드 추출
        all_keywords = []
        for response in new_responses:
            keywords = self.extract_keywords(response)
            all_keywords.extend(keywords)
        
        # 키워드 가중치 계산
        keyword_weights = self.calculate_keyword_weights(all_keywords, new_responses)
        
        # 상위 키워드 선택 (가중치 기준)
        top_keywords = sorted(
            keyword_weights.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:20]  # 상위 20개 키워드
        
        # 기존 키워드와 병합
        if existing_template:
            existing_keywords = json.loads(existing_template.get('keywords', '[]'))
            existing_weights = json.loads(existing_template.get('weights', '{}'))
            
            # 기존 키워드 가중치 업데이트
            for keyword, weight in top_keywords:
                if keyword in existing_weights:
                    # 기존 가중치와 새 가중치의 평균
                    existing_weights[keyword] = (existing_weights[keyword] + weight) / 2
                else:
                    existing_weights[keyword] = weight
            
            # 최종 키워드 리스트
            final_keywords = list(existing_weights.keys())
            final_weights = existing_weights
        else:
            final_keywords = [kw[0] for kw in top_keywords]
            final_weights = dict(top_keywords)
        
        # 데이터베이스 업데이트
        template_id = db.update_evaluation_template(
            test_type=test_type,
            question_id=question_id,
            keywords=json.dumps(final_keywords, ensure_ascii=False),
            weights=json.dumps(final_weights, ensure_ascii=False)
        )
        
        return {
            'template_id': template_id,
            'keywords': final_keywords,
            'weights': final_weights,
            'new_keywords_count': len([kw for kw in final_keywords if kw not in (existing_template.get('keywords', '[]') if existing_template else [])])
        }
    
    def analyze_response_sentiment(self, text: str) -> Dict[str, float]:
        """응답의 감정 분석"""
        keywords = self.extract_keywords(text)
        
        sentiment_scores = {
            'depression': 0.0,
            'anxiety': 0.0,
            'sleep': 0.0
        }
        
        for category, patterns in self.emotion_patterns.items():
            for keyword in keywords:
                for pattern in patterns:
                    if pattern in keyword or keyword in pattern:
                        sentiment_scores[category] += 1.0
        
        # 정규화 (0-1 범위)
        total_keywords = len(keywords)
        if total_keywords > 0:
            for category in sentiment_scores:
                sentiment_scores[category] = min(sentiment_scores[category] / total_keywords, 1.0)
        
        return sentiment_scores
    
    def get_keyword_suggestions(self, test_type: str, question_id: str, 
                               user_response: str) -> List[str]:
        """사용자 응답 기반 키워드 제안"""
        # 현재 템플릿 조회
        template = db.get_evaluation_template(test_type, question_id)
        
        if not template:
            return []
        
        template_keywords = json.loads(template.get('keywords', '[]'))
        template_weights = json.loads(template.get('weights', '{}'))
        
        # 사용자 응답에서 키워드 추출
        user_keywords = self.extract_keywords(user_response)
        
        # 템플릿 키워드와 매칭되는 키워드 찾기
        matching_keywords = []
        for user_keyword in user_keywords:
            for template_keyword in template_keywords:
                if user_keyword in template_keyword or template_keyword in user_keyword:
                    matching_keywords.append({
                        'keyword': template_keyword,
                        'weight': template_weights.get(template_keyword, 0),
                        'user_keyword': user_keyword
                    })
        
        # 가중치 기준 정렬
        matching_keywords.sort(key=lambda x: x['weight'], reverse=True)
        
        return [kw['keyword'] for kw in matching_keywords[:10]]  # 상위 10개
    
    def generate_feedback_suggestions(self, test_type: str, question_id: str,
                                    user_response: str, calculated_score: float) -> Dict[str, any]:
        """피드백 제안 생성"""
        # 감정 분석
        sentiment_scores = self.analyze_response_sentiment(user_response)
        
        # 키워드 제안
        keyword_suggestions = self.get_keyword_suggestions(test_type, question_id, user_response)
        
        # 점수 기반 피드백
        score_feedback = self._generate_score_feedback(calculated_score, test_type)
        
        return {
            'sentiment_analysis': sentiment_scores,
            'keyword_suggestions': keyword_suggestions,
            'score_feedback': score_feedback,
            'recommended_score_range': self._get_recommended_score_range(sentiment_scores, test_type)
        }
    
    def _generate_score_feedback(self, score: float, test_type: str) -> str:
        """점수 기반 피드백 생성"""
        if test_type == 'cdi':
            if score >= 19:
                return "심각한 우울 증상이 관찰됩니다. 전문의 상담이 필요합니다."
            elif score >= 13:
                return "중간 정도의 우울 증상이 관찰됩니다. 주의 깊은 관찰이 필요합니다."
            elif score >= 7:
                return "경미한 우울 증상이 관찰됩니다. 지속적인 관심이 필요합니다."
            else:
                return "정상 범위의 응답입니다."
        elif test_type == 'rcmas':
            if score >= 15:
                return "높은 불안 수준이 관찰됩니다. 전문가 상담을 권장합니다."
            elif score >= 10:
                return "중간 정도의 불안이 관찰됩니다. 관심과 지원이 필요합니다."
            elif score >= 5:
                return "경미한 불안이 관찰됩니다. 주의 깊은 관찰이 필요합니다."
            else:
                return "정상 범위의 응답입니다."
        elif test_type == 'bdi':
            if score >= 29:
                return "심각한 우울 증상이 관찰됩니다. 즉시 전문의 상담이 필요합니다."
            elif score >= 20:
                return "중간 정도의 우울 증상이 관찰됩니다. 전문가 상담을 권장합니다."
            elif score >= 14:
                return "경미한 우울 증상이 관찰됩니다. 지속적인 관심이 필요합니다."
            else:
                return "정상 범위의 응답입니다."
        else:
            return "점수 분석이 필요합니다."
    
    def _get_recommended_score_range(self, sentiment_scores: Dict[str, float], test_type: str) -> Tuple[float, float]:
        """권장 점수 범위 계산"""
        base_score = 0.0
        
        if test_type == 'cdi':
            base_score = sentiment_scores['depression'] * 10
        elif test_type == 'rcmas':
            base_score = sentiment_scores['anxiety'] * 10
        elif test_type == 'bdi':
            base_score = sentiment_scores['depression'] * 15
        
        # ±2 범위로 권장 점수 범위 설정
        return (max(0, base_score - 2), min(10, base_score + 2))

# 전역 키워드 추출기 인스턴스
keyword_extractor = KeywordExtractor()
