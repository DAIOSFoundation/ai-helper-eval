# -*- coding: utf-8 -*-

import json
import numpy as np
from collections import defaultdict

class Data:
    def __init__(self, entity_tracker, action_tracker):
        self.et = entity_tracker
        self.at = action_tracker
        
        # 트레이닝 데이터 로드
        self.trainset = self._load_training_data()
    
    def _load_training_data(self):
        """트레이닝 데이터 로드 및 전처리 (점수화된 데이터 우선 사용)"""
        try:
            # 점수화된 데이터 우선 사용
            with open('training_ds/training_dataset_scored.json', 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            print("✅ 점수화된 훈련 데이터 로드 완료")
        except FileNotFoundError:
            try:
                # 점수화된 데이터가 없으면 원본 데이터 사용
                with open('training_ds/training_dataset.json', 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                print("⚠️  원본 훈련 데이터 사용 (점수화된 데이터 없음)")
            except FileNotFoundError:
                print("❌ 트레이닝 데이터 파일을 찾을 수 없습니다.")
                return [], []
        
        # 대화 데이터 처리
        processed_dialogs = []
        dialog_indices = []
        
        start_idx = 0
        
        for dialog in raw_data:
            dialog_turns = []
            
            for turn in dialog:
                if turn['speaker'] == 'user':
                    # 사용자 발화 (점수 정보 포함)
                    user_utterance = turn['utterance']
                    user_score = turn.get('score')  # 점수화된 데이터에서 점수 추출
                    dialog_turns.append({
                        'utterance': user_utterance,
                        'action': None,
                        'score': user_score
                    })  # 응답은 다음 턴에서 처리
                elif turn['speaker'] == 'system':
                    # 시스템 응답
                    system_utterance = turn['utterance']
                    metadata = turn.get('metadata', {})
                    
                    # 메타데이터에서 액션 인덱스 결정
                    action_idx = self._metadata_to_action_idx(metadata, system_utterance)
                    
                    # 이전 턴이 사용자 발화였다면 응답 매칭
                    if dialog_turns and dialog_turns[-1]['action'] is None:
                        dialog_turns[-1]['action'] = action_idx
                    else:
                        # 새로운 시스템 발화 (인사 등)
                        dialog_turns.append((None, action_idx))
            
            if dialog_turns:
                processed_dialogs.extend(dialog_turns)
                end_idx = start_idx + len(dialog_turns)
                dialog_indices.append({'start': start_idx, 'end': end_idx})
                start_idx = end_idx
        
        return processed_dialogs, dialog_indices
    
    def _metadata_to_action_idx(self, metadata, utterance):
        """메타데이터를 액션 인덱스로 변환"""
        action_type = metadata.get('action_type', '')
        
        if action_type == 'greeting':
            return 0  # 인사
        elif action_type == 'question':
            question_index = metadata.get('question_index', 1)
            if question_index == 1:
                return 1  # CDI 질문
            elif question_index == 2:
                return 2  # RCMAS 질문
            elif question_index == 3:
                return 3  # BDI 질문
        elif action_type == 'completion':
            return 4  # 진단 완료
        
        # 메타데이터가 없으면 기존 방식으로 폴백
        return self._utterance_to_action_idx(utterance)
    
    def _utterance_to_action_idx(self, utterance):
        """발화를 액션 인덱스로 변환 (폴백용)"""
        # 액션 템플릿과 매칭
        for idx, template in enumerate(self.at.action_templates):
            if self._is_similar_utterance(utterance, template):
                return idx
        
        # 매칭되지 않으면 기본값 (인사)
        return 0
    
    def _is_similar_utterance(self, utterance1, utterance2):
        """두 발화가 유사한지 확인"""
        # 간단한 유사도 검사
        words1 = set(utterance1.split())
        words2 = set(utterance2.split())
        
        # 공통 단어 비율 계산
        common_words = words1.intersection(words2)
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        similarity = len(common_words) / max(len(words1), len(words2))
        return similarity > 0.3  # 30% 이상 유사하면 매칭
    
    def get_training_batches(self, batch_size=32):
        """훈련용 배치 생성"""
        dialogs, dialog_indices = self.trainset
        
        batches = []
        for i in range(0, len(dialogs), batch_size):
            batch = dialogs[i:i+batch_size]
            batches.append(batch)
        
        return batches
    
    def get_dialog_data(self, dialog_idx):
        """특정 대화 데이터 반환"""
        dialogs, dialog_indices = self.trainset
        
        if dialog_idx >= len(dialog_indices):
            return []
        
        start = dialog_indices[dialog_idx]['start']
        end = dialog_indices[dialog_idx]['end']
        
        return dialogs[start:end]

