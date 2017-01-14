from visual import *
scene.range = 8 # fixed size, no autoscaling
arr = arrow(pos=(2,0,0),axis=(0,5,0))
by = 1 # touch this close to tail or tip
drag_pos = None

def grab(evt):
    global drag_pos
    drag = None
    if mag(arr.pos-evt.pos) <= by:
        drag = 'tail' # near tail of arrow
    elif mag((arr.pos+arr.axis)-evt.pos) <= by:
        drag = 'tip' # near tip of arrow
    if drag is not None:
        drag_pos = evt.pos # save mousedown location
        scene.bind('mousemove', move, drag)
        scene.bind('mouseup', drop)

def move(evt, drag):
    global drag_pos
    new_pos = evt.pos
    if new_pos != drag_pos: # if mouse has moved
        displace = new_pos - drag_pos # how far
        drag_pos = new_pos # update drag position
        if drag == 'tail':
            arr.pos += displace # displace the tail
        else:
            arr.axis += displace # displace the tip

def drop(evt):
    scene.unbind('mousemove', move)
    scene.unbind('mouseup', drop)

scene.bind('mousedown', grab)
