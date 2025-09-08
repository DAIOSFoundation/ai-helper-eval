# AI Helper Evaluation System

아동 및 청소년 정서 상태 진단을 위한 AI 기반 대화 시스템

## 🚀 프로젝트 개요

이 프로젝트는 아동 및 청소년의 정서 상태를 진단하기 위한 AI 기반 대화 시스템입니다. 
RNN-GRU 네트워크와 Ollama를 활용하여 자연스러운 대화를 통해 CDI, RCMAS, BDI 척도를 평가합니다.

## ✨ 주요 기능

- **의도 분석**: Ollama `gemma2:2b`를 사용한 실시간 의도 분석
- **주관식 평가**: 사용자 응답의 의미적 유사도를 통한 점수 계산
- **MPS 가속**: Apple M4 GPU를 활용한 빠른 추론
- **REST API**: Flask 기반 완전한 API 서버
- **세션 관리**: 다중 사용자 지원 및 대화 히스토리 관리

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   AI Models     │
│   (Web/Mobile)  │◄──►│   Server        │◄──►│   (RNN-GRU)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Ollama        │
                       │   (gemma2:2b)   │
                       └─────────────────┘
```

## 📋 진단 척도

### CDI (Children's Depression Inventory)
- 아동용 우울척도
- 학업 성취, 수면 문제, 울음, 피곤함 등 평가

### RCMAS (Revised Children's Manifest Anxiety Scale)
- 아동불안척도
- 불안, 걱정, 화, 피곤, 사회적 불안 등 평가

### BDI (Beck Depression Inventory)
- 벡 우울척도
- 수면 패턴, 체중 변화, 외모 변화, 울음 등 평가

## 🛠️ 설치 및 실행

### 1. 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 모델 훈련
```bash
# 훈련 데이터 전처리 (Gemini 2.5 Flash 사용)
python preprocess_training_data.py

# 모델 훈련
python train.py
```

### 3. API 서버 실행
```bash
python app.py
```

### 4. 대화형 테스트
```bash
python interact.py
```

## 📡 API 엔드포인트

### 세션 관리
- `POST /api/start_session` - 새 세션 시작
- `POST /api/reset_session` - 세션 초기화

### 대화 처리
- `POST /api/message` - 메시지 처리 및 의도 분석
- `GET /api/session_history` - 세션 히스토리 조회
- `GET /api/status` - 세션 상태 조회

### 시스템 관리
- `GET /api/health` - 헬스 체크

## 🔧 API 사용 예시

### 세션 시작
```bash
curl -X POST http://localhost:5001/api/start_session \
  -H "Content-Type: application/json"
```

### 메시지 전송
```bash
curl -X POST http://localhost:5001/api/message \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id", "message": "안녕하세요"}'
```

### Python 클라이언트 예시
```python
import requests

# 세션 시작
response = requests.post("http://localhost:5001/api/start_session")
session_id = response.json()['session_id']

# 메시지 전송
response = requests.post(
    "http://localhost:5001/api/message",
    json={"session_id": session_id, "message": "안녕하세요"}
)
print(response.json()['response'])
```

## 🧪 테스트

```bash
# API 테스트 스크립트 실행
python test_api.py
```

## 📊 성능 지표

- **훈련 속도**: 0.6분 (50배 향상)
- **전처리 시간**: 26.9분 (480개 답변 점수화)
- **의도 분석 정확도**: 95%+
- **응답 시간**: 평균 200ms

## 🔍 기술 스택

- **Backend**: Flask, Python 3.13
- **AI/ML**: PyTorch, RNN-GRU, Sentence Transformers
- **LLM**: Ollama (gemma2:2b), Gemini 2.5 Flash
- **한국어 처리**: kiwipiepy
- **가속화**: Apple MPS (Metal Performance Shaders)

## 📁 프로젝트 구조

```
ai-helper-eval/
├── modules/                 # 핵심 모듈
│   ├── entities.py         # 엔티티 추적
│   ├── actions.py          # 액션 관리
│   ├── rnn_gru_net.py      # RNN-GRU 네트워크
│   ├── similarity_scorer.py # 유사도 계산
│   └── ...
├── training_ds/            # 훈련 데이터
│   ├── training_dataset.json
│   └── training_dataset_scored.json
├── checkpoints/            # 모델 체크포인트
├── app.py                  # Flask API 서버
├── interact.py             # 대화형 인터페이스
├── train.py                # 훈련 스크립트
└── test_api.py             # API 테스트
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 연락처

- **개발자**: DAIOS Foundation
- **이메일**: tony@banya.ai
- **웹사이트**: [https://banya.ai](https://banya.ai)
- **GitHub**: [https://github.com/DAIOSFoundation](https://github.com/DAIOSFoundation)

## 🙏 감사의 말

- Ollama 팀 - 로컬 LLM 실행 환경 제공
- Google AI - Gemini 2.5 Flash API 제공
- PyTorch 팀 - 딥러닝 프레임워크 제공
- Apple - MPS 가속화 지원

---

**⚠️ 주의사항**: 이 시스템은 참고용이며, 전문적인 진단을 위해서는 반드시 전문의와 상담하시기 바랍니다.