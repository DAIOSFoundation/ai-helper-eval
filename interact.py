# -*- coding: utf-8 -*-

from modules.entities import EntityTracker
from modules.bow import BoW_encoder
from modules.rnn_gru_net import RNN_GRU_net
from modules.embed import UtteranceEmbed
from modules.actions import ActionTracker
from modules.similarity_scorer import SimilarityScorer
import modules.util as util
import numpy as np
import torch

class InteractiveSession:
    def __init__(self):
        print("대화 시스템 초기화 중...")
        
        # 컴포넌트 초기화
        self.et = EntityTracker()
        self.bow_enc = BoW_encoder()
        self.emb = UtteranceEmbed()
        self.at = ActionTracker(self.et)
        self.similarity_scorer = SimilarityScorer()
        
        # 네트워크 초기화
        obs_size = self.emb.dim + self.bow_enc.vocab_size + self.et.num_features
        self.action_templates = self.at.get_action_templates()
        action_size = self.at.action_size
        nb_hidden = 128
        
        self.net = RNN_GRU_net(obs_size=obs_size,
                               action_size=action_size,
                               nb_hidden=nb_hidden)
        
        # 체크포인트 복원
        self.net.restore()
        
        print("대화 시스템이 준비되었습니다!")
    
    def interact(self):
        """대화 루프"""
        # 엔티티 트래커와 액션 트래커 초기화
        et = EntityTracker()
        at = ActionTracker(et)
        
        # 네트워크 상태 초기화
        self.net.reset_state()
        
        print("\n=== 아동 및 청소년 정서 상태 진단 시스템 ===")
        print("안녕하세요! 정서 상태를 알아보는 몇 가지 질문을 드릴게요.")
        print("명령어: 'clear' 또는 'reset' - 새 세션 시작, 'exit' 또는 'quit' - 종료\n")
        
        # 대화 루프
        while True:
            try:
                # 사용자 입력 받기
                user_input = input('사용자: ').strip()
                
                # 명령어 처리
                if user_input.lower() in ['clear', 'reset', 'restart']:
                    self.net.reset_state()
                    et = EntityTracker()
                    at = ActionTracker(et)
                    print("새로운 세션이 시작되었습니다.\n")
                    continue
                
                elif user_input.lower() in ['exit', 'stop', 'quit', 'q']:
                    print("진단을 종료합니다. 감사합니다!")
                    break
                
                # 빈 입력 처리
                if not user_input:
                    user_input = '<SILENCE>'
                
                # 사용자 의도 분석 (Ollama 기반, 시스템 질문 맥락 포함)
                # 이전 시스템 질문 가져오기
                last_system_question = getattr(self, '_last_system_question', None)
                intent = self.similarity_scorer.analyze_user_intent(user_input, last_system_question)
                print(f"[의도 분석: {intent}]")
                
                # 의도에 따른 액션 선택
                prediction = self._select_action_by_intent(intent, et, at, user_input)
                
                # 현재 질문에 대한 평가 항목 설정
                at.set_current_evaluation(prediction)
                
                # 질문 인덱스 업데이트
                if prediction > 0 and prediction < len(self.action_templates) - 1:
                    et.entities['current_question_index'] = prediction
                
                # 응답 생성
                response = self._generate_response(prediction, et, at)
                
                # 시스템 질문 저장 (다음 의도 분석을 위해)
                self._last_system_question = response
                
                print(f"시스템: {response}\n")
                
                # 진단 완료 확인
                if self._is_diagnosis_complete(et):
                    self._show_diagnosis_result(et)
                    break
                    
            except KeyboardInterrupt:
                print("\n진단을 종료합니다.")
                break
            except Exception as e:
                print(f"오류가 발생했습니다: {e}")
                continue
    
    def _extract_features(self, utterance, et):
        """발화에서 특성 추출 (주관식 평가 포함)"""
        # 엔티티 추출 (유사도 평가 포함)
        u_ent, u_entities = et.extract_entities(utterance, is_test=True, similarity_scorer=self.similarity_scorer)
        u_ent_features = et.context_features()
        
        # 임베딩
        u_emb = self.emb.encode(utterance)
        u_bow = self.bow_enc.encode(utterance)
        
        # 특성 결합
        features = np.concatenate((u_ent_features, u_emb, u_bow), axis=0)
        
        return features  # numpy 배열로 반환 (GRU_net에서 텐서로 변환)
    
    def _select_action_by_intent(self, intent, et, at, user_input):
        """의도에 따른 액션 선택"""
        current_question_index = et.entities['current_question_index']
        answered_questions = et.entities['answered_questions']
        
        if intent == 'greeting':
            # 인사에는 인사로 응답
            return 0
        elif intent == 'ready':
            # 준비됨 의도에는 다음 질문으로 진행
            if current_question_index == 0:
                return 1  # 첫 번째 CDI 질문
            elif current_question_index < 3:
                return current_question_index + 1  # 다음 질문
            else:
                return len(self.action_templates) - 1  # 결과 출력
        elif intent == 'answer':
            # 답변 의도에는 답변을 평가하고 다음 질문으로
            # 현재 질문에 대한 평가 항목이 설정되어 있는지 확인
            if et.entities['current_evaluation'] and current_question_index not in answered_questions:
                # 답변 평가 수행
                category, subcategory = et.entities['current_evaluation']
                score = self.similarity_scorer.calculate_similarity_score(
                    user_input, category, subcategory
                )
                print(f"[답변 평가: {category}-{subcategory} = {score}점]")
                
                # 평가 히스토리에 추가
                evaluation_record = {
                    'category': category,
                    'subcategory': subcategory,
                    'response': user_input,
                    'score': score,
                    'question_index': current_question_index
                }
                et.entities['evaluation_history'].append(evaluation_record)
                
                # 점수 업데이트
                if category == 'cdi':
                    if et.entities['cdi_score'] is None:
                        et.entities['cdi_score'] = 0
                    et.entities['cdi_score'] += score
                elif category == 'rcmas':
                    if et.entities['rcmas_score'] is None:
                        et.entities['rcmas_score'] = 0
                    et.entities['rcmas_score'] += score
                elif category == 'bdi':
                    if et.entities['bdi_score'] is None:
                        et.entities['bdi_score'] = 0
                    et.entities['bdi_score'] += score
                
                # 답변한 질문으로 표시
                answered_questions.add(current_question_index)
            
            # 다음 질문으로 진행 (3개 질문만)
            if current_question_index < 3:
                return current_question_index + 1
            else:
                return len(self.action_templates) - 1  # 결과 출력
        elif intent == 'confused':
            # 혼란 의도에는 현재 질문 반복
            if current_question_index == 0:
                return 1  # 첫 번째 질문
            else:
                return min(current_question_index, len(self.action_templates) - 2)
        elif intent == 'refuse':
            # 거부 의도에는 종료
            return len(self.action_templates) - 1
        else:
            # 기본값: 다음 질문으로 진행
            if current_question_index < 3:
                return current_question_index + 1
            else:
                return len(self.action_templates) - 1
    
    def _generate_response(self, prediction, et, at):
        """예측된 액션에 따른 응답 생성"""
        if prediction < len(self.action_templates):
            response = self.action_templates[prediction]
            
            # 진단 결과 출력인 경우
            if prediction == len(self.action_templates) - 1:  # 마지막 액션 (결과 출력)
                result = self._format_diagnosis_result(et)
                response += f" CDI 점수는 {result['cdi_score']}점, RCMAS 점수는 {result['rcmas_score']}점, BDI 점수는 {result['bdi_score']}점입니다."
            
            return response
        else:
            return "죄송합니다. 이해하지 못했습니다. 다시 말씀해 주세요."
    
    def _is_diagnosis_complete(self, et):
        """진단 완료 여부 확인 (3개 질문 완료)"""
        return len(et.entities['answered_questions']) >= 3
    
    def _format_diagnosis_result(self, et):
        """진단 결과 포맷팅"""
        return {
            'cdi_score': et.entities['cdi_score'] or 0,
            'rcmas_score': et.entities['rcmas_score'] or 0,
            'bdi_score': et.entities['bdi_score'] or 0
        }
    
    def _show_diagnosis_result(self, et):
        """진단 결과 출력"""
        result = self._format_diagnosis_result(et)
        
        print("\n=== 진단 완료 ===")
        print(f"CDI (아동 우울 척도) 점수: {result['cdi_score']}")
        print(f"RCMAS (아동 불안 척도) 점수: {result['rcmas_score']}")
        print(f"BDI (벡 우울 척도) 점수: {result['bdi_score']}")
        print("\n각 점수는 해당 영역의 심각도를 나타냅니다.")
        print("점수가 높을수록 해당 증상이 더 심각할 수 있습니다.")
        print("※ 이 결과는 참고용이며, 전문적인 진단을 위해서는 전문의와 상담하시기 바랍니다.")
        print("================\n")

if __name__ == '__main__':
    # 대화 세션 시작
    session = InteractiveSession()
    session.interact()
