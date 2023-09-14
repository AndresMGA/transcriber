import cv2
import numpy as np
import data
import colors

rotation = 0
prev_rotation = 0
video_file = None
video_capture = None
video_format = 1080
video_resize_factor = 1
preview_video = None
preview_video_capture = None
export_video = None
export_video_capture = None
export_video_file = None
h = 1920
w = 1080
vh = 1920
vw = 1080
ph =  636
pw = 360
fps = 24


def rotate_video():
        global vh,vw, prev_rotation,video_capture, video_format
        
        rw = 0
        rh = 0
        angle = 0
        
        if rotation == 0:
            video_capture = cv2.VideoCapture(video_file)
            vw = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            vh = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_format =  min([vw,vh])
            prev_rotation = rotation
            return
        elif rotation ==1:
            angle = cv2.ROTATE_90_CLOCKWISE
            rw = vh
            rh = vw
        elif rotation == 2:
            angle = cv2.ROTATE_180
            rw = vw
            rh = vh
        elif rotation == 3:
            rw = vh
            rh = vw
            angle = cv2.ROTATE_90_COUNTERCLOCKWISE
        
        video_capture = cv2.VideoCapture(video_file)
        path = "./tmp/rotated_video.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(path, fourcc, fps, (rw, rh))
        # Loop through the frames and rotate each frame
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            # Rotate the frame
            rotated_frame = cv2.rotate(frame,angle)  
            # Write the rotated frame to the new video file
            out.write(rotated_frame)
        # Release video objects
        
        out.release()
        video_capture = cv2.VideoCapture(path)
        vw = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        vh = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_format =  min([vw,vh])
        prev_rotation = rotation
        
def load_video():
    global video_file, video_capture, w, h, vw, vh, video_format, video_resize_factor, ph,pw,preview_video, preview_video_capture
    if video_file == None:
        video_capture = None
        h = 1920
        w = 1080
        vw = w
        vh = h
        ph = 360
        pw = 636
        return
    video_capture = cv2.VideoCapture(video_file)
    if video_capture.isOpened() == False:
        print("video error")
        return
    # Get video properties
    
    vw = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    vh = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_format =  min([vw,vh])
    if rotation!=prev_rotation:
        rotate_video()

    if vh>vw:
        
        h = 1920
        w = 1080
        ph = 636
        pw = 360
    else:
        h = 1080
        w = 1920
        ph = 360
        pw = 636
    
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    output_video_path = "./tmp/resized.mp4"
    preview_video = cv2.VideoWriter(output_video_path, fourcc, fps, (pw, ph), isColor=True)
    print("resizing video for preview")
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        resized_frame = cv2.resize(frame, (pw, ph))
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        preview_video.write(rgb_frame)


    # Release the video capture and video writer objects
    video_capture.release()
    preview_video.release()


    preview_video_capture = cv2.VideoCapture(output_video_path)
    if(rotation>0):
       video_capture = cv2.VideoCapture("./tmp/rotated_video.mp4")
    else:
        video_capture = cv2.VideoCapture(video_file)
    video_resize_factor = w/vw
 
def find_current_note(lst, threshold):
    index_and_values = [(index, num) for index, num in enumerate(
        lst) if num < threshold and num > -w/2]
    if not index_and_values:
        return None  # Return None if there are no values below the threshold
    largest_value_index = max(index_and_values, key=lambda x: x[1])[0]
    if largest_value_index == None:
        largest_value_index = 13
    return largest_value_index

def get_time_range(frame_time):
    phrase_time = 0
    phrase_idx = 0
    next_phrase_time = 10000
    phrases = data.phrases

    if not 0.0 in data.phrases:
        phrases.append(0)
    sphrases = sorted(phrases)
    for i,p in enumerate(sphrases):
        if frame_time>p:
            phrase_time = p
            phrase_idx = i

    if (phrase_idx+1) < len(sphrases):
            next_phrase_time = sphrases[phrase_idx+1]
    
    return phrase_time, next_phrase_time

old_phrase = []
def getPhrase(frame_time):
    global old_phrase
    min_t, max_t = get_time_range(frame_time)
    tab_times = []

    for tab_time in data.times_onsets:
        tab_times.append(tab_time-frame_time)
    active_note_idx= find_current_note(tab_times,.2)
    
      
    ptabs = []
    for i,t in enumerate(data.times_onsets):
        if t>min_t and t<max_t:
            tab_color = colors.text_color
            if i == active_note_idx and "-" in data.tabs[i]:
                tab_color = colors.draw_color
            if i == active_note_idx and "-" not in data.tabs[i]:
                tab_color = colors.blow_color
            ptabs.append({"tab": data.tabs[i], "time":t, "color": tab_color, "active":i==active_note_idx, "midi":data.onsets[i],"chord":data.chords[i]})
    
    new_phrase = sorted(ptabs, key=lambda x: x["time"])

    if old_phrase == new_phrase:
        return new_phrase,False
    else:
        old_phrase = new_phrase

    return new_phrase,True

def get_preview_frame_at(frame_time):

    frame = None
    if (preview_video_capture is not None):
        frame_id = int(fps*(frame_time))
        preview_video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = preview_video_capture.read()
        if not ret:
            return
    else:
        frame = np.zeros((ph, pw, 3), dtype=np.uint8)
    
    return frame

def prepare_export():

    global fourcc,export_video,export_video_capture,export_video_file,preview_video_capture,video_capture

    print("resizing video for export")

    video_capture.release()
    video_capture = cv2.VideoCapture(video_file)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    export_video_file = "./tmp/export.mp4"
    export_video = cv2.VideoWriter(export_video_file, fourcc, fps, (w, h), isColor=True)
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("can't read ")
            break
        resized_frame = cv2.resize(frame, (w, h))
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        export_video.write(rgb_frame)
    
    export_video.release()
    video_capture.release()

    export_video_capture = cv2.VideoCapture(export_video_file)
    print("export video resized")

def get_export_frame_at(frame_time):
    
    frame = None
    if (export_video_capture is not None):
        frame_id = int(fps*(frame_time))
        export_video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = export_video_capture.read()
        
        if not ret:
            print("get export frame failed")
            return
                
    else:
        frame = np.zeros((w, h, 3), dtype=np.uint8)
    
    return frame

def close():
    if video_capture != None:
        video_capture.release()

def update():
    global  video_file,  rotation, prev_rotation
   
    new_video_file = data.video_file
    new_rotation = data.rotation
    if (video_file != new_video_file) or (rotation != new_rotation):
        video_file = new_video_file
        prev_rotation = rotation
        rotation = new_rotation
        load_video()

    
    return


