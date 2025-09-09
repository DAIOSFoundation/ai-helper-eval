
# -*- coding: utf-8 -*-
"""
RNN-GRU 네트워크 모듈
LSTM 대신 GRU를 사용하여 MPS 호환성을 개선한 대화 시스템 모델
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os

# MPS 가속 설정
def get_device():
    """사용 가능한 디바이스 반환 (MPS 안전성 개선)"""
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
        # MPS 사용 시 안전성을 위한 환경 변수 설정
        os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        # MPS 메모리 관리 개선
        torch.mps.set_per_process_memory_fraction(0.8)
        print("MPS 가속 활성화 (메모리 최적화)")
        return torch.device("mps")
    else:
        # CPU에서 멀티스레딩으로 성능 개선
        torch.set_num_threads(8)  # M4의 8코어 활용
        print("CPU 사용 (멀티스레딩 활성화)")
        return torch.device("cpu")

class RNN_GRU_net(nn.Module):
    """
    RNN-GRU 기반 대화 시스템 네트워크
    LSTM 대신 GRU를 사용하여 MPS에서 안정적으로 작동
    """
    def __init__(self, obs_size, action_size, nb_hidden=128):
        super(RNN_GRU_net, self).__init__()
        
        self.obs_size = obs_size
        self.action_size = action_size
        self.nb_hidden = nb_hidden
        
        # 디바이스 설정
        self.device = get_device()
        print(f"사용 디바이스: {self.device}")
        
        # GRU 레이어 (LSTM 대신 GRU 사용)
        self.gru = nn.GRU(obs_size, nb_hidden, batch_first=True)
        
        # 출력 레이어
        self.output_layer = nn.Linear(nb_hidden, action_size)
        
        # 활성화 함수
        self.softmax = nn.Softmax(dim=-1)
        
        # 옵티마이저
        self.optimizer = optim.Adam(self.parameters(), lr=0.001)
        
        # 손실 함수
        self.criterion = nn.CrossEntropyLoss()
        
        # 히든 상태 초기화 (GRU는 cell_state가 없음)
        self.hidden_state = None
        
        # 체크포인트 경로
        self.checkpoint_path = 'checkpoints/model.pth'
        
        # 모델을 디바이스로 이동
        self.to(self.device)
        
    def forward(self, features, action_mask=None):
        """순전파"""
        # 입력을 디바이스로 이동
        if not isinstance(features, torch.Tensor):
            features = torch.tensor(features, dtype=torch.float32)
        features = features.to(self.device)
        
        # 배치 차원 추가
        if len(features.shape) == 1:
            features = features.unsqueeze(0).unsqueeze(0)  # (1, 1, obs_size)
        elif len(features.shape) == 2:
            features = features.unsqueeze(0)  # (1, seq_len, obs_size)
        
        # 액션 마스크를 디바이스로 이동
        if action_mask is not None:
            if not isinstance(action_mask, torch.Tensor):
                action_mask = torch.tensor(action_mask, dtype=torch.float32)
            action_mask = action_mask.to(self.device)
        
        # 히든 상태 초기화 (첫 번째 호출인 경우)
        if self.hidden_state is None:
            batch_size = features.size(0)
            self.hidden_state = torch.zeros(1, batch_size, self.nb_hidden, device=self.device)
        
        # GRU 순전파 (cell_state 없음)
        gru_out, self.hidden_state = self.gru(features, self.hidden_state)
        
        # 마지막 출력 사용
        last_output = gru_out[:, -1, :]  # (batch_size, nb_hidden)
        
        # 출력 레이어
        logits = self.output_layer(last_output)  # (batch_size, action_size)
        
        # 액션 마스크 적용
        if action_mask is not None:
            if len(action_mask.shape) == 1:
                action_mask = action_mask.unsqueeze(0)  # (1, action_size)
            logits = logits * action_mask + (1 - action_mask) * (-1e9)
        
        # 소프트맥스 적용
        probs = self.softmax(logits)
        
        # 가장 높은 확률의 액션 선택
        action = torch.argmax(probs, dim=-1)
        
        return action.item()
    
    def train_step(self, features, target_action, action_mask=None):
        """훈련 스텝 (MPS 안전성 개선)"""
        self.train()
        
        try:
            # 입력을 디바이스로 이동
            if not isinstance(features, torch.Tensor):
                features = torch.tensor(features, dtype=torch.float32)
            features = features.to(self.device)
            
            # 배치 차원 추가
            if len(features.shape) == 1:
                features = features.unsqueeze(0).unsqueeze(0)
            elif len(features.shape) == 2:
                features = features.unsqueeze(0)
        
            # 타겟을 텐서로 변환하고 디바이스로 이동
            if isinstance(target_action, int):
                target = torch.tensor([target_action], dtype=torch.long)
            else:
                target = target_action
            target = target.to(self.device)
            
            # 액션 마스크를 디바이스로 이동
            if action_mask is not None:
                if not isinstance(action_mask, torch.Tensor):
                    action_mask = torch.tensor(action_mask, dtype=torch.float32)
                action_mask = action_mask.to(self.device)
            
            # 옵티마이저 초기화
            self.optimizer.zero_grad()
            
            # 히든 상태 초기화 (훈련 시에는 매번 초기화)
            batch_size = features.size(0)
            hidden_state = torch.zeros(1, batch_size, self.nb_hidden, device=self.device)
            
            # 순전파 (GRU는 cell_state 없음)
            gru_out, _ = self.gru(features, hidden_state)
            last_output = gru_out[:, -1, :]
            logits = self.output_layer(last_output)
            
            # 액션 마스크 적용
            if action_mask is not None:
                if len(action_mask.shape) == 1:
                    action_mask = action_mask.unsqueeze(0)
                logits = logits * action_mask + (1 - action_mask) * (-1e9)
            
            # 손실 계산
            loss = self.criterion(logits, target)
        
            # 역전파
            loss.backward()
            self.optimizer.step()
            
            return loss.item()
            
        except Exception as e:
            print(f"MPS 오류 발생, CPU로 폴백: {e}")
            # MPS 오류 시 CPU로 폴백
            self.device = torch.device("cpu")
            self.to(self.device)
            return self.train_step(features, target_action, action_mask)
    
    def reset_state(self):
        """히든 상태 초기화 (GRU는 cell_state 없음)"""
        self.hidden_state = None
    
    def save(self):
        """모델 저장"""
        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)
        torch.save({
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'obs_size': self.obs_size,
            'action_size': self.action_size,
            'nb_hidden': self.nb_hidden,
            'device': str(self.device)
        }, self.checkpoint_path)
        print(f"모델이 {self.checkpoint_path}에 저장되었습니다.")
    
    def restore(self):
        """모델 복원"""
        if os.path.exists(self.checkpoint_path):
            try:
                checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
                self.load_state_dict(checkpoint['model_state_dict'])
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                print(f"모델이 {self.checkpoint_path}에서 복원되었습니다.")
            except RuntimeError as e:
                if "size mismatch" in str(e):
                    print(f"모델 크기가 맞지 않습니다. 새로운 모델을 사용합니다. (기존 체크포인트: {self.checkpoint_path})")
                    # 기존 체크포인트를 백업하고 삭제
                    import shutil
                    backup_path = f"{self.checkpoint_path}.backup"
                    shutil.move(self.checkpoint_path, backup_path)
                    print(f"기존 체크포인트를 {backup_path}로 백업했습니다.")
                else:
                    raise e
        else:
            print("저장된 모델이 없습니다. 새로운 모델을 사용합니다.")
    
    def predict_proba(self, features, action_mask=None):
        """액션 확률 예측"""
        self.eval()
        with torch.no_grad():
            # 입력을 디바이스로 이동
            if not isinstance(features, torch.Tensor):
                features = torch.tensor(features, dtype=torch.float32)
            features = features.to(self.device)
            
            # 배치 차원 추가
            if len(features.shape) == 1:
                features = features.unsqueeze(0).unsqueeze(0)
            elif len(features.shape) == 2:
                features = features.unsqueeze(0)
            
            # 액션 마스크를 디바이스로 이동
            if action_mask is not None:
                if not isinstance(action_mask, torch.Tensor):
                    action_mask = torch.tensor(action_mask, dtype=torch.float32)
                action_mask = action_mask.to(self.device)
            
            # 히든 상태 초기화 (첫 번째 호출인 경우)
            if self.hidden_state is None or self.cell_state is None:
                batch_size = features.size(0)
                self.hidden_state = torch.zeros(1, batch_size, self.nb_hidden, device=self.device)
                self.cell_state = torch.zeros(1, batch_size, self.nb_hidden, device=self.device)
            
            # LSTM 순전파
            lstm_out, _ = self.lstm(features, (self.hidden_state, self.cell_state))
            last_output = lstm_out[:, -1, :]
            logits = self.output_layer(last_output)
            
            # 액션 마스크 적용
            if action_mask is not None:
                if len(action_mask.shape) == 1:
                    action_mask = action_mask.unsqueeze(0)
                logits = logits * action_mask + (1 - action_mask) * (-1e9)
            
            # 소프트맥스 적용
            probs = self.softmax(logits)
            
            return probs.squeeze(0).cpu().numpy()
