import os
import platform
if platform.system() == "Linux":
    os.environ['QT_QPA_PLATFORM'] = "dxcb"
from PyQt5.QtCore import Qt, QTimer,QRectF
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu,QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QColor , QFont,QPalette, QKeySequence, QImage, QPixmap
from plot import Plot
import json
import numpy as np
import cv2
from qdarkstyle import load_stylesheet_pyqt5
from PyQt5.QtCore import QT_VERSION_STR, QProcess
from moviepy.editor import VideoFileClip
import preview
import data
import grid
import settings
qt_version = QT_VERSION_STR
print(qt_version)
plot_W_no_video = 1260
plot_W_video = 950
#1366, 768
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.graphicsView = Plot(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(15, 60, plot_W_no_video,  grid.grid*42))
        self.graphicsView.setObjectName("graphicsView")

        self.img = QtWidgets.QLabel(self.centralwidget)
        self.img.setGeometry(QtCore.QRect(plot_W_video+30, 8, 636, 636))
        self.img.setObjectName("img")
        Plot.image_label = self.img
       
        
        
        self.radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton.setGeometry(QtCore.QRect(20, 20, 91, 22))
        self.radioButton.setObjectName("radioButton")
        self.radioButton.setChecked(1)
        self.radioButton.clicked.connect(self.write_tabs)
        self.radioButton_2 = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton_2.setGeometry(QtCore.QRect(110, 20, 105, 22))
        self.radioButton_2.setObjectName("radioButton_2")
        self.radioButton_2.clicked.connect(self.write_tabs)
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(400, 30, 160, 20))
        self.horizontalSlider.setMinimum(50)
        self.horizontalSlider.setMaximum(200)
        self.horizontalSlider.setValue(100)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.valueChanged.connect(self.graphicsView.zoom_changed)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(450, 10, 58, 18))
        self.label.setObjectName("label")

        self.cpu_label = QtWidgets.QLabel(self.centralwidget)
        self.cpu_label.setGeometry(20,grid.grid*49,60,30)
        #self.cpu_label.setMinimumSize(700, 60)  # Set a minimum size for the QLabel
        self.cpu_label.setFont(QFont("Currier New",10))
        self.cpu_label.setText(data.cpu_usage)
        Plot.cpu_label = self.cpu_label



        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(190, 15, 88, 30))
        self.checkBox.setObjectName("checkBox")
        self.checkBox.stateChanged.connect(self.graphicsView.set_speed)
        self.checkBox1 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox1.setGeometry(QtCore.QRect(280, 15, 120, 30))
        self.checkBox1.setObjectName("checkBox")
        self.checkBox1.stateChanged.connect(self.graphicsView.set_original_audio)
        self.checkBox2 = QtWidgets.QCheckBox(self.centralwidget)
        x = 590
        sep = 65
        self.checkBox2.setGeometry(QtCore.QRect(x, 15, 88, 30))
        self.checkBox2.setObjectName("checkBox2")
        self.checkBox2.stateChanged.connect(self.video_render_settings)
        self.checkBox3 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox3.setGeometry(QtCore.QRect(x+1*sep-8, 15, 88, 30))
        self.checkBox3.setObjectName("checkBox3")
        self.checkBox3.stateChanged.connect(self.video_render_settings)
        self.checkBox4 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox4.setGeometry(QtCore.QRect(x+2*sep-11, 15, 88, 30))
        self.checkBox4.setObjectName("checkBox4")
        self.checkBox4.stateChanged.connect(self.video_render_settings)
        self.checkBox5 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox5.setGeometry(QtCore.QRect(x+3*sep-25, 15, 150, 30))
        self.checkBox5.setObjectName("checkBox5")
        self.checkBox5.stateChanged.connect(self.video_render_settings)
        self.checkBox6 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox6.setGeometry(QtCore.QRect(x+4*sep+5, 15, 110, 30))
        self.checkBox6.setObjectName("checkBox6")
        self.checkBox6.stateChanged.connect(self.video_render_settings)

        self.checkBox.setFocusPolicy(Qt.NoFocus)
        self.checkBox1.setFocusPolicy(Qt.NoFocus)
        self.checkBox2.setFocusPolicy(Qt.NoFocus)
        self.checkBox3.setFocusPolicy(Qt.NoFocus)
        self.checkBox4.setFocusPolicy(Qt.NoFocus)
        self.checkBox5.setFocusPolicy(Qt.NoFocus)
        self.checkBox6.setFocusPolicy(Qt.NoFocus)
        self.horizontalSlider.setFocusPolicy(Qt.NoFocus)
        self.radioButton.setFocusPolicy(Qt.NoFocus)
        self.radioButton_2.setFocusPolicy(Qt.NoFocus)
      
        
              
        # self.timer = QTimer(self.centralwidget)
        # self.timer.timeout.connect(self.update_frame)
        # self.timer.start(50)  # Set the timer interval in milliseconds (30 ms = 33.33 fps)

        self.harmSizeSlider = QtWidgets.QSpinBox(self.centralwidget)
        self.harmOffsetSlider = QtWidgets.QSpinBox(self.centralwidget)
        self.tabsSizeSlider = QtWidgets.QSpinBox(self.centralwidget)
        self.tabsOffsetSlider = QtWidgets.QSpinBox(self.centralwidget)
        self.transparency = QtWidgets.QSpinBox(self.centralwidget)
        self.shadeTop = QtWidgets.QSpinBox(self.centralwidget)
        self.shadeBottom = QtWidgets.QSpinBox(self.centralwidget)
        self.rotate = QtWidgets.QSpinBox(self.centralwidget)
        self.font = QtWidgets.QSpinBox(self.centralwidget)
        self.fonth = QtWidgets.QSpinBox(self.centralwidget)
        self.fonth.hide()
        y = int(grid.grid*47.5)
        x = 100
        sep = 70
        self.tabs_label = QtWidgets.QLabel(self.centralwidget)
        self.tabs_label.setGeometry(x+sep*11,750,1000,80)
        Plot.tabs_label = self.tabs_label

        self.harmSizeSlider.setGeometry(QtCore.QRect(x, y, 50, 45))
        self.harmOffsetSlider.setGeometry(QtCore.QRect(x+1*sep, y, 50, 45))
        self.tabsSizeSlider.setGeometry(QtCore.QRect(x+2*sep, y, 50, 45))
        self.tabsOffsetSlider.setGeometry(QtCore.QRect(x+3*sep, y, 50, 45))
        self.transparency.setGeometry(QtCore.QRect(x+4*sep, y, 50, 45))
        self.shadeTop.setGeometry(QtCore.QRect(x+5*sep, y, 50, 45))
        self.shadeBottom.setGeometry(QtCore.QRect(x+6*sep, y, 50, 45))
        self.rotate.setGeometry(QtCore.QRect(x+7*sep, y, 50, 45))
        self.font.setGeometry(QtCore.QRect(x+8*sep, y, 70, 45))
        self.fonth.setGeometry(QtCore.QRect(x+9*sep+20, y, 70, 45))

        self.harmSizeSliderl = QtWidgets.QLabel(self.centralwidget)
        self.harmOffsetSliderl = QtWidgets.QLabel(self.centralwidget)
        self.tabsSizeSliderl = QtWidgets.QLabel(self.centralwidget)
        self.tabsOffsetSliderl = QtWidgets.QLabel(self.centralwidget)
        self.transparencyl = QtWidgets.QLabel(self.centralwidget)
        self.shadeTopl = QtWidgets.QLabel(self.centralwidget)
        self.shadeBottoml = QtWidgets.QLabel(self.centralwidget)
        self.rotatel = QtWidgets.QLabel(self.centralwidget)
        self.fontl = QtWidgets.QLabel(self.centralwidget)
        self.fonthl = QtWidgets.QLabel(self.centralwidget)
        self.fonthl.hide()
        y = int(grid.grid * 51.3)
        self.harmSizeSliderl.setGeometry(QtCore.QRect(x, y, 150, 30))
        self.harmOffsetSliderl.setGeometry(QtCore.QRect(x+1*sep,y, 150, 30))
        self.tabsSizeSliderl.setGeometry(QtCore.QRect(x+2*sep, y, 150, 30))
        self.tabsOffsetSliderl.setGeometry(QtCore.QRect(x+3*sep, y, 150, 30))
        self.transparencyl.setGeometry(QtCore.QRect(x+4*sep, y, 150, 30))
        self.shadeTopl.setGeometry(QtCore.QRect(x+5*sep, y, 150, 30))
        self.shadeBottoml.setGeometry(QtCore.QRect(x+6*sep, y, 150, 30))
        self.rotatel.setGeometry(QtCore.QRect(x+7*sep, y, 150, 30))
        self.fontl.setGeometry(QtCore.QRect(x+8*sep, y, 150, 30))
        self.fonthl.setGeometry(QtCore.QRect(x+9*sep+20, y, 150, 30))
        
        self.harmSizeSliderl.setText("H Size")
        self.harmOffsetSliderl.setText("H Pos")
        self.tabsSizeSliderl.setText("T Size")
        self.tabsOffsetSliderl.setText("T Pos")
        self.transparencyl.setText("Shade")
        self.shadeTopl.setText("Sh Top")
        self.shadeBottoml.setText("Sh Bott")
        self.rotatel.setText("Rotate")
        self.fontl.setText("Font")
        self.fonthl.setText("FontH")

        self.harmSizeSlider.setMinimum(0)
        self.harmSizeSlider.setMaximum(50)
        self.harmSizeSlider.setValue(22)

        self.harmOffsetSlider.setMinimum(0)
        self.harmOffsetSlider.setMaximum(100)
        self.harmOffsetSlider.setValue(90)

        self.tabsSizeSlider.setMinimum(10)
        self.tabsSizeSlider.setMaximum(40)
        self.tabsSizeSlider.setValue(21)

        self.tabsOffsetSlider.setMinimum(0)
        self.tabsOffsetSlider.setMaximum(100)
        self.tabsOffsetSlider.setValue(10)

        self.transparency.setMinimum(0)
        self.transparency.setMaximum(100)
        self.transparency.setValue(30)

        self.shadeTop.setMinimum(0)
        self.shadeTop.setMaximum(100)
        self.shadeTop.setValue(30)
        
        self.shadeBottom.setMinimum(0)
        self.shadeBottom.setMaximum(100)
        self.shadeBottom.setValue(70)

        self.rotate.setMinimum(0)
        self.rotate.setMaximum(3)
        self.rotate.setValue(0)

        self.font.setMinimum(0)
        self.font.setMaximum(3318)
        self.font.setValue(0)

        self.fonth.setMinimum(0)
        self.fonth.setMaximum(3318)
        self.fonth.setValue(45)

        self.harmSizeSlider.valueChanged.connect(Ui_MainWindow.set_harm_size)
        self.harmOffsetSlider.valueChanged.connect(Ui_MainWindow.set_harm_offset)
        self.tabsSizeSlider.valueChanged.connect(Ui_MainWindow.set_tab_size)
        self.tabsOffsetSlider.valueChanged.connect(Ui_MainWindow.set_tab_offset)
        self.transparency.valueChanged.connect(Ui_MainWindow.set_transparency)
        self.shadeTop.valueChanged.connect(Ui_MainWindow.set_shade_top)
        self.shadeBottom.valueChanged.connect(Ui_MainWindow.set_shade_bottom)
        self.rotate.valueChanged.connect(Ui_MainWindow.set_rotate)
        self.font.valueChanged.connect(Ui_MainWindow.set_font)
        self.fonth.valueChanged.connect(Ui_MainWindow.set_fontH)


        self.horizontalSlider.valueChanged.connect(self.graphicsView.zoom_changed)
       
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1566, 30))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        # Add the File menu and its submenus
        file_menu = QMenu("File", self.centralwidget)
        self.menubar.addMenu(file_menu)

        open_project_action = QAction("Open Project", self.centralwidget)
        open_project_action.setShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_O))
        open_project_action.triggered.connect(self.open_project_dialog)
        file_menu.addAction(open_project_action)

        # open_audio_action = QAction("New Project from Audio", self.centralwidget)
        # open_audio_action.triggered.connect(self.open_audio_dialog)
        # #open_audio_action.setShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_A))
        # file_menu.addAction(open_audio_action)

        open_video_action = QAction("New Project from Video", self.centralwidget)
        #open_video_action.setShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_V))
        open_video_action.triggered.connect(self.open_video_dialog)
        file_menu.addAction(open_video_action)

        save_project_action = QAction("Save Project", self.centralwidget)
        save_project_action.setShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_S))
        save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(save_project_action)

        save_project_as_action = QAction("Save Project As", self.centralwidget)
        #save_project_action.setShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_S))
        save_project_as_action.triggered.connect(self.save_dialog)
        file_menu.addAction(save_project_as_action)

        sync_video_action = QAction("Sync Video", self.centralwidget)
        #sync_video_action.setShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_E))
        sync_video_action.triggered.connect(self.graphicsView.sync_video)
        file_menu.addAction(sync_video_action)

        export_video_action = QAction("Export Video", self.centralwidget)
        export_video_action.setShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_E))
        export_video_action.triggered.connect(self.export_video_dialog)
        file_menu.addAction(export_video_action)

        # Add the Edit menu and its submenus
        help = QMenu("Help", self.centralwidget)
        self.menubar.addMenu(help)

        help_action = QAction("Show Help", self.centralwidget)
        help_action.triggered.connect(self.show_help)
        help.addAction(help_action)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.window = MainWindow
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.checkBox1.setChecked(1)
        self.checkBox2.setChecked(1)
        self.checkBox3.setChecked(1)
        self.checkBox4.setChecked(1)
        self.checkBox5.setChecked(0)
        self.checkBox6.setChecked(1)
        

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Harmonica Transciber "))
        self.radioButton.setText(_translate("MainWindow", "chromatic"))
        self.radioButton_2.setText(_translate("MainWindow", "diatonic"))
        self.label.setText(_translate("MainWindow", "zoom"))
        self.checkBox.setText(_translate("MainWindow", "Half speed"))
        self.checkBox1.setText(_translate("MainWindow", "Original audio"))
        self.checkBox2.setText(_translate("MainWindow", "video"))
        self.checkBox3.setText(_translate("MainWindow", "harmo"))
        self.checkBox4.setText(_translate("MainWindow", "tabs"))
        self.checkBox5.setText(_translate("MainWindow", "tabs frame"))
        self.checkBox6.setText(_translate("MainWindow", "update only"))

    def write_tabs(self):
        Plot.stop()
        data.n_holes = 12
        if self.radioButton_2.isChecked():
            data.n_holes = 10
        self.graphicsView.write_tabs()
        Plot.update_video()
    def show_popup_message(self, message):
        # Create a QMessageBox
        popup = QtWidgets.QMessageBox(self.centralwidget)
        popup.setWindowTitle("Popup Message")
        popup.setText(message)
        popup.setIcon(QtWidgets.QMessageBox.Information)

        # Add buttons to the popup (optional)
        popup.addButton(QtWidgets.QMessageBox.Ok)
        popup.addButton(QtWidgets.QMessageBox.Cancel)

        # Show the popup and handle the result
        result = popup.exec_()

        # You can handle the result here if needed
        if result == QtWidgets.QMessageBox.Ok:
            print("OK clicked")
        elif result == QtWidgets.QMessageBox.Cancel:
            print("Cancel clicked")
    def save_project(self):
        if Plot.project_file == None:
            self.save_dialog()
        else:
            with open(Plot.project_file, "w") as file:
                json.dump(Plot.get_json(), file,indent=4)

        self.show_popup_message("project saved as "+Plot.project_file)
    
    def convert_to_python_float(self,o):
        if isinstance(o, np.float32):
            return float(o)
        raise TypeError("Object of type {} is not JSON serializable".format(type(o)))

    def show_help(self):
        help = ""
        help = help + "Double Click    =>  add a note\n"
        help = help + "Click + O       =>  toogle optional tab\n"
        help = help + "Click + Shift   =>  set player position\n"
        help = help + "Click + Control =>  add scene\n"
        help = help + "Delete          =>  delete selection\n"


        self.show_popup_message(help)
    def save_dialog(self):
        file_dialog = QtWidgets.QFileDialog(caption = 'Save', directory='./', filter= '*.json')
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setNameFilters(['Project File (*.json)'])
        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_file = file_dialog.selectedFiles()[0]
        Plot.project_file = selected_file
        with open(selected_file, "w") as file:
            json.dump(Plot.get_json(),file,indent=4)
            
        
    def export_video_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        file_filter = "All Files (*.*)"
        video_file, _ = QtWidgets.QFileDialog.getSaveFileName(self.centralwidget, "Export Video", "", file_filter, options=options)
        Plot.export_video(video_file)
    def open_video_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        file_filter = "Video Files (*.mp4 *.avi *.mov *.mkv *.m4a)"
        video_file, _ = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget, "Open Video", "", file_filter, options=options)
        video_clip = VideoFileClip(video_file)
        video_width, video_height = video_clip.size
        
        if video_clip.rotation == 90 or video_clip.rotation == 270:
            video_height, video_width = video_clip.size
        else:
            video_width, video_height = video_clip.size

        if video_height>video_width:
            self.load_settings()
        else:
            self.load_settings()

        audio_clip = video_clip.audio
        audio_clip.write_audiofile("./tmp/audio.wav")
        video_clip.close()
        audio_clip.close()
        Plot.clear_data()
        self.radioButton.setChecked(1)
        self.write_tabs()
        self.horizontalSlider.setValue(grid.pixels_per_second)
        print("analising")
        Plot.analyse("./tmp/audio.wav")
        print("synthesizing")
        Plot.synth()
        print("synth done")
        
        self.graphicsView.plot_array()
        data.video_file = video_file
        Plot.update_video()
        self.window.setWindowTitle("New Project from Video File")
       
    def open_audio_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        file_filter = "Audio Files (*.mp3 *.wav *.ogg)"
        audio_file, _ = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget, "Open Audio", "", file_filter, options=options)
        Plot.clear_data()
        self.radioButton.setChecked(1)
        #self.write_tabs()
        self.horizontalSlider.setValue(grid.pixels_per_second)
        self.load_settings()
        print("analising")
        Plot.analyse(audio_file)
        print("synthesizing")
        Plot.synth()
        print("synth done")
        self.graphicsView.plot_array()
        Plot.update_video()
        self.window.setWindowTitle("New Project from Audio File")

    def open_project_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        file_filter = "Project Files (*.json)"
        project_file, _ = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget, "Open Project", "", file_filter, options=options)
        self.open_project(project_file)
        

    def open_project(self,project_file):
        Plot.stop()
        Plot.clear_data()
        Plot.load_json(project_file)
        video_clip = None
        try:
            video_clip = VideoFileClip(data.video_file)
        except:
            self.show_popup_message("Donde esta el video!!!!!!!!")
            return
        
        audio_clip = video_clip.audio
        audio_clip.write_audiofile("./tmp/audio.wav")
        video_clip.close()
        audio_clip.close()
        self.set_spinners()
        if data.n_holes == 12:
            self.radioButton.setChecked(1)
        else:
            self.radioButton_2.setChecked(1)
        
        self.write_tabs()
        print("analising")
        Plot.analyse("./tmp/audio.wav",False)
        print("synthesizing")
        Plot.synth()
        print("synth done")
        self.graphicsView.plot_array()
        self.horizontalSlider.setValue(grid.pixels_per_second)
        preview.update()
        #Plot.update_video()
       
        print(Plot.project_file)
        self.window.setWindowTitle(Plot.project_file)

    def set_spinners(self):
        self.harmSizeSlider.setValue(data.harm_size)
        self.harmOffsetSlider.setValue(round(100-data.harm_offset*100))
        self.tabsSizeSlider.setValue(round(data.tab_size))
        self.tabsOffsetSlider.setValue(round(100-data.tab_offset*100))
        self.transparency.setValue(round(data.transparency*100))
        self.shadeTop.setValue(round(100-data.shade_top*100))
        self.shadeBottom.setValue(round(100-data.shade_bottom*100))
        self.font.setValue(settings.tabs_font)
        self.fonth.setValue(settings.harm_font)
        #self.fonth.setValue(data.fontH)
    def load_settings(self):
        self.harmSizeSlider.setValue(settings.harmonica_size)
        self.harmOffsetSlider.setValue(settings.harmonica_position)
        self.tabsSizeSlider.setValue(settings.tabs_size)
        self.tabsOffsetSlider.setValue(settings.tabs_position)
        self.transparency.setValue(settings.shade_opacity)
        self.shadeTop.setValue(settings.shade_top)
        self.shadeBottom.setValue(settings.shade_bottom)
        self.rotate.setValue(settings.rotate)
        self.font.setValue(settings.tabs_font)
        self.fonth.setValue(settings.harm_font)


   

    def video_render_settings(self):
        Plot.stop()
        data.render_video = self.checkBox2.isChecked()
        data.render_harmonica = self.checkBox3.isChecked()
        data.render_tabs = self.checkBox4.isChecked()
        data.tab_background = self.checkBox5.isChecked()
        data.update_only = self.checkBox6.isChecked()
        
        if  data.render_tabs + data.render_harmonica + data.render_video == 0:
            self.graphicsView.setGeometry(QtCore.QRect(15, 60, plot_W_no_video,  grid.grid*42))
            Plot.image_label.hide()
        else: 
            self.graphicsView.setGeometry(QtCore.QRect(15, 60, plot_W_video,  grid.grid*42))
            Plot.image_label.show()
        Plot.interval = 50# + 100 * data.render_video
        Plot.update_video()

    def set_harm_size(value):
        data.harm_size = value
        Plot.update_video()

    @staticmethod
    def set_harm_offset(value):
        data.harm_offset = 1-value/100
        Plot.update_video()

    @staticmethod
    def set_tab_size(value):
        data.tab_size = value
        Plot.update_video()

    @staticmethod
    def set_tab_offset(value):
        data.tab_offset = 1-value/100
        Plot.update_video()

    @staticmethod
    def set_transparency(value):
        data.transparency = value/100
        Plot.update_video()

    @staticmethod
    def set_shade_top(value):
        data.shade_top = 1-value/100
        Plot.update_video()

    @staticmethod
    def set_shade_bottom(value):
        data.shade_bottom = 1-value/100
        Plot.update_video()

    @staticmethod
    def set_rotate(value):
        data.rotation = value
        Plot.update_video()

    def set_font(value):
        settings.tabs_font = value
        Plot.update_video()
    
    def set_fontH(value):
        settings.harm_font = value
        Plot.update_video()
            
class MyMainWindow(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        ui.graphicsView.quit()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet_pyqt5())
    MainWindow = MyMainWindow()
    MainWindow.setObjectName("MainWindow")
    MainWindow.setGeometry(0,0,1920,950)
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    if len(sys.argv)>1:
        ui.open_project(sys.argv[1])
    MainWindow.show()
    sys.exit(app.exec_())
