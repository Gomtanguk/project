## Title : m0609_task_20260114_axis_z_force
## Time : 2026-01-15 11:47:14
Global_cnt = 0


def con_pose():
    global System_cnt
    global System_a
    global System_b
    global System_c
    global System_center
    global Global_cnt
    # IfBlockNode
    if System_cnt==0:
        movel(System_a, radius=0.00, ref=0, mod=DR_MV_MOD_ABS, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
        global _alias_sub_name_griping
        _alias_sub_name_griping()
        
    elif System_cnt==1:
        movel(System_b, radius=0.00, ref=0, mod=DR_MV_MOD_ABS, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
        global _alias_sub_name_griping
        _alias_sub_name_griping()
        
    else:
        movel(System_c, radius=0.00, ref=0, mod=DR_MV_MOD_ABS, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
        global _alias_sub_name_griping
        _alias_sub_name_griping()
        
    
_alias_sub_name_con_pose = con_pose

def griping():
    # SetNode
    set_digital_output(1,ON)
    # SetNode
    set_digital_output(2,OFF)
    # WaitNode
    wait(1.00)
    
_alias_sub_name_griping = griping

def releasing():
    # SetNode
    set_digital_output(1,OFF)
    # SetNode
    set_digital_output(2,ON)
    # WaitNode
    wait(1.00)
    
_alias_sub_name_releasing = releasing

def relative_move():
    global System_cnt
    global System_a
    global System_b
    global System_c
    global System_center
    global Global_cnt
    # MoveLNode
    movel(posx(-3.00, -300.00, 0.00, 0.00, 0.00, 0.00), radius=0.00, ref=0, mod=DR_MV_MOD_REL, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
    
_alias_sub_name_relative_move = relative_move

def up_move():
    global System_cnt
    global System_a
    global System_b
    global System_c
    global System_center
    global Global_cnt
    # MoveLNode
    movel(posx(0.00, 0.00, 50.00, 0.00, 0.00, 0.00), radius=0.00, ref=0, mod=DR_MV_MOD_REL, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
    
_alias_sub_name_up_move = up_move

def down_move():
    global System_cnt
    global System_a
    global System_b
    global System_c
    global System_center
    global Global_cnt
    # MoveLNode
    movel(posx(0.00, 0.00, -50.00, 0.00, 0.00, 0.00), radius=0.00, ref=0, mod=DR_MV_MOD_REL, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
    
_alias_sub_name_down_move = down_move

set_singular_handling(DR_AVOID)
set_velj(60.0)
set_accj(100.0)
set_velx(250.0, 80.625, DR_OFF)
set_accx(1000.0, 322.5)
gLoop114714481 = 0
while gLoop114714481 < 1:
    # SetNode
    set_ref_coord(1)
    # CallNode
    _alias_sub_name_releasing()
    # MoveLNode
    movel(posx(367.25, 6.68, 191.61, 130.96, 179.97, 130.93), radius=0.00, ref=0, mod=DR_MV_MOD_ABS, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
    # MoveLNode
    movel(System_center, radius=0.00, ref=0, mod=DR_MV_MOD_ABS, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
    # RepeatNode
    for cnt in range(0, 3, 1):
        if cnt==0:
            movel(System_a, radius=0.00, ref=0, mod=DR_MV_MOD_ABS, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
            _alias_sub_name_griping()
            _alias_sub_name_up_move()
            _alias_sub_name_relative_move()
            _alias_sub_name_down_move()
            _alias_sub_name_releasing()
            
        elif cnt==1:
            movel(System_b, radius=0.00, ref=0, mod=DR_MV_MOD_ABS, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
            _alias_sub_name_griping()
            _alias_sub_name_up_move()
            _alias_sub_name_relative_move()
            _alias_sub_name_down_move()
            _alias_sub_name_releasing()
            
        elif cnt==2:
            movel(System_c, radius=0.00, ref=0, mod=DR_MV_MOD_ABS, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
            _alias_sub_name_griping()
            _alias_sub_name_up_move()
            _alias_sub_name_relative_move()
            _alias_sub_name_down_move()
            _alias_sub_name_releasing()
            
        
    # MoveLNode
    movel(System_center, radius=0.00, ref=0, mod=DR_MV_MOD_ABS, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
    # CallNode
    _alias_sub_name_griping()
    # CallNode
    _alias_sub_name_up_move()
    # MoveLNode
    movel(posx(347.47, -232.69, 90.22, 138.38, 179.97, 138.34), radius=0.00, ref=0, mod=DR_MV_MOD_ABS, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
    # MoveLNode
    movel(posx(0.00, 0.00, -25.00, 0.00, 0.00, 0.00), radius=0.00, ref=0, mod=DR_MV_MOD_REL, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
    # ComplianceNode
    task_compliance_ctrl()
    set_stiffnessx([3000.00, 3000.00, 3000.00, 200.00, 200.00, 200.00],time=0.0)
    # MoveLNode
    movel(posx(0.00, 0.00, -15.00, 0.00, 0.00, 0.00), vel=[34.39, 62.84], acc=[1000.00, 251.35], radius=0.00, ref=0, mod=DR_MV_MOD_REL, ra=DR_MV_RA_DUPLICATE, app_type=DR_MV_APP_NONE)
    # RepeatNode
    while Global_cnt<5:
        if check_force_condition(DR_AXIS_Z, max=22):
            release_compliance_ctrl()
            _alias_sub_name_releasing()
            _alias_sub_name_up_move()
            break
            
        else:
            set_desired_force([0.00, 0.00, 20.00, 0.00, 0.00, 0.00],[0,0,1,0,0,0],time=0.7,mod=DR_FC_MOD_ABS)
            move_periodic(amp=[0.00, 0.00, 0.00, 0.00, 0.00, 10.00], period=[0.00, 0.00, 0.00, 0.00, 0.00, 1.00], atime=0.50, repeat=2, ref=0)
            
        
    gLoop114714481 = gLoop114714481 + 1