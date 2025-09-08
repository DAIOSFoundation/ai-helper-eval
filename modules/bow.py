# -*- coding: utf-8 -*-

import numpy as np
from collections import Counter
import re

class BoW_encoder:
    def __init__(self):
        # 한국어 심리 진단 관련 어휘
        self.vocab = {
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
            '이다': 95,
            '어요': 96,
            '아요': 97,
            '해요': 98,
            '되다': 99,
            '하다': 100
        }
        
        self.vocab_size = len(self.vocab)
        self.reverse_vocab = {v: k for k, v in self.vocab.items()}
    
    def encode(self, utterance):
        """발화를 Bag of Words 벡터로 인코딩"""
        # 발화 전처리
        utterance = self._preprocess(utterance)
        
        # 단어 분리
        words = utterance.split()
        
        # BoW 벡터 생성
        bow_vector = np.zeros(self.vocab_size, dtype=np.float32)
        
        for word in words:
            if word in self.vocab:
                bow_vector[self.vocab[word]] += 1
            else:
                bow_vector[self.vocab['<UNK>']] += 1
        
        return bow_vector
    
    def _preprocess(self, utterance):
        """발화 전처리"""
        # 특수문자 제거
        utterance = re.sub(r'[^\w\s]', ' ', utterance)
        
        # 공백 정규화
        utterance = re.sub(r'\s+', ' ', utterance)
        
        # 소문자 변환
        utterance = utterance.lower()
        
        return utterance.strip()
    
    def decode(self, bow_vector):
        """BoW 벡터를 단어로 디코딩"""
        words = []
        for i, count in enumerate(bow_vector):
            if count > 0:
                word = self.reverse_vocab.get(i, '<UNK>')
                words.extend([word] * int(count))
        return ' '.join(words)

