# 바이오뱅크 검체 이송 관리 자동화 시스템

두산 로봇(DART Platform / DART Studio) 기반으로 바이오뱅크 검체(튜브/랙) 이송을 자동화하는 DRL 프로젝트입니다.  
픽업/배치, 로그 기반 라우팅, 예외 처리(미검출/그립 실패/타임아웃) 등을 포함합니다.

---

## 1. 개요 (Overview)
- 대상: 튜브/랙 검체 이송 프로세스 자동화
- 제어 방식: DART Studio DRL(Task Writer 또는 Code 기반)
- 인터페이스: Digital I/O 기반 그리퍼 제어, 센서 입력(DI) 기반 상태 확인(선택)

---

## 2. 주요 기능 (Features)
- [ ] 랙 이송: A 저장고 → B 저장고
- [ ] 튜브 이송: 랙↔랙
- [ ] 로그 기반 목적지 결정(랙 위치/점유/이력)
- [ ] 그리퍼 제어(OPEN/CLOSE/ENABLE 등)
- [ ] 예외 처리
  - 미그립/놓침 감지(옵션: DI 피드백)
  - 타임아웃 및 재시도
  - 충돌/보호정지 대응(운영 절차 포함)

---

## 3. 시스템 구성 (System Architecture)
- Robot: Doosan Collaborative Robot (M0609)
- Controller: DART Platform, DART Studio
- Runtime: DART Studio (DRL)
- End-effector: 전동 그리퍼 (Digital Output 제어)
- Sensors (Optional): DI 기반 그립 완료/Force 등

---

## 4. 코드 규칙

### 4.1 버전 표기
- 모든 DRL 파일 최상단에 버전을 표기합니다.

예:

    # Version: v0.000
    # Change: Initial draft

### 4.2 버전 증가 규칙
- `vX.X00` : 소수점 첫째 자리(X) ↑ → **기능 구현/변화**
- `v0.0Y0` : 소수점 둘째 자리(Y) ↑ → **변수/파라미터/상수/구조(경미) 수정**
- `v0.00Z` : 소수점 셋째 자리(Z) ↑ → **버그 수정**

예시:
- `v0.000` → 초기
- `v0.100` → 기능 추가(예: 로그 기반 라우팅 구현)
- `v0.110` → 파라미터/변수명 정리
- `v0.111` → 그립 타임아웃 버그 수정

### 4.3 네이밍(권장)

#### 4.3.1 기본 표기 규칙(Case)
- **snake_case**: 변수/함수/모듈(파일)명, ROS 토픽/서비스/파라미터
  - 예) `grip_delay_s`, `open_gripper()`, `error_handling.drl`, `/tube/status`, `use_sim_time`
- **PascalCase(CapWords)**: 클래스명(사용 시)
  - 예) `TubeTransferProcess`, `GripperInterface`
- **UPPER_SNAKE_CASE**: 상수(고정 값)
  - 예) `MAX_RETRY`, `SAFE_Z_MM`
- **camelCase**: 기본적으로 사용하지 않음(외부 API/기존 규격에 맞출 때만 예외)

#### 4.3.2 프로젝트 네이밍 규칙
- Pose: `pose_<zone>_<action>_<index>[_safe|_pre|_post]`
  - 예) `pose_a_storage_pick_1_safe`, `pose_b_storage_place_3_pre`
- I/O: `do_*`(출력), `di_*`(입력)
  - 예) `do_gripper_open`, `di_grip_ok`
- 단위 포함 권장: `_mm`, `_s`, `_deg`
  - 예) `safe_z_mm`, `grip_delay_s`


---

## 5. 폴더 구조 (Structure)
```text
.
├── drl/
│   ├── main.drl                # 메인 시나리오(상태머신/시퀀스)
│   ├── motion_points.drl       # 포인트/좌표(posx/posj) 정의
│   ├── gripper_io.drl          # 그리퍼 I/O 함수(OPEN/CLOSE/ENABLE)
│   ├── error_handling.drl      # 예외처리/리트라이/타임아웃
│   └── utils.drl               # 공통 유틸(로그/타이머/상태)
├── docs/
│   ├── flowchart.md            # 작업 플로우(노션/머메이드 등)
│   ├── io_mapping.md           # DO/DI 맵핑 표
│   └── setup_guide.md          # DART Studio 실행/설정 가이드
├── assets/
│   ├── screenshots/            # 화면 캡처
│   └── videos/                 # 동작 영상(용량 큰 경우 업로드 주의)
├── .gitignore
└── README.md
