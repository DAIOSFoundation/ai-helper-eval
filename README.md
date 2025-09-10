# AI Helper Evaluation System

아동 및 청소년 정서 상태 진단을 위한 AI 기반 대화 시스템

## 🚀 프로젝트 개요

이 프로젝트는 아동 및 청소년의 정서 상태를 진단하기 위한 AI 기반 대화 시스템입니다. 
React-Vite 클라이언트와 Flask 백엔드를 통해 자연스러운 대화로 CDI, RCMAS, BDI 척도를 평가합니다.

## 📋 최근 업데이트 (2025-09-10)

### 🔒 보안 및 권한 관리 (v1.6.1)
- **권한 기반 UI 제어**: 사용자 권한에 따른 메뉴 표시 제어
- **AI 관리 페이지 접근 제한**: 관리자만 AI 모델 관리 페이지 접근 가능
- **사이드바 메뉴 필터링**: 권한별 사이드바 메뉴 동적 필터링
- **네비게이션 보안**: 직접 URL 접근 및 프로그래밍적 접근 차단
- **API 헤더 인코딩 수정**: 한글 헤더 값의 ISO-8859-1 호환성 문제 해결

### 🎨 UI/UX 개선 (v1.6.0)
- **Tailwind CSS 제거**: 커스텀 CSS로 전환하여 더 안정적인 스타일링
- **사이드바 메뉴 구조**: 대시보드를 좌측 사이드바 메뉴로 재구성
- **통일된 버튼 스타일**: 모든 버튼에 `btn-unified` 클래스 적용
- **전체 페이지 상세 보고서**: 모달에서 전체 페이지로 변경

### 🔧 기능 개선
- **사용자 통계 그래프**: Chart.js를 사용한 점수 추이 그래프 구현
- **전체 사용자 진행률**: 관리자용 전체 사용자 테스트 진행률 표시
- **정확한 사용자 수**: 전체 통계에서 실제 등록된 사용자 수 표시
- **세션 목록 스타일**: 모든 사용자 테스트 세션 타이틀 스타일 통일

### 🏷️ 브랜딩 변경
- **애플리케이션 제목**: "AI Helper Evaluation" → "AI Helper Admin"

## ✨ 주요 기능

### 🎯 핵심 기능
- **통합 대화 시스템**: 일반 대화 중 트리거 키워드 감지로 자동 진단 시작
- **3가지 진단 테스트**: CDI, RCMAS, BDI 각 20문항씩 완전한 평가
- **역할 기반 권한**: 관리자/전문가/사용자별 차별화된 접근 권한
- **실시간 의도 분석**: Ollama `gemma2:2b`를 사용한 정확한 의도 파악

### 🖥️ 사용자 인터페이스
- **React-Vite 클라이언트**: 현대적이고 반응형 웹 인터페이스
- **사용자 인증**: 이메일 기반 회원가입/로그인 시스템
- **대시보드**: 사용자별 진행률 및 통계 시각화
- **관리자 패널**: 전체 사용자 현황 및 세션 관리

### 🔧 백엔드 시스템
- **Flask REST API**: 완전한 RESTful API 서버
- **SQLite 데이터베이스**: 사용자, 세션, 응답 데이터 관리
- **세션 관리**: UUID 기반 다중 사용자 지원
- **전문가 피드백**: 휴먼 피드백을 통한 모델 개선

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Client  │    │   Flask API     │    │   SQLite DB     │
│   (Vite/TS)     │◄──►│   Server        │◄──►│   (Users)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │      Gemini     │    │     Gemini      │
                       │   (2.5 Falsh)   │ ──►│   (2.5 Flash)   │
                       │      의도분석     │    │      일반대화      │
                       └─────────────────┘    └─────────────────┘       
                              │
                              ▼                
                       ┌─────────────────┐
                       │   Ollama        │
                       │   (gemma2:2b)   │
                       │   심리검사 의도분석  │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   AI Models     │
                       │   (RNN-GRU)     │
                       │   심리검사 평가    │
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

### 1. 백엔드 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 모델 훈련 (선택사항)
python train.py

