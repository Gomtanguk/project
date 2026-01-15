# =========================
#  9 Blocks Classify Flow (per your 12 steps)
# =========================

# -------------------------
# Gripper (AS-IS)
# -------------------------
def griping():
    # SetNode
    set_digital_output(1,ON)
    # SetNode
    set_digital_output(2,OFF)
    # WaitNode
    wait(1.00)

def releasing():
    # SetNode
    set_digital_output(1,OFF)
    # SetNode
    set_digital_output(2,ON)
    # WaitNode
    wait(1.00)

# -------------------------
# Teach Points (TODO 채우기)
# -------------------------
# A-i 이동 포인트(상단/접근 기준점)
A_i_Z = 70
A_i_safe_Z = 65


A_1 = posx(400.32,142.28,A_i_Z,     90.02,179.97,89.99); A_1_safe = posx(400.32,142.28,A_i_safe_Z, 90.02,179.97,89.99)
A_2 = posx(450.32,142.28,A_i_Z,     90.02,179.97,89.99); A_2_safe = posx(450.32,142.28,A_i_safe_Z, 90.02,179.97,89.99)
A_3 = posx(500.32,142.28,A_i_Z,     90.02,179.97,89.99); A_3_safe = posx(500.32,142.28,A_i_safe_Z, 90.02,179.97,89.99)
A_4 = posx(400,   92,    A_i_Z,     90.02,179.97,89.99); A_4_safe = posx(400,   92,    A_i_safe_Z, 90.02,179.97,89.99)
A_5 = posx(450,   92,    A_i_Z,     90.02,179.97,89.99); A_5_safe = posx(450,   92,    A_i_safe_Z, 90.02,179.97,89.99)
A_6 = posx(500,   92,    A_i_Z,     90.02,179.97,89.99); A_6_safe = posx(500,   92,    A_i_safe_Z, 90.02,179.97,89.99)
A_7 = posx(400,   42,    A_i_Z,     90.02,179.97,89.99); A_7_safe = posx(400,   42,    A_i_safe_Z, 90.02,179.97,89.99)
A_8 = posx(450,   42,    A_i_Z,     90.02,179.97,89.99); A_8_safe = posx(450,   42,    A_i_safe_Z, 90.02,179.97,89.99)
A_9 = posx(500,   42,    A_i_Z,     90.02,179.97,89.99); A_9_safe = posx(500,   42,    A_i_safe_Z, 90.02,179.97,89.99)

A_LIST      = [A_1,A_2,A_3,A_4,A_5,A_6,A_7,A_8,A_9]
A_SAFE_LIST = [A_1_safe,A_2_safe,A_3_safe,A_4_safe,A_5_safe,A_6_safe,A_7_safe,A_8_safe,A_9_safe]

# 분류 트레이 "XY 기준점"(각 홀의 XY/자세는 절대값 티칭)
High_0 = posx(397,-163,150,90.02,179.97,89.99); High_1 = posx(447,-163,150, 90.02,179.97,89.99); High_2 = posx(497,-163,150, 90.02,179.97,89.99)
Mid_0  = posx(397,-109,150, 90.02,179.97,89.99); Mid_1  = posx(447,-109,150,90.02,179.97,89.99); Mid_2  = posx(497,-109,150, 90.02,179.97,89.99)
Low_0  = posx(397,-62.5,150, 90.02,179.97,89.99); Low_1  = posx(447,-62.5,150, 90.02,179.97,89.99); Low_2  = posx(497,-62.5,150, 90.02,179.97,89.99)

HIGH_LINE = [High_0, High_1, High_2]
MID_LINE  = [Mid_0,  Mid_1,  Mid_2]
LOW_LINE  = [Low_0,  Low_1,  Low_2]

# -------------------------
# Params (튜닝값)
# -------------------------
VEL_MOVE  = 200
ACC_MOVE  = 160
VEL_PROBE = 10
ACC_PROBE = 20

# (4) 프로빙/분류용
PROBE_MAX_DN = 35.0
PROBE_STEP   = 1.0
F_CONTACT_N  = 6.0
F_TARGET_N   = 25.0

# (6) 그립위치 상대이동 (A-i_safe에서 tool 기준으로 내려감)
GRIP_DX = 0.0
GRIP_DY = 0.0
GRIP_DZ = 10.0   # 아래로 내려갈 거리(양수로 두고 -GRIP_DZ로 내려감)
GRIP_DZ_SAFE = 80.0

# (9) 분류열 safe Z 이동: 기준점에서 tool 기준 위로 올릴 거리
PLACE_SAFE_UP = 50.0

# (10) 분류별 내려가기 상대값(안전 높이에서 아래로)
DZ_PLACE_HIGH = 35.0
DZ_PLACE_MID  = 55.0
DZ_PLACE_LOW  = 65.0

# 분류 임계 Z (측정된 z_contact 기준)
Z_TH_HIGH = 60.0
Z_TH_MID  = 50.0

# -------------------------
# Helpers
# -------------------------
def classify_by_z(z_contact):
    if z_contact >= Z_TH_HIGH:
        return 0  # HIGH
    elif z_contact >= Z_TH_MID:
        return 1  # MID
    else:
        return 2  # LOW


