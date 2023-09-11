import data

hu = 22
offset_x = 0
offset_y = 420
font_scale = 1
def x(u):
    return (hu*u+offset_x)
def y(u):
    return (hu*u+offset_y)
def r(u):
    return (hu*u)
def f(u):
    return round(data.tab_size*font_scale*u)
def scale(w,h):
    global hu, font_scale, offset_x, offset_y
    hu = data.harm_size * w/360
    font_scale = w/360
    if data.render_harmonica:
        offset_y = h * data.harm_offset
        if data.n_holes>10:
            offset_x = (w - r(14.8))/2
        else:
            offset_x = (w - r(11.5))/2