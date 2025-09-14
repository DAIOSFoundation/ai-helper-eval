# -*- coding: utf-8 -*-

import numpy as np
import re
import json
import ollama
from collections import defaultdict
# from konlpy.tag import Okt  # Java 오류로 인해 비활성화

class SimilarityScorer:
    def __init__(self, model_name="gemma2:2b"):
        self.model_name = model_name
        self.use_ollama = True  # 항상 Ollama 사용
        
        # 한국어 형태소 분석기 초기화 (Java 오류로 인해 비활성화)
        # self.okt = Okt()
        
        # 평가 기준 템플릿 정의
        self.evaluation_templates = {
            'cdi': {
                'academic_achievement': {
                    'positive': ['어렵지 않다', '쉽다', '잘하다', '괜찮다', '문제없다', '좋다', '재미있다', '성공하다'],
                    'moderate': ['노력하다', '어렵다', '힘들다', '조금 어렵다', '보통이다', '그럭저럭이다'],
                    'negative': ['매우 어렵다', '전혀 못하다', '포기하다', '실패하다', '나쁘다', '싫다', '지겹다']
                },
                'sleep_problems': {
                    'positive': ['잘 잔다', '편안하다', '문제없다', '좋다', '괜찮다'],
                    'moderate': ['가끔 어렵다', '보통이다', '조금 어렵다', '힘들다'],
                    'negative': ['매우 어렵다', '전혀 못한다', '불면증', '잠들기 어렵다', '자주 깬다']
                },
                'crying': {
                    'positive': ['울지 않는다', '평소와 같다', '문제없다', '괜찮다'],
                    'moderate': ['가끔 운다', '조금 더 운다', '보통이다'],
                    'negative': ['자주 운다', '항상 운다', '울고 싶다', '눈물이 난다']
                },
                'fatigue': {
                    'positive': ['피곤하지 않다', '활력있다', '에너지가 있다', '괜찮다'],
                    'moderate': ['가끔 피곤하다', '보통이다', '조금 피곤하다'],
                    'negative': ['항상 피곤하다', '매우 피곤하다', '기력이 없다', '무기력하다']
                },
                'friendship': {
                    'positive': ['친구가 많다', '사람들과 잘 지낸다', '인기가 있다', '좋다'],
                    'moderate': ['친구가 조금 있다', '보통이다', '적당하다'],
                    'negative': ['친구가 없다', '외롭다', '사람들과 어렵다', '고립감']
                },
                'social_interaction': {
                    'positive': ['잘 지낸다', '편하다', '재미있다', '좋다'],
                    'moderate': ['보통이다', '그럭저럭이다', '가끔 어렵다'],
                    'negative': ['어렵다', '힘들다', '불편하다', '싫다']
                },
                'adult_interaction': {
                    'positive': ['편하다', '좋다', '괜찮다', '이해해준다'],
                    'moderate': ['보통이다', '그럭저럭이다', '가끔 어렵다'],
                    'negative': ['어렵다', '힘들다', '무서워', '싫다']
                },
                'loneliness': {
                    'positive': ['외롭지 않다', '괜찮다', '편하다', '좋다'],
                    'moderate': ['가끔 외롭다', '보통이다', '그럭저럭이다'],
                    'negative': ['매우 외롭다', '항상 외롭다', '고독하다', '쓸쓸하다']
                },
                'depression': {
                    'positive': ['우울하지 않다', '기분 좋다', '괜찮다', '밝다'],
                    'moderate': ['가끔 우울하다', '보통이다', '그럭저럭이다'],
                    'negative': ['매우 우울하다', '항상 슬프다', '절망적이다', '어둡다']
                },
                'concentration': {
                    'positive': ['잘 집중한다', '문제없다', '좋다', '괜찮다'],
                    'moderate': ['가끔 어렵다', '보통이다', '그럭저럭이다'],
                    'negative': ['전혀 집중 못한다', '매우 어렵다', '산만하다', '힘들다']
                },
                'appetite': {
                    'positive': ['잘 먹는다', '맛있다', '좋다', '괜찮다'],
                    'moderate': ['보통이다', '그럭저럭이다', '가끔 안 먹는다'],
                    'negative': ['전혀 안 먹는다', '맛없다', '싫다', '토할 것 같다']
                }
            },
            'rcmas': {
                'anxiety': {
                    'positive': ['걱정하지 않는다', '평온하다', '안정적이다', '괜찮다'],
                    'negative': ['걱정이 많다', '불안하다', '초조하다', '긴장된다', '두렵다']
                },
                'anger': {
                    'positive': ['화를 내지 않는다', '차분하다', '침착하다', '평온하다'],
                    'negative': ['화가 많다', '짜증이 난다', '성질이 급하다', '화를 잘 낸다']
                },
                'physical_symptoms': {
                    'positive': ['건강하다', '문제없다', '괜찮다', '편안하다'],
                    'negative': ['속이 메슥거린다', '숨이 차다', '가슴이 답답하다', '몸이 아프다']
                },
                'social_anxiety': {
                    'positive': ['편안하다', '자연스럽다', '괜찮다', '문제없다', '편하다'],
                    'negative': ['불안하다', '긴장된다', '신경쓰인다', '부담스럽다', '어색하다', '두렵다', '무서워한다', '걱정된다']
                },
                'self_esteem': {
                    'positive': ['자신있다', '잘한다', '괜찮다', '좋다', '만족한다'],
                    'moderate': ['보통이다', '그럭저럭이다', '가끔 자신없다'],
                    'negative': ['자신없다', '못한다', '부족하다', '열등감', '비교된다']
                },
                'worry': {
                    'positive': ['걱정없다', '평온하다', '괜찮다', '안정적이다'],
                    'moderate': ['가끔 걱정된다', '보통이다', '그럭저럭이다'],
                    'negative': ['걱정이 많다', '불안하다', '초조하다', '스트레스받는다']
                },
                'family_relationship': {
                    'positive': ['잘 지낸다', '편하다', '좋다', '괜찮다', '사랑한다'],
                    'moderate': ['보통이다', '그럭저럭이다', '가끔 어렵다'],
                    'negative': ['어렵다', '힘들다', '싫다', '갈등', '불편하다']
                },
                'stress': {
                    'positive': ['스트레스없다', '편안하다', '괜찮다', '여유있다'],
                    'moderate': ['가끔 스트레스받는다', '보통이다', '그럭저럭이다'],
                    'negative': ['스트레스가 많다', '힘들다', '압박받는다', '부담된다']
                },
                'mood_swings': {
                    'positive': ['기분이 안정적이다', '괜찮다', '편안하다', '일정하다'],
                    'moderate': ['가끔 변한다', '보통이다', '그럭저럭이다'],
                    'negative': ['기분이 자주 변한다', '갑자기 화난다', '불안정하다', '예측불가능하다']
                }
            },
            'bdi': {
                'sleep_pattern': {
                    'positive': ['잘 잔다', '편안하다', '문제없다', '괜찮다'],
                    'moderate': ['조금 어렵다', '가끔 어렵다', '보통이다'],
                    'negative': ['매우 어렵다', '전혀 못한다', '불면증', '자주 깬다']
                },
                'weight_change': {
                    'positive': ['변화없다', '안정적이다', '괜찮다'],
                    'moderate': ['조금 줄었다', '조금 늘었다', '보통이다'],
                    'negative': ['많이 줄었다', '많이 늘었다', '급격한 변화']
                },
                'appearance': {
                    'positive': ['괜찮다', '만족한다', '좋다', '문제없다'],
                    'moderate': ['보통이다', '그럭저럭이다'],
                    'negative': ['못생겼다', '싫다', '부끄럽다', '자신없다']
                }
            }
        }
        
        # TF-IDF 벡터라이저는 사용하지 않음 (Ollama 기반 평가 사용)
        
        # 키워드 가중치
        self.keyword_weights = {
            'very': 2.0,      # 매우, 정말, 완전히
            'quite': 1.5,     # 꽤, 상당히
            'somewhat': 1.2,  # 조금, 약간
            'not': -1.0,      # 안, 못, 않
            'never': -2.0     # 전혀, 절대
        }
    
    def calculate_similarity_score(self, user_response, category, subcategory):
        """사용자 답변과 평가 기준의 유사도 점수 계산 (Ollama 기반)"""
        if category not in self.evaluation_templates:
            return 0
        
        if subcategory not in self.evaluation_templates[category]:
            return 0
        
        templates = self.evaluation_templates[category][subcategory]
        
        # Ollama를 사용한 유사도 측정
        try:
            score = self._calculate_ollama_similarity(user_response, category, subcategory, templates)
            return score
        except Exception as e:
            print(f"Ollama 유사도 측정 오류: {e}")
            # 기본 점수 반환
            return 1
    
    def _extract_korean_stems(self, text):
        """한국어 텍스트에서 어간 추출"""
        if not text:
            return []
        
        # 형태소 분석
        morphs = self.okt.morphs(text, stem=True)
        
        # 어간만 추출 (명사, 동사, 형용사, 부사)
        stems = []
        for morph in morphs:
            # 품사 태깅
            pos_tags = self.okt.pos(morph, stem=True)
            for word, pos in pos_tags:
                # 의미있는 품사만 추출
                if pos in ['Noun', 'Verb', 'Adjective', 'Adverb', 'Determiner']:
                    stems.append(word)
        
        return stems
    
    def _normalize_korean_text(self, text):
        """한국어 텍스트 정규화 (어간 기반)"""
        if not text:
            return ""
        
        # 어간 추출
        stems = self._extract_korean_stems(text)
        
        # 어간들을 공백으로 연결
        normalized = " ".join(stems)
        
        return normalized
    
    def analyze_user_intent(self, user_response, system_question=None):
        """사용자 의도 분석 (Ollama 기반)"""
        # 항상 Ollama 사용
        try:
            # 시스템 질문이 있으면 맥락을 포함한 프롬프트 생성
            if system_question:
                prompt = f"""
다음 대화를 분석하여 사용자의 의도를 파악해주세요.

시스템 질문: "{system_question}"
사용자 응답: "{user_response}"

다음 중 하나로 분류해주세요:
1. "ready" - 질문에 답할 준비가 되었음
2. "answer" - 질문에 대한 구체적인 답변을 제공함
3. "greeting" - 인사말
4. "confused" - 혼란스러워함
5. "refuse" - 거부함

답변은 반드시 위의 키워드 중 하나만 출력해주세요.
"""
            else:
                prompt = f"""
사용자의 응답을 분석하여 의도를 파악해주세요.

사용자 응답: "{user_response}"

다음 중 하나로 분류해주세요:
1. "ready" - 질문에 답할 준비가 되었음
2. "answer" - 질문에 대한 구체적인 답변을 제공함
3. "greeting" - 인사말
4. "confused" - 혼란스러워함
5. "refuse" - 거부함

답변은 반드시 위의 키워드 중 하나만 출력해주세요.
"""
            
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': '당신은 사용자의 의도를 분석하는 전문가입니다. 주어진 응답을 분석하여 적절한 의도를 분류해주세요.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.1,
                    'top_p': 0.9
                }
            )
            
            intent = response['message']['content'].strip().lower()
            
            # 의도 분류 (더 정확한 파싱)
            if any(keyword in intent for keyword in ['ready', '준비', '시작']):
                return 'ready'
            elif any(keyword in intent for keyword in ['answer', '답변', '응답']):
                return 'answer'
            elif any(keyword in intent for keyword in ['greeting', '인사', '안녕']):
                return 'greeting'
            elif any(keyword in intent for keyword in ['confused', '혼란', '모르겠']):
                return 'confused'
            elif any(keyword in intent for keyword in ['refuse', '거부', '싫어']):
                return 'refuse'
            else:
                # 기본값: 답변으로 간주
                return 'answer'
                
        except Exception as e:
            print(f"Ollama 의도 분석 오류: {e}")
            return 'answer'  # 기본값
    
    def _preprocess_text(self, text):
        """텍스트 전처리"""
        # 소문자 변환
        text = text.lower()
        
        # 특수문자 제거
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # 공백 정규화
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _calculate_keyword_similarity(self, user_response, keywords):
        """키워드 기반 유사도 계산"""
        if not user_response or not keywords:
            return 0
        
        # 사용자 응답에서 키워드 매칭
        matches = 0
        total_keywords = len(keywords)
        
        for keyword in keywords:
            if keyword in user_response:
                # 키워드 가중치 적용
                weight = 1.0
                for modifier, modifier_weight in self.keyword_weights.items():
                    if modifier in user_response:
                        weight *= modifier_weight
                
                matches += weight
        
        # 유사도 계산 (0-1 범위)
        if total_keywords > 0:
            similarity = min(matches / total_keywords, 1.0)
        else:
            similarity = 0
        
        return similarity
    
    def _level_to_score(self, level, category):
        """레벨을 점수로 변환"""
        if category == 'cdi':
            if level == 'positive':
                return 0
            elif level == 'moderate':
                return 1
            elif level == 'negative':
                return 2
        elif category == 'rcmas':
            if level == 'positive':
                return 0
            elif level == 'negative':
                return 1
        elif category == 'bdi':
            if level == 'positive':
                return 0
            elif level == 'moderate':
                return 1
            elif level == 'negative':
                return 2
        
        return 1  # 기본값
    
    def get_evaluation_criteria(self, category, subcategory):
        """평가 기준 반환"""
        if category in self.evaluation_templates and subcategory in self.evaluation_templates[category]:
            return self.evaluation_templates[category][subcategory]
        return {}
    
    def extract_keywords_from_response(self, user_response):
        """사용자 응답에서 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 기법 사용 가능)
        keywords = []
        
        # 감정 키워드
        emotion_keywords = ['좋다', '나쁘다', '어렵다', '쉽다', '피곤하다', '활력있다', 
                          '걱정', '불안', '화', '짜증', '편안', '긴장']
        
        for keyword in emotion_keywords:
            if keyword in user_response:
                keywords.append(keyword)
        
        return keywords
    
    def _calculate_ollama_similarity(self, user_response, category, subcategory, templates):
        """Ollama를 사용한 유사도 측정"""
        # 프롬프트 구성
        prompt = self._create_evaluation_prompt(user_response, category, subcategory, templates)
        
        # Ollama API 호출
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    'role': 'system',
                    'content': '당신은 아동 및 청소년의 정서 상태를 평가하는 전문가입니다. 주어진 답변을 분석하여 적절한 점수를 매겨주세요.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            options={
                'temperature': 0.1,  # 일관성을 위해 낮은 temperature 사용
                'top_p': 0.9
            }
        )
        
        # 응답에서 점수 추출
        score = self._extract_score_from_response(response['message']['content'], category)
        return score
    
    def _create_evaluation_prompt(self, user_response, category, subcategory, templates):
        """평가를 위한 프롬프트 생성"""
        category_names = {
            'cdi': '아동용 우울척도(CDI)',
            'rcmas': '아동불안척도(RCMAS)', 
            'bdi': '벡 우울척도(BDI)'
        }
        
        subcategory_names = {
            'academic_achievement': '학업 성취',
            'sleep_problems': '수면 문제',
            'crying': '울음',
            'fatigue': '피곤함',
            'friendship': '친구 관계',
            'anxiety': '불안',
            'anger': '화',
            'physical_symptoms': '신체 증상',
            'sleep_pattern': '수면 패턴',
            'weight_change': '체중 변화',
            'appearance': '외모'
        }
        
        category_name = category_names.get(category, category)
        subcategory_name = subcategory_names.get(subcategory, subcategory)
        
        # 평가 기준 설명
        criteria_text = ""
        for level, keywords in templates.items():
            level_name = {
                'positive': '긍정적/정상',
                'moderate': '보통/중간',
                'negative': '부정적/문제'
            }.get(level, level)
            criteria_text += f"- {level_name}: {', '.join(keywords)}\n"
        
        # 사용자 답변의 어간 추출 (간단한 버전)
        user_stems = self._extract_korean_stems(user_response)
        user_normalized = " ".join(user_stems) if user_stems else user_response
        
        prompt = f"""