def probe_and_get_z_contact():
    # A-i-safe에서 시작했다고 가정 (ref=DR_BASE 절대)
    set_ref_coord(DR_TOOL)  # 툴 좌표계 사용

    task_compliance_ctrl([2000,2000,200, 300,300,300], time=0.0) # 순응제어 On
    set_desired_force([0,0,10, 0,0,0], [0,0,1,0,0,0], time=1, mod=DR_FC_MOD_REL)    # Force On, z축 10N(260114 값 그대로 사용)

    traveled = 0.0
    while traveled < 35.0:  # 35mm 까지 
        movel(posx(0,0,PROBE_STEP,0,0,0), vel=10, acc=20, ref=DR_TOOL, mod=DR_MV_MOD_REL)

        if check_force_condition(DR_AXIS_Z, min=6.0, ref=DR_TOOL):
            cur,_ = get_current_posx(ref=DR_BASE)
            z_contact = cur[2]
            release_compliance_ctrl()   # 순응제어 Off
            set_ref_coord(DR_BASE)  # 베이스 좌표계 이동
            return z_contact    # 얻은 z 값 : z_contact

        traveled += PROBE_STEP

    release_compliance_ctrl()
    set_ref_coord(DR_BASE)
    return None

def move_to_grip_relative_from_here():
    # (6) 그립위치 이동(상대적이동) : tool 기준
    set_ref_coord(DR_TOOL)
    movel(posx(GRIP_DX, GRIP_DY, GRIP_DZ, 0,0,0),
          vel=VEL_PROBE, acc=ACC_PROBE, ref=DR_TOOL, mod=DR_MV_MOD_REL)
    set_ref_coord(DR_BASE)

def move_to_grip_relative_from_safe():
    # 안전위치 이동(상대적이동) : tool 기준
    set_ref_coord(DR_TOOL)
    movel(posx(GRIP_DX, GRIP_DY, -GRIP_DZ_SAFE, 0,0,0),
          vel=150, acc=ACC_PROBE, ref=DR_TOOL, mod=DR_MV_MOD_REL)
    set_ref_coord(DR_BASE)

def place_in_class(cls, idx_in_line):
    # cls: 0=HIGH,1=MID,2=LOW
    if cls == 0:
        p = HIGH_LINE[idx_in_line]
        dz = DZ_PLACE_HIGH
    elif cls == 1:
        p = MID_LINE[idx_in_line]
        dz = DZ_PLACE_MID
    else:
        p = LOW_LINE[idx_in_line]
        dz = DZ_PLACE_LOW

    # (9) 분류열로 이동(safe Z축 위치) = 기준점 p로 가서 위로 올림
    movel(p, vel=VEL_MOVE, acc=ACC_MOVE, ref=DR_BASE)
    set_ref_coord(DR_TOOL)
    movel(posx(0,0,PLACE_SAFE_UP,0,0,0),
          vel=VEL_MOVE, acc=ACC_MOVE, ref=DR_TOOL, mod=DR_MV_MOD_REL)

    # (10) 분류위치 내려가기(분류 별 z축 상대값)
    movel(posx(0,0,dz,0,0,0),
          vel=VEL_PROBE, acc=ACC_PROBE, ref=DR_TOOL, mod=DR_MV_MOD_REL)

    # (11) 그립퍼 열기
    releasing()

    # (12) safe z축으로 이동
    movel(posx(0,0,-dz,0,0,0),
          vel=150, acc=ACC_PROBE, ref=DR_TOOL, mod=DR_MV_MOD_REL)

    set_ref_coord(DR_BASE)

# -------------------------
# Main (your 12-step loop)
# -------------------------
def main():
    hi_cnt = 0
    mid_cnt = 0
    low_cnt = 0

    for i in range(9):
        pA      = A_LIST[i]
        pA_safe = A_SAFE_LIST[i]

        # 1 그립 닫기
        griping()

        # 2 A-i 이동
        movel(pA, vel=VEL_MOVE, acc=ACC_MOVE, ref=DR_BASE)

        # 3 A-i-safe 이동
        movel(pA_safe, vel=VEL_MOVE, acc=ACC_MOVE, ref=DR_BASE)

        # 4 순응제어 + force 사용해서 분류 작업 진행 (Z 저장)
        zc = probe_and_get_z_contact()
        if zc is None:
            tp_log("Probe fail: A-%d" % (i+1))
            continue

        cls = classify_by_z(zc)

        # 5 그립 열기
        releasing()

        # 6 그립위치 이동(상대적이동)
        move_to_grip_relative_from_here()

        # 7 그립 닫기

        griping()
   
        # 8 A-i-safe 이동(올리는 동작)
        move_to_grip_relative_from_safe()

        # 9~12 분류열 채우기(0번부터)
        if cls == 0:
            if hi_cnt >= 3: tp_log("HIGH overflow"); continue
            place_in_class(0, hi_cnt)
            hi_cnt += 1
        elif cls == 1:
            if mid_cnt >= 3: tp_log("MID overflow"); continue
            place_in_class(1, mid_cnt)
            mid_cnt += 1
        else:
            if low_cnt >= 3: tp_log("LOW overflow"); continue
            place_in_class(2, low_cnt)
            low_cnt += 1

    tp_log("Done: High=%d Mid=%d Low=%d" % (hi_cnt, mid_cnt, low_cnt))

main()
