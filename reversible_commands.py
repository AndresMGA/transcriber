from PyQt5.QtWidgets import   QUndoCommand
from PyQt5.QtGui import  QPen, QColor , QBrush
import undo_redo as ur
import grid
pen = QPen(QColor(250, 0, 0,100))
brush = QBrush(QColor(250, 0, 0,100))
pen_opt = QPen(QColor(0, 250, 250,100))
brush_opt = QBrush(QColor(0, 250, 250,100))


class MoveCommand(QUndoCommand):
    def __init__(self, view,notes,  parent=None):
        super().__init__(parent)
        self.view = view
        self.notes = []
        self.old_positions = []
        self.new_positions = []
        for note in notes:
            note.setPos(note.pos().x(),grid.snap(note.pos().y()))
            self.notes += [note]
            self.old_positions += [note.old_pos]
            self.new_positions += [note.pos()]
            
        
        ur.undo_stack.push(self)
        
    def redo(self):
        for i,note in enumerate(self.notes):
            note.setPos(self.new_positions[i])
            self.view._update_video()
       
        
        
            
        
    def undo(self):
        for i,note in enumerate(self.notes):
            note.setPos(self.old_positions[i])
            self.view._update_video()
       
       


class ChangeWidthCommand(QUndoCommand):
    def __init__(self,  notes,  parent=None):
        super().__init__(parent)
        
        self.notes = []
        self.old_rects = []
        self.new_rects = []
        for note in notes:
            #note.setPos(note.pos().x(),grid.snap(note.pos().y()))
            self.notes += [note]
            self.old_rects += [note.old_rect]
            self.new_rects += [note.rect()]
            
        
        ur.undo_stack.push(self)
        
    def redo(self):
        for i,note in enumerate(self.notes):
            note.setRect(self.new_rects[i])
            
        
    def undo(self):
        for i,note in enumerate(self.notes):
            note.setRect(self.old_rects[i])

            

class AddNoteCommand(QUndoCommand):
    def __init__(self, view, x, y):
        super().__init__()
        self.view = view
        self.x = x
        self.y = y
        self.note = None
        ur.undo_stack.push(self)

    def redo(self):
        self.note= self.view.addNote(self.x, grid.snap(self.y))
        self.view._update_video()
        

    def undo(self):
        self.view.scene().removeItem(self.note)
        self.view._update_video()
        

class PasteCommand(QUndoCommand):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.clipboard = view.clipboard.copy()
        self.bin = []
        ur.undo_stack.push(self)

    def redo(self):
        self.bin = []
        for note in self.clipboard:
            self.bin += [self.view.addNote(note.rect().x()+grid.grid, note.rect().y()+grid.grid,selected = True)]
        self.view._update_video()

    def undo(self):
        for note in self.bin:
            self.view.scene().removeItem(note)
        self.view._update_video()
       
        

class DeleteCommand(QUndoCommand):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.selected_notes = []
        ur.undo_stack.push(self)

    def redo(self):
        self.selected_notes = self.view.scene().selectedItems()
        for note in self.selected_notes:
            self.view.scene().removeItem(note)
        self.view._update_video()
        
    def undo(self):
        for note in self.selected_notes:
            self.view.scene().addItem(note)  
        self.view._update_video()
        


class AddSceneCommand(QUndoCommand):
    def __init__(self, view, pos, parent=None):
        super().__init__(parent)
        self.view = view
        self.pos = pos
        self.item = None
        ur.undo_stack.push(self)

    def redo(self):
        self.item = self.view.addNewPhrase(self.pos.x())
        
        self.view._update_video()
        

    def undo(self):
        self.view.scene().removeItem(self.item)
        self.view._update_video()
        

class OpTabCommand(QUndoCommand):
    def __init__(self, view, parent=None):
        super().__init__(parent)
        self.view = view
        self.items = []
        ur.undo_stack.push(self)
    def redo(self):
        selected_items = self.view.scene().selectedItems()
        self.items = selected_items.copy()
        for item in selected_items:
                if not item.optional_tab:
                    item.setPen(pen_opt)
                    item.setBrush(brush_opt)
                    item.optional_tab = 1
                    
                else:
                    item.setPen(pen)
                    item.setBrush(brush)
                    item.optional_tab = 0
        self.view._update_video()
                   
        
    def undo(self):
        self.redo()
        self.view._update_video()
        

class ChordCommand(QUndoCommand):
    def __init__(self, view, chord, parent=None):
        super().__init__(parent)
        self.view = view
        self.items = []
        self.chord = chord
        ur.undo_stack.push(self)
    def redo(self):
        selected_items = self.view.scene().selectedItems()
        self.items = selected_items.copy()
        for item in selected_items:
                    
                    item.chord = self.chord
                    
                    item.setRect(item.rect().x(),item.rect().y(),item.rect().width(),grid.grid*(1 if item.chord<2 else item.chord))
           
        self.view._update_video()
                   
        
    def undo(self):
        self.redo()
        self.view._update_video()