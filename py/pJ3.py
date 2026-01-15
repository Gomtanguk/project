# =========================================================
#  9 Blocks Classify Flow (12-step per block)
#  - A 트레이(A_1~A_9)에서 높이 측정(순응+Force) → High/Mid/Low 분류
#  - 분류 트레이 각 라인(0~2)에 순서대로 적재
# =========================================================

# -------------------------
# Gripper I/O (AS-IS 유지)
# -------------------------
def griping():
    # DO1 ON / DO2 OFF : 그립 닫기
    set_digital_output(1, ON)
    set_digital_output(2, OFF)
    wait(1.00)

def releasing():
    # DO1 OFF / DO2 ON : 그립 열기
    set_digital_output(1, OFF)
    set_digital_output(2, ON)
    wait(1.00)

# ---------------------------------------------------------
# Teach Points
#  - A_i : A 트레이 각 위치의 상단(접근) 포인트
#  - A_i_safe : 프로빙(측정) 시작 안전 포인트
#  - 분류 트레이(High/Mid/Low) : 각 홀의 기준(절대) 포인트
# ---------------------------------------------------------

# A 트레이 공통 Z (접근/안전)
A_i_Z      = 70
A_i_safe_Z = 65

# A 트레이 9개 위치(절대 티칭)
A_1 = posx(400.32,142.28,A_i_Z,     90.02,179.97,89.99); A_1_safe = posx(400.32,142.28,A_i_safe_Z, 90.02,179.97,89.99)
A_2 = posx(450.32,142.28,A_i_Z,     90.02,179.97,89.99); A_2_safe = posx(450.32,142.28,A_i_safe_Z, 90.02,179.97,89.99)
A_3 = posx(500.32,142.28,A_i_Z,     90.02,179.97,89.99); A_3_safe = posx(500.32,142.28,A_i_safe_Z, 90.02,179.97,89.99)
A_4 = posx(400,   92,    A_i_Z,     90.02,179.97,89.99); A_4_safe = posx(400,   92,    A_i_safe_Z, 90.02,179.97,89.99)
A_5 = posx(450,   92,    A_i_Z,     90.02,179.97,89.99); A_5_safe = posx(450,   92,    A_i_safe_Z, 90.02,179.97,89.99)
A_6 = posx(500,   92,    A_i_Z,     90.02,179.97,89.99); A_6_safe = posx(500,   92,    A_i_safe_Z, 90.02,179.97,89.99)
A_7 = posx(400,   42,    A_i_Z,     90.02,179.97,89.99); A_7_safe = posx(400,   42,    A_i_safe_Z, 90.02,179.97,89.99)
A_8 = posx(450,   42,    A_i_Z,     90.02,179.97,89.99); A_8_safe = posx(450,   42,    A_i_safe_Z, 90.02,179.97,89.99)
A_9 = posx(500,   42,    A_i_Z,     90.02,179.97,89.99); A_9_safe = posx(500,   42,    A_i_safe_Z, 90.02,179.97,89.99)

# 리스트로 관리
A_LIST      = [A_1,A_2,A_3,A_4,A_5,A_6,A_7,A_8,A_9]
A_SAFE_LIST = [A_1_safe,A_2_safe,A_3_safe,A_4_safe,A_5_safe,A_6_safe,A_7_safe,A_8_safe,A_9_safe]

# 분류 트레이 각 라인 기준점(절대 티칭)
High_0 = posx(397,-163, 150,90.02, 179.97, 89.99); High_1 = posx(447,-163, 150, 90.02,179.97, 89.99); High_2 = posx(497,-163,150, 90.02,179.97,89.99)
Mid_0  = posx(397,-109, 150, 90.02, 179.97, 89.99); Mid_1  = posx(447,-109, 150, 90.02,179.97, 89.99); Mid_2  = posx(497,-109,150, 90.02,179.97,89.99)
Low_0  = posx(397,-62.5, 150, 90.02, 179.97, 89.99); Low_1  = posx(447,-62.5, 150, 90.02,179.97, 89.99); Low_2  = posx(497,-62.5,150, 90.02,179.97,89.99)

HIGH_LINE = [High_0, High_1, High_2]
MID_LINE  = [Mid_0,  Mid_1,  Mid_2]
LOW_LINE  = [Low_0,  Low_1,  Low_2]

