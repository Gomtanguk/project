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
- Robot: Doosan Collaborative Robot (예: M0609 등)
- Controller: DART Platform, DART Studio
- Runtime: DART Studio (DRL)
- End-effector: 전동 그리퍼 (Digital Output 제어)
- Sensors (Optional): DI 기반 그립 완료/검체 존재/도어/인터락 등

---

## 4. 폴더 구조 (Structure)
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
