# -*- coding: utf-8 -*-

import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from tqdm import tqdm
import re
from kiwipiepy import Kiwi

class TrainingDataPreprocessor:
    def __init__(self):
        # .env 파일 로드
        load_dotenv()
        
        # Gemini API 설정
        api_key = os.getenv('Gemini_API_Key')
        if not api_key:
            raise ValueError("Gemini_API_Key가 .env 파일에 설정되지 않았습니다.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 한국어 형태소 분석기 (순수 Python 버전)
        self.kiwi = Kiwi()
        
        # 평가 기준 템플릿 (기존과 동일)
        self.evaluation_templates = {
            'cdi': {
                'academic_achievement': {
                    'positive': ['어렵지 않다', '쉽다', '잘하다', '괜찮다', '문제없다', '좋다', '재미있다', '성공하다'],
                    'moderate': ['노력하다', '어렵다', '힘들다', '조금 어렵다', '보통이다', '그럭저럭이다'],
                    'negative': ['매우 어렵다', '전혀 못하다', '포기하다', '실패하다', '나쁘다', '싫다', '지겹다']
                },
                'sleep_problems': {
                    'positive': ['잘 자다', '편안하다', '문제없다', '좋다', '괜찮다', '충분하다'],
                    'moderate': ['가끔 어렵다', '보통이다', '조금 어렵다', '힘들다', '그럭저럭이다'],
                    'negative': ['매우 어렵다', '전혀 못하다', '불면증', '잠들기 어렵다', '자주 깨다', '피곤하다']
                },
                'crying': {
                    'positive': ['울지 않다', '평소와 같다', '문제없다', '괜찮다', '안정적이다'],
                    'moderate': ['가끔 울다', '조금 더 울다', '보통이다', '그럭저럭이다'],
                    'negative': ['자주 울다', '항상 울다', '울고 싶다', '눈물이 나다', '슬프다']
                },
                'fatigue': {
                    'positive': ['피곤하지 않다', '활력있다', '에너지가 있다', '괜찮다', '건강하다'],
                    'moderate': ['가끔 피곤하다', '보통이다', '조금 피곤하다', '그럭저럭이다'],
                    'negative': ['항상 피곤하다', '매우 피곤하다', '기력이 없다', '무기력하다', '지치다']
                },
                'friendship': {
                    'positive': ['친구가 많다', '사람들과 잘 지내다', '인기가 있다', '좋다', '편하다'],
                    'moderate': ['친구가 조금 있다', '보통이다', '적당하다', '그럭저럭이다'],
                    'negative': ['친구가 없다', '사람들과 어렵다', '외롭다', '소외감', '어색하다']
                }
            },
            'rcmas': {
                'anxiety': {
                    'positive': ['걱정하지 않다', '평온하다', '안정적이다', '괜찮다'],
                    'negative': ['걱정이 많다', '불안하다', '초조하다', '긴장되다', '두렵다']
                },
                'anger': {
                    'positive': ['화를 내지 않다', '차분하다', '침착하다', '평온하다'],
                    'negative': ['화가 많다', '짜증이 나다', '성질이 급하다', '화를 잘 내다']
                },
                'physical_symptoms': {
                    'positive': ['건강하다', '문제없다', '괜찮다', '편안하다'],
                    'negative': ['속이 메슥거리다', '숨이 차다', '가슴이 답답하다', '몸이 아프다']
                }
            },
            'bdi': {
                'sleep_pattern': {
                    'positive': ['잘 자다', '편안하다', '문제없다', '괜찮다'],
                    'moderate': ['조금 어렵다', '가끔 어렵다', '보통이다'],
                    'negative': ['매우 어렵다', '전혀 못하다', '불면증', '자주 깨다']
                },
                'weight_change': {
                    'positive': ['변화없다', '안정적이다', '괜찮다'],
                    'moderate': ['조금 줄다', '조금 늘다', '보통이다'],
                    'negative': ['많이 줄다', '많이 늘다', '급격한 변화']
                },
                'appearance': {
                    'positive': ['괜찮다', '만족하다', '좋다', '문제없다'],
                    'moderate': ['보통이다', '그럭저럭이다'],
                    'negative': ['불만족하다', '싫다', '자신없다', '부끄럽다']
                }
            }
        }
        
        # 통계
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None
        }
    
    def _extract_korean_stems(self, text):
        """한국어 텍스트에서 어간 추출 (kiwipiepy 사용)"""
        if not text:
            return []
        
        try:
            # kiwipiepy를 사용한 형태소 분석
            morphs = self.kiwi.analyze(text)
            
            # 어간만 추출 (명사, 동사, 형용사, 부사)
            stems = []
            for token in morphs[0][0]:  # 첫 번째 문장의 첫 번째 분석 결과
                morph, pos, _, _ = token
                # 의미있는 품사만 추출
                if pos in ['NNG', 'NNP', 'NNB', 'VV', 'VA', 'VX', 'VCP', 'VCN', 'MAG', 'MAJ']:
                    stems.append(morph)
            
            return stems
            
        except Exception as e:
            print(f"kiwipiepy 분석 오류: {e}")
            # 폴백: 간단한 어간 추출
            stems = []
            words = text.split()
            
            for word in words:
                # 기본적인 어미 제거
                if word.endswith('요') or word.endswith('어요') or word.endswith('아요'):
                    word = word[:-1] if word.endswith('요') else word[:-2]
                elif word.endswith('다') or word.endswith('어') or word.endswith('아'):
                    word = word[:-1]
                elif word.endswith('고') or word.endswith('는') or word.endswith('을') or word.endswith('를'):
                    word = word[:-1]
                
                if word:
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
    
    def _create_evaluation_prompt(self, user_response, category, subcategory):
        """Gemini용 평가 프롬프트 생성"""
        category_names = {
            'cdi': 'CDI (아동 우울 척도)',
            'rcmas': 'RCMAS (아동 불안 척도)', 
            'bdi': 'BDI (벡 우울 척도)'
        }
        
        category_name = category_names.get(category, category)
        
        # 평가 기준 템플릿 가져오기
        templates = self.evaluation_templates[category][subcategory]
        
        # 평가 기준 텍스트 생성
        criteria_text = ""
        for level, keywords in templates.items():
            level_name = {
                'positive': '긍정적/정상',
                'moderate': '보통/중간',
                'negative': '부정적/문제'
            }.get(level, level)
            criteria_text += f"- {level_name}: {', '.join(keywords)}\n"
        
        # 사용자 답변의 어간 추출
        user_stems = self._extract_korean_stems(user_response)
        user_normalized = " ".join(user_stems) if user_stems else user_response
        
        prompt = f"""
다음은 {category_name}의 '{subcategory}' 항목에 대한 평가입니다.

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
    
    def calculate_similarity_score(self, user_response, category, subcategory):
        """Gemini를 사용한 유사도 점수 계산 (재시도 로직 포함)"""
        max_retries = 3
        base_delay = 2  # 기본 대기 시간 (초)
        
        for attempt in range(max_retries):
            try:
                prompt = self._create_evaluation_prompt(user_response, category, subcategory)
                
                # Gemini API 호출
                response = self.model.generate_content(prompt)
                
                if response and response.text:
                    score = self._extract_score_from_response(response.text, category)
                    return score
                else:
                    print(f"Gemini 응답이 비어있음: {user_response}")
                    return 1  # 기본값
                    
            except Exception as e:
                error_msg = str(e)
                print(f"Gemini API 오류 (시도 {attempt+1}/{max_retries}): {error_msg}")
                
                # 할당량 초과 오류인 경우 더 긴 대기
                if "429" in error_msg or "quota" in error_msg.lower():
                    delay = base_delay * (2 ** attempt)  # 지수 백오프
                    print(f"할당량 초과로 {delay}초 대기 중...")
                    time.sleep(delay)
                elif attempt < max_retries - 1:
                    # 다른 오류인 경우 짧은 대기
                    time.sleep(1)
                else:
                    # 마지막 시도에서도 실패하면 기본값 반환
                    print(f"최대 재시도 횟수 초과, 기본값 반환")
                    return 1
        
        return 1  # 기본값
    
    def preprocess_training_data(self, input_file, output_file, batch_size=10):
        """훈련 데이터 전처리 (점수화) - 배치 처리 + 프로그래스 바"""
        print(f"🚀 훈련 데이터 전처리 시작 (배치 크기: {batch_size})")
        print(f"입력 파일: {input_file}")
        print(f"출력 파일: {output_file}")
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 훈련 데이터 로드
        print("📂 훈련 데이터 로딩 중...")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.stats['start_time'] = time.time()
        self.stats['total_processed'] = len(data)
        
        # 전체 대화 수 계산
        total_conversations = len(data)
        total_batches = (total_conversations + batch_size - 1) // batch_size
        
        print(f"📊 총 {total_conversations}개 대화, {total_batches}개 배치로 처리")
        print("="*80)
        
        # 전체 진행률을 위한 프로그래스 바
        with tqdm(total=total_conversations, desc="전체 진행률", unit="대화", 
                 bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
            
            for batch_idx in range(total_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, total_conversations)
                batch_data = data[start_idx:end_idx]
                
                # 배치별 프로그래스 바
                batch_desc = f"배치 {batch_idx+1}/{total_batches}"
                with tqdm(batch_data, desc=batch_desc, unit="대화", 
                         leave=False, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]") as batch_pbar:
                    
                    for i, conversation in enumerate(batch_data):
                        global_idx = start_idx + i
                        
                        # 현재 진단 카테고리 추적
                        current_category = None
                        current_subcategory = None
                        user_responses_processed = 0
                        
                        # 각 발화 처리
                        for j, turn in enumerate(conversation):
                            if turn['speaker'] == 'system':
                                # 시스템 발화에서 메타데이터 확인
                                metadata = turn.get('metadata', {})
                                if 'category' in metadata and 'subcategory' in metadata:
                                    current_category = metadata['category']
                                    current_subcategory = metadata['subcategory']
                            
                            elif turn['speaker'] == 'user' and current_category and current_subcategory:
                                user_response = turn['utterance']
                                
                                # 점수 계산
                                score = self.calculate_similarity_score(user_response, current_category, current_subcategory)
                                
                                # 점수를 발화에 추가
                                turn['score'] = score
                                user_responses_processed += 1
                                self.stats['successful'] += 1
                                
                                # API 호출 간격 (할당량 제한 방지)
                                time.sleep(2)  # 2초 대기로 할당량 문제 방지
                        
                        # 배치 프로그래스 바 업데이트
                        batch_pbar.set_postfix({
                            '카테고리': f"{current_category}-{current_subcategory}" if current_category else "N/A",
                            '처리된답변': user_responses_processed,
                            '총성공': self.stats['successful']
                        })
                        batch_pbar.update(1)
                        
                        # 전체 프로그래스 바 업데이트
                        pbar.set_postfix({
                            '배치': f"{batch_idx+1}/{total_batches}",
                            '성공': self.stats['successful'],
                            '실패': self.stats['failed']
                        })
                        pbar.update(1)
                
                # 배치 완료 후 중간 저장
                tqdm.write(f"💾 배치 {batch_idx+1} 완료, 중간 저장 중...")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 배치별 통계
                elapsed = time.time() - self.stats['start_time']
                progress = (batch_idx + 1) / total_batches * 100
                avg_time = elapsed / (batch_idx + 1)
                remaining = (total_batches - (batch_idx + 1)) * avg_time
                
                tqdm.write(f"📊 배치 {batch_idx+1} 완료 - 진행률: {progress:.1f}%")
                tqdm.write(f"⏱️  경과: {elapsed/60:.1f}분, 예상 남은: {remaining/60:.1f}분")
                tqdm.write(f"✅ 성공: {self.stats['successful']}개, 실패: {self.stats['failed']}개")
                tqdm.write("-" * 60)
        
        # 최종 통계 출력
        total_time = time.time() - self.stats['start_time']
        print("\n" + "="*80)
        print("🎉 전처리 완료!")
        print("="*80)
        print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"총 소요 시간: {total_time/60:.1f}분")
        print(f"처리된 대화: {len(data)}개")
        print(f"성공한 점수화: {self.stats['successful']}개")
        print(f"실패한 점수화: {self.stats['failed']}개")
        print(f"평균 처리 시간: {total_time/len(data):.2f}초/대화")
        print(f"배치 크기: {batch_size}")
        print(f"처리 속도: {self.stats['successful']/(total_time/60):.1f} 답변/분")
        print("="*80)

def main():
    preprocessor = TrainingDataPreprocessor()
    
    # 파일 경로
    input_file = 'training_ds/training_dataset.json'
    output_file = 'training_ds/training_dataset_scored.json'
    
    # 전처리 실행
    preprocessor.preprocess_training_data(input_file, output_file)

if __name__ == '__main__':
    main()
