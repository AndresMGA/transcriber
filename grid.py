import data

grid = 16
number_of_lines = 38
pixels_per_second = 100
piano_w = 150

def snap(x):
    return round(x / grid) * grid

def miditoy(midi):
    ret = round(number_of_lines*grid - (midi-60)*grid)
    if ret<0:
        ret=0
    return ret

def ytomidi(y):
    return round((number_of_lines*grid - y) / grid + 60)

def ytotab(y):
    return data.notes_info[ytomidi(y)][2]

def timetox(time):
    return round(time*pixels_per_second+piano_w)

def xtotime(x):
    return (x-piano_w)/pixels_per_second

max_y = miditoy(60)
