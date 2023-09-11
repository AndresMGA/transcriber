
import csv
print("data imported")
notes_info=[]
with open('notes.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        notes_info.append(row)
notes_info.pop(0)


tabs = []
onsets = []
times_onsets = []
chords = []

video_file = ""
n_holes = 12
harm_size = 72
harm_offset = 0
tab_size = 0
tab_offset = 0
transparency = 0
shade_top = 0
shade_bottom = 0
rotation = 0
phrases = []
render_video = 1
render_tabs = 1
render_harmonica = 1
tab_background = 0
update_only = 1

cpu_usage = "0%"


import psutil
import threading
import time
import os 

pid = os.getpid()

def get_cpu_usage():
    try:
        process = psutil.Process(pid)
        cpu_percent = process.cpu_percent(interval=.5)
        return cpu_percent
    except psutil.NoSuchProcess:
        return None

def monitor_cpu_usage():
    while True:
        global cpu_usage
        cpu_usage = (f"{get_cpu_usage()}%")
        time.sleep(1)


cpu_monitor_thread = threading.Thread(target=monitor_cpu_usage)
cpu_monitor_thread.daemon = True
cpu_monitor_thread.start()