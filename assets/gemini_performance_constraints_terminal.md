
# 🛡️ Gemini Performance Constraints (Terminal / Python Doom Edition)

## 📌 Purpose
Python 터미널 기반, CPU 중심 환경에서 LLM이 생성하는 비효율적 코드(반복, 재계산, 과도한 연산)를 제어하고 프레임 안정성과 예측 가능한 성능을 보장한다.

---

## 1. Frame Execution Model

### ⚖️ Rule
프레임 루프는 고정 크기 기반 연산만 허용한다.

### ✅ Allowed
- 화면 버퍼 크기 기준 반복 (예: width × height)
- 고정 길이 배열 순회
- 단순 연산 (조건, 대입, 참조)

### 🚫 Forbidden
- 입력 크기 기반 반복 (동적 리스트 순회)
- 중첩 루프 (O(n²) 이상)
- 프레임마다 크기가 변하는 연산

---

## 2. Frame Budget (핵심 규칙)

### ⚖️ Rule
모든 프레임은 시간 예산 내에서만 실행되어야 한다.

### 기준
- 목표: 30~60 FPS
- 프레임당 예산: 약 16ms ~ 33ms

### 초과 시 처리
- 연산 축소
- 일부 업데이트 스킵
- 해상도 또는 처리 범위 축소

---

## 3. Controlled Loop Usage

### ⚖️ Rule
루프는 금지되지 않지만 엄격히 제한된다.

### 허용 조건
- 반복 횟수가 고정되어 있음
- 상한이 명확함 (예: 화면 크기)

### 🚫 Forbidden
- while 기반 무한 루프
- 종료 조건 불명확한 반복
- 데이터 크기에 따라 증가하는 루프

---

## 4. Recalculation Control

### ⚖️ Rule
상태가 변하지 않으면 계산하지 않는다.

### Required
- 캐싱 (Cached values)
- Dirty flag 사용

### 🚫 Forbidden
- 동일 값 반복 계산
- 프레임마다 전체 재계산

---

## 5. State-Driven Updates

### ⚖️ Rule
모든 로직은 상태 변화 기반으로 실행된다.

### 상태 정의
State = Input + Time + Internal State

### 🚫 Forbidden
- 상태와 무관한 연산
- 무조건 실행되는 업데이트

---

## 6. Allocation Constraints

### ⚖️ Rule
핫 패스(프레임 루프)에서 메모리 할당 금지

### 🚫 Forbidden
- 객체 생성 (new, append 등)
- 리스트/배열 크기 변경

### ✅ Required
- 사전 할당
- 메모리 재사용

---

## 7. CPU Budget Protection

### ⚖️ Rule
CPU는 최소한의 제어 로직만 담당한다.

### 원칙
- 반복 계산 최소화
- 동일 연산 재사용
- 계산 → 저장 → 재사용

---

## 8. LLM Forbidden Patterns

다음 패턴은 절대 생성 금지:

- 프레임 루프 내부의 동적 반복
- 중첩 루프
- 매 프레임 객체 생성
- 상태 변화 없는 재계산
- 숨겨진 O(n²) 이상 연산

---

## 9. Mandatory Review Checklist

코드 승인 전 반드시 확인:

- [ ] 프레임 루프는 고정 크기 반복인가?
- [ ] 프레임 예산을 초과하지 않는가?
- [ ] 불필요한 재계산이 제거되었는가?
- [ ] 메모리 할당이 핫 패스에 없는가?
- [ ] 상태 기반으로만 실행되는가?

---

## 💡 Final Principle

LLM은 항상 다음을 가정한다:

1. CPU는 제한적이다  
2. 프레임 유지가 최우선이다  
3. 반복은 비용이다  
4. 상태 변화만이 실행 트리거다  
5. 모든 연산은 예산 내에서 수행되어야 한다  

---

## 핵심 변화 요약 (의도)

- O(1 강제 제거 → 고정 크기 + 예산 기반)
- 루프 금지 제거 → 제어된 루프 허용
- GPU 전제 제거 → CPU 최적화 구조로 전환
