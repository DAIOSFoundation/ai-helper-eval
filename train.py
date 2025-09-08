# -*- coding: utf-8 -*-

import os
import sys
import torch
import gc
import time
from datetime import datetime

# MPS 가속을 위한 환경 변수 설정
os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

from modules.entities import EntityTracker
from modules.bow import BoW_encoder
from modules.rnn_gru_net import RNN_GRU_net
from modules.embed import UtteranceEmbed
from modules.actions import ActionTracker
from modules.similarity_scorer import SimilarityScorer
from modules.data_utils import Data
import modules.util as util
import numpy as np

class Trainer:
    def __init__(self):
        print("훈련 데이터 로딩 중...")
        
        # 컴포넌트 초기화
        self.et = EntityTracker()
        self.bow_enc = BoW_encoder()
        self.emb = UtteranceEmbed()
        self.at = ActionTracker(self.et)
        self.similarity_scorer = SimilarityScorer()
        
        # 데이터 로드
        self.dataset, self.dialog_indices = Data(self.et, self.at).trainset
        
        if not self.dataset:
            print("훈련 데이터가 없습니다. 프로그램을 종료합니다.")
            sys.exit(1)
        
        print(f"로드된 대화 수: {len(self.dialog_indices)}")
        print(f"총 턴 수: {len(self.dataset)}")
        
        # 훈련/검증 데이터 분할
        self._split_data()
        
        # 네트워크 초기화
        obs_size = self.emb.dim + self.bow_enc.vocab_size + self.et.num_features
        self.action_templates = self.at.get_action_templates()
        action_size = self.at.action_size
        nb_hidden = 128
        
        print(f"관찰 크기: {obs_size}")
        print(f"액션 크기: {action_size}")
        
        self.net = RNN_GRU_net(obs_size=obs_size,
                               action_size=action_size,
                               nb_hidden=nb_hidden)
    
    def _split_data(self):
        """훈련/검증 데이터 분할"""
        total_dialogs = len(self.dialog_indices)
        train_ratio = 0.8
        
        train_size = int(total_dialogs * train_ratio)
        
        # 랜덤 셔플
        indices = list(range(total_dialogs))
        np.random.shuffle(indices)
        
        self.dialog_indices_tr = [self.dialog_indices[i] for i in indices[:train_size]]
        self.dialog_indices_dev = [self.dialog_indices[i] for i in indices[train_size:]]
        
        print(f"훈련 대화 수: {len(self.dialog_indices_tr)}")
        print(f"검증 대화 수: {len(self.dialog_indices_dev)}")
    
    def train(self):
        print('\n🚀 훈련 시작')
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        epochs = 20
        start_time = time.time()
        
        # Early stopping 설정
        patience = 5  # 5 에포크 동안 개선이 없으면 조기 종료
        min_delta = 0.001  # 최소 개선 임계값
        best_loss = float('inf')
        patience_counter = 0
        best_model_state = None
        
        # 훈련 히스토리 저장
        training_history = {
            'epoch': [],
            'train_loss': [],
            'response_accuracy': [],
            'dialogue_accuracy': [],
            'epoch_time': []
        }
        
        for epoch in range(epochs):
            epoch_start_time = time.time()
            
            print(f"\n{'='*60}")
            print(f"🔄 에포크 {epoch+1}/{epochs} 시작")
            print(f"시작 시간: {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*60}")
            
            # 훈련
            train_loss = self._train_epoch(epoch+1, epochs)
            
            # 검증
            per_response_accuracy, per_dialogue_accuracy = self.evaluate(epoch+1, epochs)
            
            # 에포크 소요 시간 계산
            epoch_time = time.time() - epoch_start_time
            total_time = time.time() - start_time
            
            # 결과 출력
            print(f"\n📊 에포크 {epoch+1}/{epochs} 결과:")
            print(f"   훈련 손실: {train_loss:.4f}")
            print(f"   응답 정확도: {per_response_accuracy:.4f} ({per_response_accuracy*100:.1f}%)")
            print(f"   대화 정확도: {per_dialogue_accuracy:.4f} ({per_dialogue_accuracy*100:.1f}%)")
            print(f"   에포크 소요 시간: {epoch_time:.1f}초")
            print(f"   총 소요 시간: {total_time/60:.1f}분")
            
            # Early stopping 체크
            if train_loss < best_loss - min_delta:
                best_loss = train_loss
                patience_counter = 0
                # 최고 성능 모델 저장
                best_model_state = self.net.state_dict().copy()
                print(f"   🎯 새로운 최고 성능! 손실: {best_loss:.4f}")
            else:
                patience_counter += 1
                print(f"   ⏳ 개선 없음 ({patience_counter}/{patience})")
            
            # 히스토리 저장
            training_history['epoch'].append(epoch+1)
            training_history['train_loss'].append(train_loss)
            training_history['response_accuracy'].append(per_response_accuracy)
            training_history['dialogue_accuracy'].append(per_dialogue_accuracy)
            training_history['epoch_time'].append(epoch_time)
            
            # 진행률 및 예상 완료 시간
            progress = (epoch+1) / epochs * 100
            if epoch > 0:
                avg_epoch_time = sum(training_history['epoch_time']) / len(training_history['epoch_time'])
                remaining_epochs = epochs - (epoch + 1)
                estimated_remaining_time = remaining_epochs * avg_epoch_time
                print(f"   전체 진행률: {progress:.1f}%")
                print(f"   예상 남은 시간: {estimated_remaining_time/60:.1f}분")
            
            # Early stopping 체크
            if patience_counter >= patience:
                print(f"\n🛑 Early Stopping! {patience} 에포크 동안 개선이 없었습니다.")
                print(f"   최고 손실: {best_loss:.4f} (에포크 {training_history['epoch'][training_history['train_loss'].index(best_loss)]})")
                break
            
            print(f"{'='*60}")
        
        # 최고 성능 모델 복원 및 저장
        if best_model_state is not None:
            self.net.load_state_dict(best_model_state)
            print(f"\n💾 최고 성능 모델 복원 완료 (손실: {best_loss:.4f})")
        
        # 모델 저장
        self.net.save()
        total_training_time = time.time() - start_time
        
        print(f"\n🎉 훈련 완료!")
        print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"총 훈련 시간: {total_training_time/60:.1f}분")
        print(f"실제 훈련 에포크: {len(training_history['epoch'])}/{epochs}")
        
        # 최종 결과 요약
        print(f"\n📈 최종 훈련 결과:")
        print(f"   최종 훈련 손실: {training_history['train_loss'][-1]:.4f}")
        print(f"   최종 응답 정확도: {training_history['response_accuracy'][-1]:.4f} ({training_history['response_accuracy'][-1]*100:.1f}%)")
        print(f"   최종 대화 정확도: {training_history['dialogue_accuracy'][-1]:.4f} ({training_history['dialogue_accuracy'][-1]*100:.1f}%)")
        print(f"   평균 에포크 시간: {sum(training_history['epoch_time'])/len(training_history['epoch_time']):.1f}초")
    
    def _train_epoch(self, current_epoch, total_epochs):
        """한 에포크 훈련 (실시간 진행 상황 표시)"""
        total_loss = 0.0
        num_examples = 0
        
        print(f"  🔄 훈련 대화 수: {len(self.dialog_indices_tr)}")
        
        for i, dialog_idx in enumerate(self.dialog_indices_tr):
            start, end = dialog_idx['start'], dialog_idx['end']
            dialog = self.dataset[start:end]
            
            # 대화별 훈련
            loss = self._train_dialog(dialog)
            total_loss += loss * len(dialog)
            num_examples += len(dialog)
            
            # 실시간 진행 상황 표시 (10개마다, 출력 오버헤드 감소)
            if (i + 1) % 10 == 0:
                progress = (i + 1) / len(self.dialog_indices_tr) * 100
                avg_loss = total_loss / num_examples if num_examples > 0 else 0.0
                print(f"    진행: {i+1}/{len(self.dialog_indices_tr)} 대화 완료 ({progress:.1f}%) - 평균 손실: {avg_loss:.4f}")
                
                # MPS 메모리 관리 (빈도 감소)
                if torch.backends.mps.is_available():
                    torch.mps.empty_cache()
                    torch.mps.synchronize()
                gc.collect()
        
        avg_loss = total_loss / num_examples if num_examples > 0 else 0.0
        print(f"  ✅ 에포크 {current_epoch} 훈련 완료 - 평균 손실: {avg_loss:.4f}")
        
        return avg_loss
    
    def _train_dialog(self, dialog):
        """대화별 훈련 (주관식 평가 기반, 속도 최적화)"""
        # 엔티티 트래커와 액션 트래커 초기화
        et = EntityTracker()
        at = ActionTracker(et)
        
        # 네트워크 상태 초기화
        self.net.reset_state()
        
        total_loss = 0.0
        valid_examples = 0
        
        # 배치 처리를 위한 데이터 수집
        batch_features = []
        batch_targets = []
        batch_masks = []
        
        for turn_data in dialog:
            if isinstance(turn_data, tuple):
                # 기존 형식: (user_utterance, target_action)
                user_utterance, target_action = turn_data
                precomputed_score = None
            else:
                # 새로운 형식: 딕셔너리 (점수화된 데이터)
                user_utterance = turn_data.get('utterance')
                target_action = turn_data.get('action')
                precomputed_score = turn_data.get('score')
            
            if user_utterance is None or target_action is None:
                continue
            
            try:
                # 현재 질문에 대한 평가 항목 설정
                at.set_current_evaluation(target_action)
                
                # 특성 추출 (점수화된 데이터 사용)
                features = self._extract_features(user_utterance, et, precomputed_score)
                
                # 액션 마스크
                action_mask = at.action_mask
                
                # 배치에 추가
                batch_features.append(features)
                batch_targets.append(target_action)
                batch_masks.append(action_mask)
                
            except Exception as e:
                print(f"특성 추출 오류 (건너뜀): {e}")
                continue
        
        # 배치별 훈련 (더 효율적)
        if batch_features:
            for features, target, mask in zip(batch_features, batch_targets, batch_masks):
                try:
                    loss = self.net.train_step(features, target, mask)
                    total_loss += loss
                    valid_examples += 1
                except Exception as e:
                    print(f"훈련 스텝 오류 (건너뜀): {e}")
                    continue
        
        return total_loss / valid_examples if valid_examples > 0 else 0.0
    
    def _extract_features(self, utterance, et, precomputed_score=None):
        """발화에서 특성 추출 (점수화된 데이터 지원)"""
        # 엔티티 추출 (점수화된 데이터 우선 사용)
        u_ent, u_entities = et.extract_entities(
            utterance, 
            is_test=False, 
            similarity_scorer=self.similarity_scorer,
            precomputed_score=precomputed_score
        )
        u_ent_features = et.context_features()
        
        # 임베딩
        u_emb = self.emb.encode(utterance)
        u_bow = self.bow_enc.encode(utterance)
        
        # 특성 결합
        features = np.concatenate((u_ent_features, u_emb, u_bow), axis=0)
        
        return features  # numpy 배열로 반환 (RNN_GRU_net에서 텐서로 변환)
    
    def evaluate(self, current_epoch, total_epochs):
        """모델 평가 (실시간 진행 상황 표시)"""
        self.net.eval()
        
        dialog_accuracy = 0.0
        correct_dialogue_count = 0
        
        print(f"  🔍 검증 대화 수: {len(self.dialog_indices_dev)}")
        
        for i, dialog_idx in enumerate(self.dialog_indices_dev):
            start, end = dialog_idx['start'], dialog_idx['end']
            dialog = self.dataset[start:end]
            
            # 대화별 평가
            correct_examples = self._evaluate_dialog(dialog)
            
            # 대화 완전 정확도
            if correct_examples == len(dialog):
                correct_dialogue_count += 1
            
            # 응답 정확도
            dialog_accuracy += correct_examples / len(dialog)
            
            # 실시간 진행 상황 표시 (5개마다, 출력 오버헤드 감소)
            if (i + 1) % 5 == 0:
                progress = (i + 1) / len(self.dialog_indices_dev) * 100
                current_accuracy = dialog_accuracy / (i + 1)
                print(f"    검증 진행: {i+1}/{len(self.dialog_indices_dev)} 대화 완료 ({progress:.1f}%) - 현재 정확도: {current_accuracy:.4f}")
        
        num_dev_examples = len(self.dialog_indices_dev)
        per_response_accuracy = dialog_accuracy / num_dev_examples if num_dev_examples > 0 else 0.0
        per_dialogue_accuracy = correct_dialogue_count / num_dev_examples if num_dev_examples > 0 else 0.0
        
        print(f"  ✅ 에포크 {current_epoch} 검증 완료 - 응답 정확도: {per_response_accuracy:.4f}, 대화 정확도: {per_dialogue_accuracy:.4f}")
        
        return per_response_accuracy, per_dialogue_accuracy
    
    def _evaluate_dialog(self, dialog):
        """대화별 평가"""
        # 엔티티 트래커와 액션 트래커 초기화
        et = EntityTracker()
        at = ActionTracker(et)
        
        # 네트워크 상태 초기화
        self.net.reset_state()
        
        correct_examples = 0
        
        for turn_data in dialog:
            if isinstance(turn_data, tuple):
                # 기존 형식: (user_utterance, target_action)
                user_utterance, target_action = turn_data
            else:
                # 새로운 형식: 딕셔너리 (점수화된 데이터)
                user_utterance = turn_data.get('utterance')
                target_action = turn_data.get('action')
            if user_utterance is None or target_action is None:
                continue
            
            # 특성 추출
            features = self._extract_features(user_utterance, et)
            
            # 액션 마스크
            action_mask = at.action_mask
            
            # 예측
            prediction = self.net.forward(features, action_mask)
            
            # 정확도 계산
            if prediction == target_action:
                correct_examples += 1
        
        return correct_examples

if __name__ == '__main__':
    # 랜덤 시드 설정
    util.set_seed(42)
    
    # 훈련 시작
    trainer = Trainer()
    trainer.train()
