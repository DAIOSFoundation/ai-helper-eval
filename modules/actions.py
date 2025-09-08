import numpy as np
from modules.entities import EntityTracker

class ActionTracker:
    def __init__(self, et):
        self.et = et
        
        # 10대 청소년 문체 액션 템플릿 (카테고리 정보 숨김)
        self.action_templates = [
            "안녕! 오늘 기분은 어때? 몇 가지 질문으로 이야기해볼까?",
            "야, 요즘 공부는 어때? 어떤 기분이야?",
            "친구들이나 다른 애들이랑 있을 때 어떤 느낌이야?",
            "요즘 잠은 잘 자? 잠자리는 어때?",
            "이야기해줘서 고마워. 오늘 대화로 느낀 점들을 정리해줄게."
        ]
        
        self.action_size = len(self.action_templates)
        
        # 액션 마스크 정의 (현재 상태에 따라 가능한 액션들)
        self.action_mask = np.ones(self.action_size, dtype=np.float32)
        
        # 질문과 평가 항목 매핑 (3개 카테고리로 간소화)
        self.question_evaluation_mapping = {
            1: ('cdi', 'academic_achievement'),
            2: ('rcmas', 'social_anxiety'),
            3: ('bdi', 'sleep_pattern')
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
