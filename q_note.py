
from PyQt5.QtCore import QRectF,QPointF,QRect 
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import   QGraphicsRectItem, QGraphicsSceneMouseEvent, QToolTip
import preview
import reversible_commands as cmd
import grid
import numpy as np
import data
import sounddevice as sd

class QNoteRect(QGraphicsRectItem):
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.old_pos = QPointF(x,y)
        self.old_width = width
        self.old_rect = QRectF(x,y,width,height)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        QToolTip.setFont(QFont("Currier New",20))
        self.resizing = False
        self.moving =False
        self.optional_tab = 0
        self.time = grid.xtotime(x)
        self.onset = grid.ytomidi(y)
        self.tab = "na"
        self.chord = 1
        
        
       
    def mousePressEvent(self, event):
        # edge = -(event.pos().x()-self.rect().x()-self.rect().width())
        # if edge<10:
        #     self.resizing=True

        
        #sd.wait()  # Wait for the tone to finish playing
        self.tone()
        self.displayTab(event)
        for selectedItem in self.scene().selectedItems():
            if isinstance(selectedItem,QNoteRect):
                selectedItem.old_pos = selectedItem.pos()
                selectedItem.old_width = selectedItem.rect().width()
                selectedItem.old_rect = selectedItem.rect()
        super().mousePressEvent(event)

       
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        sd.stop()
        self.displayTab(event)
        cmd.MoveCommand(self.scene().views()[0],self.scene().selectedItems())
        self.update()
        if self.moving:
            self.scene().views()[0]._update_video()
            self.moving=False
        # if self.resizing:
        #     cmd.ChangeWidthCommand(self.scene().selectedItems())
        #     self.resizing = False
        # else:
        #     cmd.MoveCommand(self.scene().selectedItems())
        return super().mouseReleaseEvent(event)
   
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        self.moving =True
        self.update()
        self.displayTab(event)
        # if self.resizing:
        #     self.resizeNotes(event.pos().x())
        #     return
        return super().mouseMoveEvent(event)

    def resizeNotes(self,evt_x):
            newWidth = evt_x-self.rect().x()
            diff = newWidth - self.rect().width()
            for note in self.scene().selectedItems():
                if isinstance(note,QNoteRect):
                    note.setRect(note.rect().x(),note.rect().y(),note.rect().width()+diff,note.rect().height())
                    if note.rect().width()<10:
                        note.setRect(note.rect().x(),note.rect().y(),10,note.rect().height())

    def update(self):
        pos = self.mapToScene(self.rect().topLeft())
        onset = grid.ytomidi(pos.y())
        if self.onset != onset:
            self.onset = onset
            sd.stop()
            self.tone()
        self.time = grid.xtotime(pos.x())
  
    def getTab(self):
        t = 14-preview.data.n_holes+self.optional_tab
        tab = preview.data.notes_info[self.onset][t]
        return tab
    
    def displayTab(self,event):
        QToolTip.showText(event.screenPos(), str(self.getTab()),self.scene().views()[0],QRect(int(event.pos().x()),int(event.pos().y()),30,30),5000)
    
    def tone(self):
        frequency = float(data.notes_info[self.onset][6])
        sr = 44100
        t = np.linspace(0, 2, int(sr * 2), False)
        tone = np.sin(2 * np.pi * frequency * t)
        sd.play(tone*.3, samplerate=sr)




