from directKeys import PressKey, ReleaseKey, W, A, S, D

def locate_window(x,y):
    if 0.75<=x<=1.0:
        return 'R'
    if 0<x<=0.25:
        return 'L'
    return None
        

def read_humans(human, fr, keypress_status):
    lw = human.body_parts.get(4,None)
    rw = human.body_parts.get(7,None)
    l,r = None, None
    if lw:
        l = locate_window(lw.x, lw.y)
    if rw:
        r = locate_window(rw.x, rw.y)
    #PressKey(W)
    if l:
        ReleaseKey(D)
        PressKey(A) 
        keypress_status = True
        print("Frame: "+str(fr)+" "+l)
    elif r:
        ReleaseKey(A)
        PressKey(D)
        keypress_status = True
        print("Frame: "+str(fr)+" "+r)

    else:
        if keypress_status:
            ReleaseKey(A)
            ReleaseKey(D)
            keypress_status = False
            print("Frame: "+str(fr)+"idle")
    return keypress_status

