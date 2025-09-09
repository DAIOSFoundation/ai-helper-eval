import numpy as np
from modules.entities import EntityTracker

class ActionTracker:
    def __init__(self, et):
        self.et = et
        
        # 10대 청소년 문체 액션 템플릿 (3개 액션)
        self.action_templates = [
            "안녕! 오늘 기분은 어때? 몇 가지 질문으로 이야기해볼까?",
            "질문",  # 동적 질문 템플릿
            "이야기해줘서 고마워. 오늘 대화로 느낀 점들을 정리해줄게."
        ]
        
        self.action_size = len(self.action_templates)
        
        # 액션 마스크 정의 (현재 상태에 따라 가능한 액션들)
        self.action_mask = np.ones(self.action_size, dtype=np.float32)
        
        # 질문과 평가 항목 매핑 (20개 질문)
        self.question_evaluation_mapping = {
            1: ('cdi', 'academic_achievement'),
            2: ('cdi', 'social_interaction'),
            3: ('cdi', 'sleep_problems'),
            4: ('cdi', 'adult_interaction'),
            5: ('cdi', 'loneliness'),
            6: ('cdi', 'depression'),
            7: ('cdi', 'friendship'),
            8: ('cdi', 'concentration'),
            9: ('cdi', 'crying'),
            10: ('cdi', 'appetite'),
            11: ('cdi', 'fatigue'),
            12: ('rcmas', 'anxiety'),
            13: ('rcmas', 'self_esteem'),
            14: ('rcmas', 'worry'),
            15: ('rcmas', 'family_relationship'),
            16: ('rcmas', 'stress'),
            17: ('rcmas', 'mood_swings'),
            18: ('bdi', 'self_harm'),
            19: ('bdi', 'suicidal_thoughts')
        }
    
    def get_action_templates(self):
        """액션 템플릿 반환"""
        return self.action_templates
    
    def action_mask(self):
        """현재 상태에 따른 액션 마스크 반환"""
        # 모든 액션이 기본적으로 가능
        mask = np.ones(self.action_size, dtype=np.float32)
        
        # 진단 모델이 전체 프로세스를 제어하도록 단순화
        # 특별한 제약 없이 모든 액션 허용
        
        return mask
    
    def set_current_evaluation(self, action_index):
        """현재 액션에 대한 평가 항목 설정"""
        if action_index in self.question_evaluation_mapping:
            category, subcategory = self.question_evaluation_mapping[action_index]
            self.et.entities['current_evaluation'] = (category, subcategory)
        else:
            self.et.entities['current_evaluation'] = None
