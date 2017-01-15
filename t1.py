from visual import *
scene.range = 4
box() # display a box for context
while True:
    if scene.mouse.clicked:
        m = scene.mouse.getclick()
        loc = m.pos
        rate(1)
        print(loc)
        sphere(pos=loc, radius=0.2, color=color.cyan)
