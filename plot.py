from PyQt5.QtCore import Qt,QRectF, QTimer, QObject, QPointF,QPoint, QRect, QMargins,pyqtSignal,QSize
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import  QGraphicsView, QGraphicsScene, QGraphicsRectItem,  QUndoStack, QUndoCommand,QGraphicsSceneMouseEvent, QToolTip, QWidget,QGraphicsTextItem,QGraphicsEllipseItem
from PyQt5.QtGui import QPainterPath, QPen, QColor , QBrush, QPainterPath, QKeySequence, QImage, QPixmap, QFont,QTextDocument, QFontMetrics,QPainter,QFontDatabase
from aubio import source, pitch
from moviepy.editor import VideoFileClip
import math
import numpy as np
import sounddevice as sd
import csv
import json
import preview
import cv2
import grid
import re
import reversible_commands as cmd
import undo_redo as ur
#import librosa
import soundfile as sf
import data
import colors
import os
import platform
from q_note import QNoteRect
from typing import Optional
import settings
import fonts
from scaling import r,f,x,y,scale


  

class RoundedRectItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, corner_radius, color, z=0,fill=True,parent=None):
        super().__init__(parent)
        self.rect = QRectF(x, y, width, height)
        self.corner_radius = corner_radius
        self.color = color
        self.setZValue(z)
        self.fill = fill



    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)  # Enable antialiasing for smoother edges
        painter.setPen(QPen(self.color))
        if self.fill:
            painter.setBrush(QBrush(self.color))
        painter.drawRoundedRect(self.rect, self.corner_radius, self.corner_radius)
        


