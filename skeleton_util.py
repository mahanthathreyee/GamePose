def configure_skeleton(human):
    lw = human.body_parts.get(4,None)
    rw = human.body_parts.get(7,None)    
    if lw and rw:
        return human, True
    return None, False

def update_skeleton(skeleton, human):
    hlw = human.body_parts.get(4,None)
    hrw = human.body_parts.get(7,None)

    if hlw:
        skeleton.body_parts[4] = hlw
    if hrw:
        skeleton.body_parts[7] = hrw

    return skeleton



