# 아동 및 청소년 정서 상태 진단 시스템

이 프로젝트는 아동 및 청소년의 정서 상태를 진단하기 위한 대화형 AI 시스템입니다. CDI(아동용 우울척도), RCMAS(아동불안척도), BDI(벡 우울척도)를 기반으로 한 심리 진단을 제공합니다.

## 주요 기능

- **대화형 진단**: 자연어 대화를 통한 심리 상태 진단
- **다중 척도 평가**: CDI, RCMAS, BDI 세 가지 척도로 종합 평가
- **Flask API**: RESTful API를 통한 웹 서비스 제공
- **체크포인트 시스템**: 훈련된 모델 저장 및 로드
- **MPS 가속 지원**: Apple Silicon Mac에서 GPU 가속 (현재는 CPU 사용)

## 시스템 구조

```
├── modules/                 # 핵심 모듈들
│   ├── entities.py         # 엔티티 트래킹
│   ├── actions.py          # 액션 관리
│   ├── lstm_net.py         # LSTM 신경망
│   ├── bow.py              # Bag of Words 인코더
│   ├── embed.py            # 임베딩 레이어
│   ├── data_utils.py       # 데이터 처리
│   └── util.py             # 유틸리티 함수
├── training_ds/            # 훈련 데이터
│   └── ai_studio_code.json # 대화 데이터셋
├── checkpoints/            # 모델 체크포인트
│   └── model.pth          # 훈련된 모델
├── train.py               # 훈련 스크립트
├── interact.py            # 대화형 인터페이스
├── app.py                 # Flask API 서버
└── requirements.txt       # 의존성 패키지
```

## 설치 및 실행

### 1. 가상환경 설정

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 모델 훈련

```bash
python train.py
```

훈련이 완료되면 `checkpoints/model.pth`에 모델이 저장됩니다.

### 3. 대화형 인터페이스 실행

```bash
python interact.py
```

### 4. Flask API 서버 실행

```bash
python app.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

## API 사용법

### 세션 시작
```bash
curl -X POST http://localhost:5000/api/start_session
```

### 메시지 전송
```bash
curl -X POST http://localhost:5000/api/message \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id", "message": "안녕하세요"}'
```

### 세션 초기화
```bash
curl -X POST http://localhost:5000/api/reset_session \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id"}'
```

### 세션 히스토리 조회
```bash
curl http://localhost:5000/api/session_history?session_id=your-session-id
```

### 시스템 상태 확인
```bash
curl http://localhost:5000/api/health
```

## 진단 척도

### CDI (아동용 우울척도)
- 학업 성취, 수면 문제, 울음, 피곤함, 친구 관계 등 평가
- 0-2점 척도 (0: 정상, 1: 경미한 우울, 2: 우울 증상 주의)

### RCMAS (아동불안척도)
- 불안, 걱정, 화, 피곤, 속이 메슥거림 등 평가
- 0-1점 척도 (0: 정상, 1: 불안 증상)

### BDI (벡 우울척도)
- 수면 패턴, 체중 변화, 외모 변화, 울음, 자기비판 등 평가
- 0-3점 척도 (0: 정상, 1: 경미한 우울, 2: 중간 우울, 3: 심한 우울)

## 주의사항

- 이 시스템은 참고용이며, 전문적인 진단을 위해서는 전문의와 상담하시기 바랍니다.
- 진단 결과는 일반적인 가이드라인이며, 개인의 상황에 따라 다를 수 있습니다.
- 심각한 정서적 문제가 있다고 생각되면 즉시 전문가의 도움을 받으시기 바랍니다.

## 기술 스택

- **Python 3.8+**
- **PyTorch**: 딥러닝 프레임워크
- **Flask**: 웹 API 프레임워크
- **NumPy**: 수치 계산
- **scikit-learn**: 머신러닝 유틸리티

## 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.