다음은 {category_name}의 '{subcategory_name}' 항목에 대한 평가입니다.

평가 기준:
{criteria_text}

사용자 답변: "{user_response}"
어간 분석: "{user_normalized}"

위 답변을 분석하여 다음 점수를 매겨주세요:
- 0점: 정상/긍정적 상태
- 1점: 보통/중간 상태  
- 2점: 문제/부정적 상태 (CDI, BDI의 경우)
- 1점: 문제/부정적 상태 (RCMAS의 경우)

한국어의 어간과 어미를 고려하여 의미를 정확히 파악해주세요.
답변은 반드시 숫자만 출력해주세요 (0, 1, 또는 2).
"""
        return prompt
    
    def _extract_score_from_response(self, response_text, category):
        """응답에서 점수 추출"""
        # 숫자 추출
        import re
        numbers = re.findall(r'\d+', response_text)
        
        if not numbers:
            return 1  # 기본값
        
        score = int(numbers[0])
        
        # 점수 범위 검증
        if category == 'rcmas':
            # RCMAS는 0 또는 1
            return min(score, 1)
        else:
            # CDI, BDI는 0, 1, 2
            return min(score, 2)
    
    def _calculate_keyword_similarity_fallback(self, user_response, templates, category):
        """키워드 기반 유사도 측정 (폴백)"""
        user_response = self._preprocess_text(user_response)
        
        # 각 레벨별 유사도 계산
        similarities = {}
        for level, keywords in templates.items():
            similarity = self._calculate_keyword_similarity(user_response, keywords)
            similarities[level] = similarity
        
        # 가장 높은 유사도를 가진 레벨 선택
        best_level = max(similarities, key=similarities.get)
        best_score = similarities[best_level]
        
        # 레벨을 점수로 변환
        score = self._level_to_score(best_level, category)
        
        # 유사도가 낮으면 중간 점수 반환
        if best_score < 0.3:
            return 1  # 중간 점수
        
        return score