class NewPhrase(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.time = None
        self.update() 
        self.old_pos=QPointF(0,0)
        
       
    def mouseReleaseEvent(self, event):
        self.setPos(self.pos().x(),0)
        cmd.MoveCommand(self.scene().views()[0],self.scene().selectedItems())
        self.setSelected(False)
        #self.setPos(self.pos().x(),0)
        self.update()
        super().mouseReleaseEvent(event)

 
    def mousePressEvent(self, event):
       
        for selectedItem in self.scene().selectedItems():
            if isinstance(selectedItem,NewPhrase):
                selectedItem.old_pos = selectedItem.pos()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
       
        if self.pos().y()<-2*grid.grid or self.pos().y()>2*grid.grid:
            return
           
        
        self.update()
        for selectedItem in self.scene().selectedItems():
            selectedItem.update()
        super().mouseMoveEvent(event)


    def update(self):
        pos = self.mapToScene(self.rect().topLeft())
        self.time = grid.xtotime(pos.x())



def callback(outdata, frames, time, status):
    if Plot.original_audio:
        indata = np.expand_dims(Plot.np_original_audio[Plot.start_idx:Plot.start_idx+frames], axis=1)
    else:
        indata = np.expand_dims(Plot.npwave[Plot.start_idx:Plot.start_idx+frames], axis=1)
    
    if np.size(indata) >= frames:
        outdata[:frames, :] = indata
        Plot.start_idx += frames

    
       
class Plot(QtWidgets.QGraphicsView):


    loc = 0
    start_idx = 0
    synth_sr = 44100*2
    orig_sr = 44100*2
    sr = 44100*2
    total_frames = 0
    onsets = []
    pitches = []
    midis = []
    midis_q = []
    levels = []
    times_pitches = []
    times_onsets = []
    alt_tabs = []
    tabs = []
    phrases = []
    project_file = None
    n_holes = 12
    scene_obj = None
    min_cont =7
    speed_div = 1
    interval = 50
    undo_stack = QUndoStack() 
    pen = QPen(colors.note)
    brush = QBrush(colors.note)
    pen_opt = QPen(colors.opt_tab_note)
    brush_opt = QBrush(colors.opt_tab_note)
    alt_pen = QPen(QColor(20, 20, 20))
    alt_brush = QBrush(QColor(40, 40, 40))
    piano = None
    time_line = None
    npwave = None

    bar = None
    os = sd.OutputStream(callback=callback,samplerate=sr,channels=1)
    np_original_audio = None
    original_audio = False


    image_label : Optional[QtWidgets.QLabel]
    tabs_label = Optional[QtWidgets.QLabel]
    cpu_label = Optional[QtWidgets.QLabel]
    timer = QTimer()

    h=0

    

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalScrollBar().valueChanged.connect(self.on_scrollbar_value_changed)
        Plot.bar = self.horizontalScrollBar()
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setFocusPolicy(Qt.StrongFocus)
        self.rubber_band_rect = None
        self.setKeyBindings()
        self.clipboard = []
        Plot.timer.timeout.connect(Plot.timer_callback)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        Plot.video_scene = QGraphicsScene()

        

        #self.timer.start(50)  # Set the timer interval in milliseconds (30 ms = 33.33 fps)

    def getNotes(self):
        notes = []
        for item in Plot.scene_obj.items():
            if isinstance(item,QNoteRect):
                notes += [item]
        return notes
    
    def analyse(input_filename, do_onsets = True):
        
        downsample = 1
        total_frames = 0
        samplerate = 44100 // downsample
        win_s = 2048 // downsample # fft size
        hop_s = 256  // downsample # hop size
        min_pitch = 250
        max_pitch = 2400
        s = source(input_filename, samplerate, hop_s)
        samplerate = s.samplerate
        pitch_o = pitch("default", win_s, hop_s, samplerate)
        pitch_o.set_unit("Hz")
        pitch_o.set_silence(-50)
        pitch_o.set_tolerance(.8)
        while True:
            samples, read = s()
            _level = float(abs(max(samples, key=abs)))
            _pitch = float(pitch_o(samples)[0])
            _level = _level if _pitch>0 else 0
            _pitch = _pitch if _pitch>min_pitch and _pitch<max_pitch else 0
            if _pitch:
                Plot.pitches += [_pitch] 
                Plot.midis += [Plot.freqtomidi(_pitch)]
                Plot.midis_q += [round(Plot.freqtomidi(_pitch))]
                Plot.levels += [_level]
                Plot.times_pitches += [total_frames/samplerate]
            total_frames += read
            if read < hop_s: break
        if do_onsets:
            for i in range(1,len(Plot.times_pitches)-Plot.min_cont):
                if Plot.midis_q[i-1]!=Plot.midis_q[i]:
                    is_onset = True
                    for c in range(1,Plot.min_cont):
                        if Plot.midis_q[i] != Plot.midis_q[i+c]:
                            is_onset =False
                            break
                    if is_onset:
                        data.onsets += [Plot.midis_q[i]]
                        data.times_onsets += [Plot.times_pitches[i]]
                        Plot.alt_tabs += [0]
                        data.chords += [1]
  
    def synth():
        
        Plot.total_frames = round(Plot.times_pitches[-1])*Plot.synth_sr
        audio_pitch = [0]*Plot.total_frames
        audio_level = [0]*Plot.total_frames
        Plot.npwave = np.zeros(Plot.total_frames)
        #print(audio_pitch)
        for i in range(len(Plot.pitches)):
            for s in range(round(256/(44100/Plot.synth_sr))+2):
                idx = s+round(Plot.times_pitches[i]*Plot.synth_sr)
                if idx<Plot.total_frames:
                    audio_pitch[idx]=Plot.pitches[i]
                    audio_level[idx]=.5#Plot.levels[i]
        ramp = 0
        for i in range(Plot.total_frames):
            ramp += audio_pitch[i]/Plot.synth_sr
            ramp = ramp -2.0 if ramp > 1.0 else ramp
            value =  math.sin(2 * math.pi * ramp)*audio_level[i]
            Plot.npwave[i] = value


        data, Plot.orig_sr = sf.read("./tmp/audio.wav")

        if len(data.shape) > 1 and data.shape[1] == 2:
            Plot.np_original_audio = np.repeat(data.mean(axis=1),2)
        else:
            Plot.np_original_audio = np.repeat(data,2)

        Plot.orig_sr = Plot.orig_sr*2

    def save_edits():
        Plot.stop()
        if not Plot.scene_obj:
            return
        data.times_onsets.clear()
        data.onsets.clear()
        Plot.alt_tabs.clear()
        data.tabs.clear()
        data.phrases.clear()
        data.chords.clear()

        for item in Plot.scene_obj.items():
            if isinstance(item, QNoteRect):
                data.times_onsets += [item.time]
                data.onsets += [item.onset]
                Plot.alt_tabs += [item.optional_tab]
                data.tabs += [item.getTab()]
                data.chords += [item.chord]
                
        for item in Plot.scene_obj.items():
            if isinstance(item, NewPhrase):
                data.phrases += [item.time]
  
    def load_json(json_file):
        Plot.stop()
        with open(json_file, "r") as file:
            json_data = json.load(file)
            data.onsets = json_data["onsets"]
            Plot.alt_tabs = json_data["alt_tabs"]
            
            Plot.project_file = json_data["project_file"]
            data.video_file = json_data["video_file"]
            
            data.n_holes = json_data["n_holes"]
            data.harm_size = json_data["harm_size"] 
            data.harm_offset = json_data["harm_offset"] 
            data.tab_size = json_data["tab_size"]
            data.tab_offset = json_data["tab_offset"]
            data.transparency = json_data["transparency"]
            data.shade_top = json_data["shade_top"]
            data.shade_bottom =json_data["shade_bottom"]
            data.rotation = json_data["rotation"]
            data.phrases = json_data["phrases"]
            data.times_onsets = json_data["times_onsets"]
            data.tabs = json_data["tabs"]
            settings.tabs_font = json_data["tab_font"]
            
            data.chords = json_data["chords"]

    def get_json():
        Plot.save_edits()
        return {
            "project_file" : Plot.project_file,
            "video_file": data.video_file,
           
            "n_holes" : data.n_holes,
            "harm_size" : data.harm_size,
            "harm_offset" : data.harm_offset,
            "tab_size" : data.tab_size,
            "tab_offset": data.tab_offset,
            "transparency" :data.transparency,
            "shade_top" : data.shade_top,
            "shade_bottom": data.shade_bottom,
            "rotation" : data.rotation,
            "tab_font" : settings.tabs_font,
            
            "onsets": data.onsets,
            "times_onsets": data.times_onsets,
            "alt_tabs": Plot.alt_tabs,
            "tabs": data.tabs,
            "phrases": data.phrases,
            "chords":data.chords

            
        }
    
    def sync_video(self):
        options = QtWidgets.QFileDialog.Options()
        file_filter = "Video Files (*.mp4 *.avi *.mov *.mkv)"
        video_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Video", "", file_filter, options=options)
        data.video_file = video_file
        Plot.update_video()
        return video_file
    
    def setKeyBindings(self):
        undo_shortcut = QKeySequence(Qt.CTRL + Qt.Key_Z)
        redo_shortcut = QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Z)
        save_shortcut = QKeySequence(Qt.CTRL + Qt.Key_Z)
        undo_action = self.undo_stack.createUndoAction(self, "Undo")
        undo_action.setShortcut(undo_shortcut)
        redo_action = self.undo_stack.createRedoAction(self, "Redo")
        redo_action.setShortcut(redo_shortcut)
        save_action = self.undo_stack.createUndoAction(self, "Save")
        save_action.setShortcut(save_shortcut)
        self.addAction(undo_action)
        self.addAction(redo_action)

    def zoom_changed(self,value):
        Plot.stop()
        grid.pixels_per_second = value
        Plot.save_edits()
        self.plot_array()
      
    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Undo):
            Plot.stop()
            ur.undo_stack.undo()
        elif event.matches(QKeySequence.Redo):
            Plot.stop()
            ur.undo_stack.redo()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
             print("copy")
             self.copy()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
             print("paste")
             self.paste()
        elif event.matches(QKeySequence.Save):
            Plot.stop()
            self.save_dialog()
        elif event.key() == Qt.Key_Backspace:
            cmd.DeleteCommand(self)
        elif event.key() == Qt.Key_Space:
            Plot.play_stop()
        # elif event.key() == Qt.Key_Q:
        #     Plot.quit()
        elif event.key() == Qt.Key_E:
            Plot.stop()
            Plot.export_video()
        elif event.key() == Qt.Key_O:
            Plot.stop()
            cmd.OpTabCommand(self)
        elif event.key() == Qt.Key_P:
            Plot.export_preview()
        elif event.text().isdigit() and int(event.text())>0:
            Plot.stop()
            cmd.ChordCommand(self,int(event.text()))
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        Plot.stop()
        #if event.button() == Qt.LeftButton and event.modifiers() == Qt.ShiftModifier:
        if event.button() == Qt.RightButton:
            global start_idx
            pos = self.mapToScene(event.pos()).x()
            pos = max(pos, grid.piano_w)
            Plot.start_idx=round(grid.xtotime(pos)*Plot.sr)
            Plot.time_line.setX(pos)
            Plot.render_video_at(Plot.start_idx/Plot.sr)
            
        if event.button() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier:
            pos = event.pos()
            pos.setX(max(pos.x(),grid.piano_w))
            cmd.AddSceneCommand(self, self.mapToScene(pos))
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragMode() == QGraphicsView.RubberBandDrag:
            if self.rubber_band_rect is not None:
                current_pos = event.pos()
                self.updateRubberBandRect(current_pos)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.dragMode() == QGraphicsView.RubberBandDrag and self.rubber_band_rect is not None:
            selection_rect = self.rubber_band_rect.normalized()
            self.selectItems(selection_rect)
            self.rubber_band_rect = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        pos = self.mapToScene(event.pos())
        #pos = event.pos()
        pos.setX(max(pos.x(),grid.piano_w))
        pos.setY(min(pos.y(),grid.max_y))
        cmd.AddNoteCommand(self,pos.x(),pos.y())

    def updateRubberBandRect(self, current_pos):
        rubber_band_path = QPainterPath()
        rubber_band_path.addRect(self.rubber_band_rect)
        rubber_band_path.addRect(QRectF(self.drag_start_pos, current_pos))
        self.setRubberBandSelection(rubber_band_path)

    def selectItems(self, selection_rect):
        selected_items = self.scene_obj.items(selection_rect, Qt.IntersectsItemShape)
        for item in selected_items:
            item.setSelected(True)

    def setRubberBandSelection(self, path):
        selection_rect = path.boundingRect()
        self.scene().setSelectionArea(path, Qt.IntersectsItemShape)
        self.viewport().update(selection_rect)
    
    def play_stop():
        if Plot.os.active or Plot.timer.isActive():
            Plot.stop()

        else:
            Plot.os =sd.OutputStream(callback=callback,samplerate=Plot.sr/Plot.speed_div,channels=1)
            Plot.os.start()
            Plot.timer.start(Plot.interval)
            print("timers started")

    def stop():
        if Plot.os.active: 
            Plot.os.stop()
            print("audio timer stopped")
        if Plot.timer.isActive():
            Plot.timer.stop()
            print("graphics timers stopped")

    def set_speed(self,value):
        Plot.stop()
        if value == 2:
            Plot.speed_div=2
        else:
            Plot.speed_div=1
        if Plot.os.active:
            Plot.os.stop()
            Plot.os =sd.OutputStream(callback=callback,samplerate=Plot.sr/Plot.speed_div,channels=1)
            Plot.os.start()
            print(Plot.os.samplerate)

    def set_original_audio(self,value):
        Plot.stop()
        if value == 2:
            Plot.original_audio=True
            Plot.sr = Plot.orig_sr
            
        else:
            Plot.original_audio=False
            Plot.sr = Plot.synth_sr
    
    def draw_guide_lines(self):
        for i in range(60,99):
            if "#" not in data.notes_info[i][1]:
                Plot.scene_obj.addRect(0,grid.miditoy(i),grid.timetox(Plot.times_pitches[-1]),grid.grid,Plot.alt_pen,Plot.alt_brush)

    def draw_pitches(self):           
        for i in range(len(Plot.times_pitches)):
            if Plot.midis[i]>59:
                col = 100#(int)(255 * Plot.levels[i] * 2)
                if col>255:
                    col = 255
                Plot.scene_obj.addRect(grid.timetox(Plot.times_pitches[i]), grid.miditoy(Plot.midis[i]),1 , grid.grid*.8,QPen(QColor(col, 100, col)))
                #Plot.scene_obj.addRect(Plot.times_pitches[i]*grid.pixels_per_second, grid.miditoy(Plot.midis_q[i])+grid.grid/2-1, 1, 2,QPen(QColor(250, 250, 250)))

    def draw_onsets(self):
        
        for i in range(len(data.times_onsets)):
            self.addNote(grid.timetox(data.times_onsets[i]), grid.miditoy(data.onsets[i]),Plot.alt_tabs[i],chord=data.chords[i])
    
    def draw_phrases(self):
        for i in range(len(data.phrases)):
            self.addNewPhrase(grid.timetox(data.phrases[i]))

    def write_tabs(self):
        tab_idx = 2
        alt_tab_idx = 3
        if data.n_holes == 10:
            tab_idx = 4
            alt_tab_idx = 5
        if not Plot.scene_obj:
            return
        for t in Plot.scene_obj.items():
            if isinstance(t,QGraphicsTextItem):
                Plot.scene_obj.removeItem(t)



        for i in range(60,99):
            if "#" not in data.notes_info[i][1]:
                
                t=Plot.scene_obj.addText(data.notes_info[i][1][0],QFont("Courier New", 8))
                t.setPos(0,grid.miditoy(i)-2)
                t.setProperty("offset",0)
            if data.notes_info[i][tab_idx]!="na":
                t=Plot.scene_obj.addText(data.notes_info[i][tab_idx],QFont("Courier New", 20))
                t.setDefaultTextColor(QColor(250,0,0,255))
                t.setPos(35,grid.miditoy(i)-7)
                t.setProperty("offset",35)
            if data.notes_info[i][tab_idx]!=data.notes_info[i][alt_tab_idx] and data.notes_info[i][alt_tab_idx]!="na":
                t=Plot.scene_obj.addText(data.notes_info[i][alt_tab_idx],QFont("Courier New", 20))
                t.setDefaultTextColor(QColor(0,250,250,255))
                t.setPos(80,grid.miditoy(i)-7)
                t.setProperty("offset",80)

        self.on_scrollbar_value_changed(self.horizontalScrollBar().value())
    
    def plot_array(self):
        # if self.scene():
        #     self.scene().clear()

        Plot.scene_obj = QGraphicsScene()
        
      
        
        self.draw_guide_lines()
        self.draw_pitches() 
        self.draw_onsets()
        self.draw_phrases()

        Plot.piano = Plot.scene_obj.addRect(0,0,grid.piano_w,grid.grid*39,QPen(QColor(0,0,0,60)),QBrush(QColor(0,0,0,60)))
        self.write_tabs()


                

        Plot.time_line = Plot.scene_obj.addRect(0,0,1,grid.grid*38,Plot.pen_opt)
       
        self.setScene(Plot.scene_obj)

    def on_scrollbar_value_changed(self, value):
        if not Plot.scene_obj:
            return
        for t in Plot.scene_obj.items():
            if isinstance(t,QGraphicsTextItem):
                offset= t.property("offset")
                t.setPos(value+offset, t.pos().y())

        self.piano.setPos(value+offset, t.pos().y())
       
    def addNote(self, x,y, opt=0,selected = False,chord=1):
        item = QNoteRect(x, y, Plot.min_cont, chord*grid.grid)
        if opt:
            item.setPen(Plot.pen_opt)
            item.setBrush(Plot.brush_opt)
            item.optional_tab=1
        else:
            item.setPen(Plot.pen)
            item.setBrush(Plot.brush)
        
        item.chord = chord if chord>1 else 1
        item.setSelected(selected)
        Plot.scene_obj.addItem(item)
        return item
    
    def addNewPhrase(self, x, selected=False):
        item = NewPhrase(x,grid.miditoy(96), 8, grid.grid*35)
        item.setPen(QColor(200,200,0,60))
        item.setBrush(QColor(200,200,0,60))
        
        Plot.scene_obj.addItem(item)
        item.setSelected(selected)
        return item

    def freqtomidi(freq):

        midi = 0
        midi = freq / 6.875
        midi = math.log(midi) / 0.6931471805599453
        midi *= 12
        midi -= 3
        return (midi)

    def quit(self=None):
        pass

    update_count=0
    def update_video():
        Plot.stop()
        Plot.save_edits()
        Plot.update_count=Plot.update_count+1
        preview.update()
        print("video updated " + str(Plot.update_count))
        
        Plot.render_video_at(Plot.start_idx/Plot.sr)

    def _update_video(self):
        Plot.update_video()

    def clear_data():

        Plot.times_pitches = []
        Plot.pitches = []
        Plot.levels = []
        Plot.midis = []
        Plot.midis_q = []
        data.times_onsets = []
        data.onsets = []
        Plot.alt_tabs = []
        data.n_holes = 12
        data.video_file = None
        grid.pixels_per_second = 100
        data.chords = []
        data.phrases = []
        data.rotation = 1

        if Plot.scene_obj:
            Plot.scene_obj.clear()
            Plot.scene_obj = None


    def render_video_at(time, export=False):
                   
        ptabs,new=preview.getPhrase(time)

        if not new and Plot.timer.isActive() and data.update_only:
            return
        

        if  data.render_tabs + data.render_harmonica + data.render_video == 0:
            return 
        w = preview.w if export else preview.pw
        h = preview.h if export else preview.ph
        scale(w,h)
        
        css = "<style>"
        css += "td{"
        css += "margin:0px"
        css += "padding:0px"
        css += f"vertical-align:{settings.chords_align};"
        css += "}"
        css += "p{"
        css += "margin:0px"
        css += "padding:0px"
        css += "top:0px;"
        css += "left:0px;"
        css_label = css + "}</style>"
        #css += f"padding-right:{f(.3)}px;"
        css += "}"
        css += "</style>"

        
        table = "<table><tr>"
        
        active_tab = None

        for t in ptabs:
            
            tab = t
            
            digits = re.findall(r'\d+', tab['tab'])
            if len(digits):
                hole = int(digits[0])
            else:
                continue
            if t["active"]:
                active_tab = tab
                active_hole = hole
            if t["chord"]<2:
                table+=f"<td style='color:{t['color'].name()};font-size:{f(1)}px'> {t['tab']} </td>"
            else:
                if t["chord"]<8:
                    f_size = f(1)#f(1 - .1*t['chord'])
                    f_size_p = f(1)#f(.6 *(t['chord']))
                    table+=f"<td  style='color:{t['color'].name()};font-size:{f_size_p}px;'>" 
                    if "-" in t["tab"]:
                        table+=" -(</td>"
                    else :
                        table+=" (</td>"
                    
                    table+=f"<td class='chord' style='color:{t['color'].name()};font-size:{f_size}px;'>" 
                    
                    for i in range(t["chord"]):
                        table+=f"{str(hole+i)} "
                        #table+="<br>"
                    
                    table = table[:-1]
                    suffix = t["tab"].replace(str(hole),"").replace("-","")
                    table+=f"</td><td  style='color:{t['color'].name()};font-size:{f_size_p}px;'>){suffix} </td>" 

                elif t["chord"]==8:
                    f_size = f(1)#f(1 - .1*t['chord'])
                    f_size_p = f(1)#f(.6 *(t['chord']))
                    table+=f"<td  style='color:{t['color'].name()};font-size:{f_size_p}px;'>" 
                    if "-" in t["tab"]:
                        table+=" -(</td>"
                    else :
                        table+=" (</td>"
                    
                    table+=f"<td class='chord' style='color:{t['color'].name()};font-size:{f_size}px;'>" 
                    
                    if data.n_holes == 12:
                        table+=f"{str(hole)} {str(hole+4)}"
                    elif data.n_holes == 10 and ("-" in t["tab"]):
                        table+=f"{str(hole)} {str(hole+4)}"
                    else:
                        table+=f"{str(hole)} {str(hole+3)}"
                    
                    #table = table[:-1]
                    suffix = t["tab"].replace(str(hole),"").replace("-","")
                    table+=f"</td><td  style='color:{t['color'].name()};font-size:{f_size_p}px;'>){suffix} </td>" 

            

                table+="</td>"
        table += "</tr></table>"


        html = css + table

        # css_label = "<style>"
        # css_label += "td.chord{"
        # css_label += "vertical-align:top;"
        # css_label += "line-height:56%;"
        # css_label += "padding:0px;"
        # css_label += "}"
        # css_label += "</style>"
        
        Plot.tabs_label.setText(css_label+table)
        Plot.tabs_label.setFont(QFont(Plot.get_font(settings.tabs_font),40))



        
        if  data.render_video:
            if export:
                frame = preview.get_export_frame_at(time)
            else:
                frame = preview.get_preview_frame_at(time)
            
            if not hasattr(frame, 'shape'):
                return None,False
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
        else:
            image = QImage(QSize(w,h),QImage.Format_RGB888)
            image.fill(colors.black)

        if export:
            p = QPainter(image)
        else:
            cv2pm = QPixmap.fromImage(image)
            p = QPainter(cv2pm)

        
        #draw shades
        if len(ptabs):
            shcol = QColor(0,0,0,round(255*data.transparency))
            p.setPen(shcol)
            p.setBrush(shcol)
            p.drawRect(0,0,w,round(h*data.shade_top))
            p.drawRect(0,round(h*data.shade_bottom),w,h-round(h*data.shade_bottom))


        
        if data.render_tabs and len(ptabs):
            text_doc = QTextDocument()
            font = QFont(Plot.get_font(settings.tabs_font),f(1))
            text_doc.setDefaultFont(font)
            text_doc.setHtml(html)
            pm = QPixmap(text_doc.size().toSize())
            pm.fill(Qt.transparent)
            pixmapPainter = QPainter(pm)
            text_doc.drawContents(pixmapPainter)
            pixmapPainter.end()
 
            # Center the text item within the scene
            text_width = pm.size().width()
            pos = QPointF((w - text_width) / 2, h*data.tab_offset)
            if data.tab_background:
                Plot.rr(p,pos.x()-f(.4),pos.y(),pm.size().width()+f(.8),pm.size().height(),r(1),colors.tab_backgroung_color,fill=colors.fill_tabs_background)

            p.drawPixmap(pos,pm)



        if  data.render_harmonica and len(ptabs):
            if active_tab and "*" in active_tab['tab']:
                Plot.draw_slide(p,True)
            elif data.n_holes>10:
                Plot.draw_slide(p,False)
            Plot.draw_harmonica(p)
            if active_tab and active_tab['tab']!="na":
                
                

                # Calculate text position to center it within the rectangle
                if active_tab['chord']<8:
                    for i in range(active_tab['chord']):
                        Plot.draw_active_tab(p,active_tab,active_hole,i)
                else:
                    Plot.draw_active_tab(p,active_tab,active_hole)
                    if data.n_holes == 12:
                        Plot.draw_active_tab(p,active_tab,active_hole,4)
                    elif data.n_holes == 10 and ("-" in active_tab["tab"]):
                        Plot.draw_active_tab(p,active_tab,active_hole,4)
                    else:
                        Plot.draw_active_tab(p,active_tab,active_hole,3)
                    

        p.end()
        

        if export:

            buffer = image.bits().asstring(w * h * 3)  # Calculate the buffer size
            rgb_frame = np.frombuffer(buffer, dtype=np.uint8).reshape(h, w, 3)
            cv2_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2RGB)
            return cv2_frame, True
        
        else:
            Plot.image_label.setPixmap(cv2pm)

    def timer_callback():
        
        Plot.cpu_label.setText("CPU " + data.cpu_usage)
        if Plot.start_idx > (Plot.total_frames - Plot.sr * .25):
            Plot.stop()
            return
        time=(Plot.start_idx/Plot.sr)
        if Plot.time_line:
            Plot.loc = grid.timetox(time)
            Plot.time_line.setX(Plot.loc)
        if Plot.timer.isActive():
            Plot.bar.setSliderPosition(Plot.loc-500)

        Plot.render_video_at(time)

    def rr(p:Optional[QPainter],x,y,w,h,r,col, fill=True):
        rect = QRectF(x,y,w,h)
        p.setPen(QPen(col,2))
        if fill:
            p.setBrush(QBrush(col))
        if not fill:
            p.setBrush(QBrush())
            
        p.drawRoundedRect(rect,r,r)

    def draw_harmonica(p:Optional[QPainter]):
        global offset_x
        if data.n_holes==12:
            
            w1 = r(12)
            w2 = r(11.7)
            w3 = r(13.6)
        else:
            
            w1 = r(10.1)
            w2 = r(9.7)
            w3 = r(11.6)
        
        Plot.rr(p,x(.8), y(.45),w1, r(.8),r(.4),colors.dark_grey)
        Plot.rr(p,x(1.0), y(1.7),w2, r(.4),r(.4),colors.dark_grey)
        Plot.rr(p,x(.0), y(.8),w3, r(1.1),r(.2),colors.light_grey)
        
        for i in range(data.n_holes):
            hx = x(1)+r(i)
            ahx = x(.97)+r(i)
            ahy = y(.97)
            ahw = ahh = r(.76)
            if platform.system() == "Linux":

                harm_marks_font = QFont("KacstOne",round(r(0.3)))
            else:

                harm_marks_font = QFont("Optima",round(r(0.4)))

            p.setFont(harm_marks_font)
            text_rect = QFontMetrics(harm_marks_font).boundingRect(str(i+1))
            text_x = ahx + (ahw - text_rect.width()) / 2
                          
            p.setPen(QColor(220,220,220))
            p.drawText(QPointF(text_x, y(.75)),str(i+1))    
            
            #Plot.rr(p,hx, y(1),r(.7), r(.7),r(.1),QColor(0,0,0))
            Plot.rr(p,ahx, ahy,ahw,ahh,r(.13),QColor(0,0,0))

    def draw_active_tab(p:Optional[QPainter],active_tab,active_hole,chord_offset = 0):   
        
        active_tab_font = QFont("Geeza Pro Interface",round(r(0.4)))
        p.setFont(active_tab_font)
        holec = active_hole+chord_offset
        tab_text = active_tab["tab"].replace(str(active_hole),str(holec))
        ahx = x(.95)+r(holec-1)
        ahy = y(.95)
        ahw = ahh = r(.8)
        Plot.rr(p,ahx, ahy,ahw,ahh,r(.13),active_tab['color'])
        
        text_rect = QFontMetrics(active_tab_font).boundingRect(str(holec))
        text_x = ahx + (ahw - text_rect.width()) / 2
        text_y = y(1.5)

        
        p.setPen(colors.white)
        p.drawText(QPointF(text_x, text_y),tab_text.replace("-", ""))    
        if "-" in tab_text:
            p.drawText(QPointF(text_x-r(.2), text_y),"-")     

    def draw_slide(p:Optional[QPainter],pushed):

        slide_start_x = x(13.1) if pushed else x(13.5)
        slide_start_y = y(.8)
        slide_end_y= y(1.9)
        slide_end_x = slide_start_x + r(1.3)
        slide_w = r(1.3)
        slide_h = r(1.1)
        path = QPainterPath()
        path.moveTo(slide_start_x, slide_start_y)
        path.arcTo(slide_start_x, slide_start_y-r(.3),slide_w, r(.6), 180, 180)
        path.lineTo(slide_end_x,slide_end_y)
        path.arcTo(slide_start_x, slide_end_y-r(.3),slide_w, r(.6), 0, 180)
        path.lineTo(slide_start_x, slide_start_y)
      
        p.setPen(colors.dark_grey)
        p.setBrush(colors.dark_grey)
        p.drawPath(path)
        
        ew = r(.18)
        ex = slide_end_x - ew/2 
        ey = slide_start_y
        eh= slide_h
        p.setPen(colors.light_grey)
        p.setBrush(colors.light_grey)
        p.drawEllipse(QRectF(ex,ey,ew,eh))

    def export_video(file_name):

        if platform.system() == "Linux":
            os.environ['QT_QPA_PLATFORM'] = "xcb"
        preview.prepare_export()
        
        
        print("exporting")
        Plot.update_video()
        file_prefix = file_name.split(".")[0]
        #fps=preview.export_video_capture.get(cv2.CAP_PROP_FPS)
        print(preview.fps)
        global writing
        writing = 1

        # Create a VideoWriter object
        output_path = './tmp/output.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        output_video = cv2.VideoWriter(output_path, fourcc, preview.fps, (preview.w, preview.h))
        frame_count = 0

        n_frames = int(preview.export_video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        ret = 1
        while ret:
                        
            cv2_frame,ret = Plot.render_video_at(frame_count/preview.fps,export=True)
            if not ret:
                print(f"export failed at {frame_count}")
                break
            frame_count += 1
            if frame_count % 50 == 0:
                print(f" writing {frame_count} of {n_frames}", end='\r')
            #cv2.imshow("",cv2_frame)    
            # cv2.waitKey(1)        
            output_video.write(cv2_frame)

        output_video.release()
        
        video_clip = VideoFileClip(output_path)
        if preview.video_file:
            video_clip = video_clip.set_audio(VideoFileClip(preview.video_file).audio)
        else:
            video_clip = video_clip.set_audio("./tmp/audio.wav")
        output_path_with_audio = file_prefix+'.mp4'
        video_clip.write_videofile(
            output_path_with_audio, codec='libx264', audio_codec='aac')


       
        writing = 0
        if platform.system() == "Linux":
            os.environ['QT_QPA_PLATFORM'] = "dxcb"
    
    def export_preview():
        if platform.system() == "Linux":
            os.environ['QT_QPA_PLATFORM'] = "xcb"
        
        print("export preview")
        Plot.update_video()
  
      
        #print(preview.w,preview.h)
        frame_count = 0
        ret = 1
        while frame_count<(preview.fps*2):
                        
            cv2_frame,ret = Plot.render_video_at(frame_count/preview.fps,export=True)
            frame_count+=1
            if not ret:
                break
            cv2.imshow("",cv2_frame)    
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break      

        cv2.destroyAllWindows()
        if platform.system() == "Linux":   
            os.environ['QT_QPA_PLATFORM'] = "dxcb"
      
        
    def copy(self):
        selected_notes = Plot.scene_obj.selectedItems()
        self.clipboard = []
        for note in selected_notes:
            if isinstance(note, QNoteRect):
                self.clipboard.append(note)
    def paste(self):
        for note in self.clipboard:
            if isinstance(note, QNoteRect):
                note.setSelected(False) 
        cmd.PasteCommand(self)
        Plot.update_video()

    def get_font(font_constant):
            ff = QFontDatabase().families()[font_constant]
            
            return ff    

        