# Flask API 서버 실행
python app.py
```

### 2. 프론트엔드 설정
```bash
# 클라이언트 디렉토리로 이동
cd client

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### 3. 접속
- **클라이언트**: http://localhost:5173
- **API 서버**: http://localhost:5001
- **API 문서**: http://localhost:5001/api/health

## 📡 API 엔드포인트

### 사용자 인증
- `POST /api/auth/register` - 사용자 회원가입
- `POST /api/auth/login` - 사용자 로그인

### 세션 관리
- `POST /api/start_session` - 새 세션 시작
- `POST /api/message` - 메시지 처리 및 의도 분석

### 대시보드
- `GET /api/dashboard/stats` - 대시보드 통계
- `GET /api/dashboard/sessions` - 사용자 세션 목록
- `GET /api/dashboard/session/<id>` - 세션 상세 정보
- `GET /api/dashboard/session/<id>/grouped-scores` - 세션 그룹별 점수
- `GET /api/dashboard/progress/<user_id>` - 사용자별 진행률
- `GET /api/admin/all-users-progress` - 모든 사용자 진행률 (관리자)
- `GET /api/admin/all-sessions` - 모든 사용자 세션 (관리자/전문가)

### 전문가 피드백
- `PUT /api/expert/score/<response_id>` - 전문가 점수 업데이트
- `POST /api/expert/feedback` - 전문가 피드백 제출
- `GET /api/expert/feedback/<id>` - 피드백 조회

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

### API 테스트
```bash
# API 헬스 체크
curl http://localhost:5001/api/health

# 세션 시작 테스트
curl -X POST http://localhost:5001/api/start_session \
  -H "Content-Type: application/json"

# 메시지 전송 테스트
curl -X POST http://localhost:5001/api/message \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id", "message": "안녕하세요"}'
```

### 프론트엔드 테스트
```bash
# 클라이언트 디렉토리로 이동
cd client

# 개발 서버 실행
npm run dev

# 빌드 테스트
npm run build
```

## 📊 성능 지표

- **훈련 속도**: 0.6분 (50배 향상)
- **전처리 시간**: 26.9분 (480개 답변 점수화)
- **의도 분석 정확도**: 95%+
- **응답 시간**: 평균 200ms

## 🔍 기술 스택

### Frontend
- **React 18**: 현대적인 UI 라이브러리
- **TypeScript**: 타입 안전성 보장
- **Vite**: 빠른 빌드 도구
- **Chart.js**: 데이터 시각화
- **Custom CSS**: 통일된 디자인 시스템

### Backend
- **Flask**: Python 웹 프레임워크
- **SQLite**: 경량 데이터베이스
- **Python 3.13**: 최신 Python 버전

### AI/ML
- **PyTorch**: 딥러닝 프레임워크
- **RNN-GRU**: 순환 신경망 모델
- **Sentence Transformers**: 문장 임베딩
- **Ollama (gemma2:2b)**: 로컬 LLM 실행
- **Gemini 2.5 Flash**: 클라우드 LLM API

### 한국어 처리
- **kiwipiepy**: 한국어 형태소 분석

### 가속화
- **Apple MPS**: Metal Performance Shaders

## 📁 프로젝트 구조

