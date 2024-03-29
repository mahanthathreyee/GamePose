#interface.py
import math
from directKeys import PressKey, ReleaseKey, W, A, S, D

def compute_angle(shoulder, elbow, wrist):
    if wrist and elbow and shoulder:
        X1 = math.sqrt(  ((shoulder.x - elbow.x)**2)   +   ((shoulder.y - elbow.y)**2)  )
        X2 = math.sqrt(  ((elbow.x - wrist.x)**2)      +   ((elbow.y - wrist.y)**2)     )
        X3 = math.sqrt(  ((shoulder.x - wrist.x)**2)   +   ((shoulder.y - wrist.y)**2)  )

        angle = math.acos( ( 
            (X1**2) + (X2**2) - (X3**2) ) / 
            (2 * X1 * X2) 
        )

        return math.degrees(angle)
    return None

def get_hand_angle(base_value, human):
    rShoulder = human.body_parts.get(base_value + 0,None)
    rElbow = human.body_parts.get(base_value + 1,None)
    rWrist = human.body_parts.get(base_value + 2,None)
    return compute_angle(rShoulder, rElbow, rWrist)

def locate_window_horizontal(x,y):
    if y < 0.25:
        return 'W'
    if y > 0.5:
        return 'S'
    return None

def locate_window_vertical(x,y):
    if 0.66<=x<=1.0:
        return 'R'
    if 0<x<=0.33:
        return 'L'
    return None

def get_keypress(human, fr, keypress_status_hand, keypress_status_nose, start_hand_angle, max_frame_rate):
    lw = human.body_parts.get(4,None)
    rw = human.body_parts.get(7,None)
    nose = human.body_parts.get(0,None)
    l,r,n = None, None, None
    if lw:
        l = locate_window_vertical(lw.x, lw.y)
    if rw:
        r = locate_window_vertical(rw.x, rw.y)
    if nose: 
        n = locate_window_horizontal(nose.x, nose.y)

    interval = 20
    angle = 63

    if l:
        ReleaseKey(D)
        PressKey(A) 
        keypress_status_hand = True

        angle = get_hand_angle(2, human)
        angle = angle if angle else 63

        #print("\nFrame: "+str(fr)+" "+l)

    elif r:
        ReleaseKey(A)
        PressKey(D)
        keypress_status_hand = True

        angle = get_hand_angle(5, human)
        angle = angle if angle else 63
        
        #print("\nFrame: "+str(fr)+" "+r)

    elif keypress_status_hand:
            ReleaseKey(A)
            ReleaseKey(D)
            keypress_status_hand = False
            #print("\nFrame: "+str(fr)+"idle")

    if n == 'S':
        ReleaseKey(W)
        PressKey(S) 
        keypress_status_nose = True

    elif n == "W":
        ReleaseKey(S)
        PressKey(W)
        keypress_status_nose = True

    elif keypress_status_nose:
        ReleaseKey(W)
        ReleaseKey(S)
        
        keypress_status_nose = False
        #print("\nFrame: "+str(fr)+"idle")

    interval = int( ((max_frame_rate * angle) - (180 * max_frame_rate) + start_hand_angle ) / ( start_hand_angle - 180 ) )
    #print("\n" + str(interval) + "  " + str(angle))
    interval = interval if 0 < interval <= max_frame_rate else max_frame_rate

    return keypress_status_hand, keypress_status_nose, interval