# ---------------------------------------------------------
# Motion / Probe Params (튜닝값)
# ---------------------------------------------------------
VEL_MOVE  = 200     # 일반 이동 속도
ACC_MOVE  = 160     # 일반 이동 가속도
VEL_PROBE = 10      # 프로빙(접촉 탐색) 속도
ACC_PROBE = 20      # 프로빙 가속도

# (4) 프로빙/분류 파라미터
PROBE_MAX_DN = 35.0 # 최대 탐침 이동(mm)
PROBE_STEP   = 1.0  # 스텝 이동(mm)
F_CONTACT_N  = 6.0  # 접촉 판정 힘(N)
F_TARGET_N   = 25.0 # (참고용) 목표 힘(코드에서는 10N 사용)

# (6) 집기 위치(상대 이동)
GRIP_DX = 0.0
GRIP_DY = 0.0
GRIP_DZ = 10.0      # A_i_safe에서 집기 위치로 내려가는 상대값(+Z가 하강방향이라는 전제)
GRIP_DZ_SAFE = 80.0 # 집은 뒤 안전 높이로 올리는 상대값(반대 방향)

# (9) 분류 라인 접근 시 안전 상승량
PLACE_SAFE_DOWN = 50.0

# (10) 분류별 삽입(하강) 상대값
DZ_PLACE_HIGH = 35.0
DZ_PLACE_MID  = 55.0
DZ_PLACE_LOW  = 65.0

# 분류 임계값 (접촉 순간 BASE Z값 기준)
Z_TH_HIGH = 60.0
Z_TH_MID  = 50.0

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def classify_by_z(z_contact):
    """
    접촉 순간의 BASE Z값(z_contact)으로 High/Mid/Low 분류
    반환: 0=HIGH, 1=MID, 2=LOW
    """
    if z_contact >= Z_TH_HIGH:
        return 0
    elif z_contact >= Z_TH_MID:
        return 1
    else:
        return 2


def probe_and_get_z_contact():
    """
    [Step 4] A_i_safe에서 시작했다고 가정.
    - TOOL 좌표 기준으로 Z 방향으로 PROBE_STEP씩 이동
    - Force 조건(F_CONTACT_N) 만족하면
      그 순간 BASE 좌표의 Z를 읽어 반환
    - 최대 거리(PROBE_MAX_DN)까지 못 찾으면 None
    """
    set_ref_coord(DR_TOOL)  # 상대이동/Force 방향을 TOOL 기준으로

    # 순응 제어 ON (강성 설정)
    task_compliance_ctrl([2000,2000,200, 300,300,300], time=0.0)

    # Force ON (Z축 10N 목표, 방향 +Z)
    set_desired_force([0,0,10, 0,0,0], [0,0,1,0,0,0], time=1, mod=DR_FC_MOD_REL)

    traveled = 0.0
    while traveled < PROBE_MAX_DN:
        # PROBE_STEP만큼 TOOL 기준 상대이동
        movel(posx(0,0,PROBE_STEP,0,0,0),
              vel=VEL_PROBE, acc=ACC_PROBE, ref=DR_TOOL, mod=DR_MV_MOD_REL)

        # 접촉 힘 감지(TOOL Z축 기준)
        if check_force_condition(DR_AXIS_Z, min=F_CONTACT_N, ref=DR_TOOL):
            cur, _ = get_current_posx(ref=DR_BASE)
            z_contact = cur[2]  # BASE Z값 저장

            # 순응 제어 OFF 및 좌표계 원복
            release_compliance_ctrl()
            set_ref_coord(DR_BASE)
            return z_contact

        traveled += PROBE_STEP

    # 실패 시 정리
    release_compliance_ctrl()
    set_ref_coord(DR_BASE)
    return None


def move_to_grip_relative_from_here():
    """
    [Step 6] 집기 위치로 상대이동
    - 현재 위치(A_i_safe 근처)에서 TOOL 기준 상대 이동
    """
    set_ref_coord(DR_TOOL)
    movel(posx(GRIP_DX, GRIP_DY, GRIP_DZ, 0,0,0),
          vel=VEL_PROBE, acc=ACC_PROBE, ref=DR_TOOL, mod=DR_MV_MOD_REL)
    set_ref_coord(DR_BASE)


