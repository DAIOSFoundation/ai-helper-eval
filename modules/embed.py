# -*- coding: utf-8 -*-

import numpy as np
import torch
import torch.nn as nn

class UtteranceEmbed:
    def __init__(self, embedding_dim=64):
        self.dim = embedding_dim
        
        # 간단한 임베딩 레이어
        self.embedding = nn.Embedding(1000, embedding_dim)
        
        # 한국어 심리 진단 관련 토큰들
        self.token_to_id = {
            '<PAD>': 0,
            '<UNK>': 1,
            '안녕': 2,
            '안녕하세요': 3,
            '시작': 4,
            '준비': 5,
            '네': 6,
            '예': 7,
            '아니오': 8,
            '아니': 9,
            '좋다': 10,
            '나쁘다': 11,
            '어렵다': 12,
            '쉽다': 13,
            '피곤하다': 14,
            '울다': 15,
            '잠': 16,
            '친구': 17,
            '학교': 18,
            '공부': 19,
            '성적': 20,
            '능력': 21,
            '외모': 22,
            '사람': 23,
            '관계': 24,
            '걱정': 25,
            '화': 26,
            '메슥': 27,
            '숨': 28,
            '놀라다': 29,
            '꼼지락': 30,
            '체중': 31,
            '변화': 32,
            '죄책감': 33,
            '성': 34,
            '관심': 35,
            '자기혐오': 36,
            '짜증': 37,
            '사회적': 38,
            '위축': 39,
            '번': 40,
            '첫번째': 41,
            '두번째': 42,
            '세번째': 43,
            '네번째': 44,
            '전혀': 45,
            '항상': 46,
            '가끔': 47,
            '자주': 48,
            '많다': 49,
            '적다': 50,
            '없다': 51,
            '있다': 52,
            '느끼다': 53,
            '생각하다': 54,
            '답변': 55,
            '감사': 56,
            '진단': 57,
            '결과': 58,
            '점수': 59,
            '요약': 60,
            'CDI': 61,
            'RCMAS': 62,
            'BDI': 63,
            '우울': 64,
            '불안': 65,
            '아동': 66,
            '청소년': 67,
            '정서': 68,
            '상태': 69,
            '질문': 70,
            '선택': 71,
            '보기': 72,
            '가장': 73,
            '가까운': 74,
            '문장': 75,
            '해당': 76,
            '상황': 77,
            '경험': 78,
            '최근': 79,
            '요즘': 80,
            '전': 81,
            '평소': 82,
            '보다': 83,
            '더': 84,
            '많이': 85,
            '조금': 86,
            '약간': 87,
            '별로': 88,
            '괜찮다': 89,
            '좋지': 90,
            '않다': 91,
            '것': 92,
            '같다': 93,
            '이다': 94,
            '어요': 95,
            '아요': 96,
            '해요': 97,
            '되다': 98,
            '하다': 99
        }
        
        self.id_to_token = {v: k for k, v in self.token_to_id.items()}
        self.vocab_size = len(self.token_to_id)
    
    def encode(self, utterance):
        """발화를 임베딩 벡터로 인코딩"""
        # 발화를 토큰으로 분리
        tokens = self._tokenize(utterance)
        
        # 토큰을 ID로 변환
        token_ids = []
        for token in tokens:
            if token in self.token_to_id:
                token_ids.append(self.token_to_id[token])
            else:
                token_ids.append(self.token_to_id['<UNK>'])
        
        # 임베딩 계산
        if len(token_ids) == 0:
            # 빈 발화의 경우
            return np.zeros(self.dim, dtype=np.float32)
        
        # 평균 임베딩 계산
        token_tensor = torch.tensor(token_ids, dtype=torch.long)
        embeddings = self.embedding(token_tensor)
        mean_embedding = torch.mean(embeddings, dim=0)
        
        return mean_embedding.detach().numpy().astype(np.float32)
    
    def _tokenize(self, utterance):
        """발화를 토큰으로 분리"""
        # 간단한 토큰화 (공백 기준)
        tokens = utterance.split()
        
        # 특수 토큰 처리
        processed_tokens = []
        for token in tokens:
            # 숫자와 함께 있는 경우 (예: "1번", "2번")
            if token.endswith('번'):
                processed_tokens.append(token)
            else:
                processed_tokens.append(token)
        
        return processed_tokens