```
ai-helper-eval/
├── client/                     # React-Vite 프론트엔드
│   ├── src/
│   │   ├── api/               # API 클라이언트
│   │   │   ├── auth.ts        # 인증 API
│   │   │   ├── dashboard.ts   # 대시보드 API
│   │   │   ├── session.ts     # 세션 API
│   │   │   └── client.ts      # Axios 설정
│   │   ├── components/        # React 컴포넌트
│   │   │   ├── Auth/          # 인증 컴포넌트
│   │   │   ├── Dashboard/     # 대시보드 컴포넌트
│   │   │   ├── Expert/        # 전문가 피드백
│   │   │   ├── Reporting/     # 리포팅
│   │   │   ├── Test/          # 테스트 인터페이스
│   │   │   ├── Layout/        # 레이아웃 컴포넌트
│   │   │   ├── Conversation/  # 대화형 테스트
│   │   │   ├── Admin/         # 관리자 기능
│   │   │   └── Settings/      # 설정 페이지
│   │   ├── data/              # 정적 데이터
│   │   │   └── sidebarMenuItems.json
│   │   ├── utils/             # 유틸리티 함수
│   │   ├── App.tsx            # 메인 앱 컴포넌트
│   │   ├── main.tsx           # 앱 진입점
│   │   └── index.css          # 통합 CSS 스타일
│   ├── package.json           # Node.js 의존성
│   └── vite.config.ts         # Vite 설정
├── modules/                   # 핵심 AI 모듈
│   ├── entities.py           # 엔티티 추적
│   ├── actions.py            # 액션 관리
│   ├── rnn_gru_net.py        # RNN-GRU 네트워크
│   ├── similarity_scorer.py  # 유사도 계산
│   ├── bow.py                # Bag of Words
│   ├── embed.py              # 임베딩 처리
│   └── util.py               # 유틸리티
├── training_ds/              # 훈련 데이터
│   └── training_dataset_scored.json
├── test_sheets/              # 진단 척도 PDF
│   ├── 아동용 우울증 척도.pdf
│   ├── 개정판 아동불안 척도.pdf
│   └── BDI 벡우울척도.pdf
├── checkpoints/              # 모델 체크포인트
├── app.py                    # Flask API 서버
├── database.py               # SQLite 데이터베이스 관리
├── keyword_extractor.py      # 키워드 추출
├── interact.py               # 대화형 인터페이스
├── train.py                  # 모델 훈련
├── requirements.txt          # Python 의존성
└── ai_helper_eval.db         # SQLite 데이터베이스
```

## 🤝 기여하기

이 프로젝트는 아동 및 청소년의 정서 상태 진단을 위한 AI 기반 대화 시스템입니다. 
기여를 통해 더 나은 진단 도구를 만들어가고자 합니다.

### 기여 방법
1. **Fork the Project** - 프로젝트를 포크합니다
2. **Create your Feature Branch** - `git checkout -b feature/AmazingFeature`
3. **Commit your Changes** - `git commit -m 'Add some AmazingFeature'`
4. **Push to the Branch** - `git push origin feature/AmazingFeature`
5. **Open a Pull Request** - 풀 리퀘스트를 생성합니다

### 기여 영역
- **UI/UX 개선**: 사용자 인터페이스 및 사용자 경험 향상
- **AI 모델 개선**: 진단 정확도 및 응답 품질 향상
- **새로운 진단 척도**: 추가적인 정서 상태 진단 도구
- **다국어 지원**: 다양한 언어로의 확장
- **성능 최적화**: 시스템 성능 및 응답 속도 개선
- **문서화**: 코드 문서화 및 사용자 가이드 개선

### 개발 가이드라인
- TypeScript를 사용한 타입 안전성 보장
- React 컴포넌트 기반 모듈화
- RESTful API 설계 원칙 준수
- 한국어 자연어 처리 최적화

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 연락처

- **개발자**: DAIOS Foundation
- **이메일**: tony@banya.ai
- **웹사이트**: [https://banya.ai](https://banya.ai)
- **GitHub**: [https://github.com/DAIOSFoundation](https://github.com/DAIOSFoundation)

## 🙏 감사의 말

### 핵심 기술 제공
- **Ollama 팀** - 로컬 LLM 실행 환경 및 gemma2:2b 모델 제공
- **Google AI** - Gemini 2.5 Flash API 및 클라우드 AI 서비스 제공
- **PyTorch 팀** - 딥러닝 프레임워크 및 RNN-GRU 모델 지원
- **Apple** - MPS (Metal Performance Shaders) 가속화 지원

### 오픈소스 라이브러리
- **React 팀** - 현대적인 UI 라이브러리 제공
- **Vite 팀** - 빠른 빌드 도구 및 개발 환경 제공
- **Chart.js 팀** - 데이터 시각화 라이브러리 제공
- **Flask 팀** - 경량 Python 웹 프레임워크 제공
- **SQLite 팀** - 경량 데이터베이스 엔진 제공

### 한국어 처리
- **kiwipiepy 팀** - 한국어 형태소 분석기 제공
- **Sentence Transformers 팀** - 다국어 문장 임베딩 모델 제공

---

**⚠️ 주의사항**: 이 시스템은 참고용이며, 전문적인 진단을 위해서는 반드시 전문의와 상담하시기 바랍니다.