def move_to_grip_relative_from_safe():
    """
    [Step 8] 집은 후 안전 높이로 복귀(상향 상대이동)
    - TOOL 기준 반대 방향(-GRIP_DZ_SAFE)로 이동(현재 셋업 기준)
    """
    set_ref_coord(DR_TOOL)
    movel(posx(GRIP_DX, GRIP_DY, -GRIP_DZ_SAFE, 0,0,0),
          vel=150, acc=ACC_PROBE, ref=DR_TOOL, mod=DR_MV_MOD_REL)
    set_ref_coord(DR_BASE)


def place_in_class(cls, idx_in_line):
    """
    [Step 9~12] 분류 트레이 적재
    - cls(0/1/2)에 따라 라인/삽입 깊이 선택
    - 기준점(절대) 이동 → safe 상승 → 삽입 하강 → 놓기 → safe 복귀
    """
    if cls == 0:
        p  = HIGH_LINE[idx_in_line]
        dz = DZ_PLACE_HIGH
    elif cls == 1:
        p  = MID_LINE[idx_in_line]
        dz = DZ_PLACE_MID
    else:
        p  = LOW_LINE[idx_in_line]
        dz = DZ_PLACE_LOW

    # (9) 기준점(절대) 이동
    movel(p, vel=VEL_MOVE, acc=ACC_MOVE, ref=DR_BASE)

    # safe Z 하강 (TOOL 기준)
    set_ref_coord(DR_TOOL)
    movel(posx(0,0,PLACE_SAFE_DOWN,0,0,0),
          vel=VEL_MOVE, acc=ACC_MOVE, ref=DR_TOOL, mod=DR_MV_MOD_REL)

    # (10) 삽입 하강(분류별 dz)
    movel(posx(0,0,dz,0,0,0),
          vel=VEL_PROBE, acc=ACC_PROBE, ref=DR_TOOL, mod=DR_MV_MOD_REL)

    # (11) 놓기
    releasing()

    # (12) safe 복귀(상향)
    movel(posx(0,0,-dz,0,0,0),
          vel=150, acc=ACC_PROBE, ref=DR_TOOL, mod=DR_MV_MOD_REL)

    set_ref_coord(DR_BASE)

# ---------------------------------------------------------
# Main (12-step loop for A_1 ~ A_9)
# ---------------------------------------------------------
def main():
    hi_cnt  = 0
    mid_cnt = 0
    low_cnt = 0

    for i in range(9):
        pA      = A_LIST[i]
        pA_safe = A_SAFE_LIST[i]

        # 1) 그립 닫기
        griping()

        # 2) A-i 이동 (ABS)
        movel(pA, vel=VEL_MOVE, acc=ACC_MOVE, ref=DR_BASE)

        # 3) A-i-safe 이동 (ABS)
        movel(pA_safe, vel=VEL_MOVE, acc=ACC_MOVE, ref=DR_BASE)

        # 4) 순응+Force로 접촉 Z 측정 → 분류
        zc = probe_and_get_z_contact()
        if zc is None:
            tp_log("Probe fail: A-%d" % (i+1))
            continue

        cls = classify_by_z(zc)

        # 5) 그립 열기
        releasing()

        # 6) 집기 위치로 상대이동
        move_to_grip_relative_from_here()

        # 7) 그립 닫기(집기)
        griping()

        # 8) 안전 높이로 복귀(상향 상대이동)
        move_to_grip_relative_from_safe()

        # 9~12) 분류 라인에 적재(0→1→2 순서)
        if cls == 0:
            if hi_cnt >= 3:
                tp_log("HIGH overflow")
                continue
            place_in_class(0, hi_cnt)
            hi_cnt += 1

        elif cls == 1:
            if mid_cnt >= 3:
                tp_log("MID overflow")
                continue
            place_in_class(1, mid_cnt)
            mid_cnt += 1

        else:
            if low_cnt >= 3:
                tp_log("LOW overflow")
                continue
            place_in_class(2, low_cnt)
            low_cnt += 1

    tp_log("Done: High=%d Mid=%d Low=%d" % (hi_cnt, mid_cnt, low_cnt))

main()
