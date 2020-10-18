from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime
import simpleaudio as sa
import copy, pickle
from core import Synth, SynthGUI
from core.Simulator import Recorder, TextReader

SampleRate = 44100

class ButtonBox(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # Create Widgets
        self.Run = QtWidgets.QPushButton()

        # Set Properties
        self.Run.setText('Run')

        # Size Policy
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.Fixed)

        # Create layout
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.Run)

class Key(QtWidgets.QWidget):
    AddKey = QtCore.pyqtSignal(int)
    DelKey = QtCore.pyqtSignal(int)
    valueChanged = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        # Create Widgets
        self.FrequencyLabel = QtWidgets.QLabel()
        self.VolumeLabel = QtWidgets.QLabel()
        self.ShortcutLabel = QtWidgets.QLabel()
        self.Frequency = QtWidgets.QLineEdit()
        self.Volume = QtWidgets.QLineEdit()
        self.Shortcut = QtWidgets.QLineEdit()
        self.Add = QtWidgets.QPushButton()
        self.Del = QtWidgets.QPushButton()

        # Set Properties
        self.FrequencyLabel.setText('Frequency')
        self.VolumeLabel.setText('Volume')
        self.ShortcutLabel.setText('Shortcut')
        self.Add.setText('Add')
        self.Del.setText('Del')

        # Initial values
        self.index = 0
        self.Frequency.setText('440')
        self.Volume.setText('25')
        self.Shortcut.setText('a')
        self.Frequency.value = 440
        self.Volume.value = 25

        # Create events
        self.Frequency.editingFinished.connect(self.changeFrequency)
        self.Volume.editingFinished.connect(self.changeVolume)
        self.Shortcut.editingFinished.connect(self.changeShortcut)
        self.Add.clicked.connect(self.AddClicked)
        self.Del.clicked.connect(self.DelClicked)

        # Create Layout
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.FrequencyLabel,0,0,1,1)
        self.layout.addWidget(self.VolumeLabel,1,0,1,1)
        self.layout.addWidget(self.ShortcutLabel,2,0,1,1)
        self.layout.addWidget(self.Add,3,0,1,1)
        self.layout.addWidget(self.Frequency,0,1,1,1)
        self.layout.addWidget(self.Volume,1,1,1,1)
        self.layout.addWidget(self.Shortcut,2,1,1,1)
        self.layout.addWidget(self.Del,3,1,1,1)

        # Set Size Policy
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.Add.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.Del.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.Frequency.setSizePolicy(QtWidgets.QSizePolicy.Ignored,QtWidgets.QSizePolicy.Fixed)
        self.Volume.setSizePolicy(QtWidgets.QSizePolicy.Ignored,QtWidgets.QSizePolicy.Fixed)
        self.Shortcut.setSizePolicy(QtWidgets.QSizePolicy.Ignored,QtWidgets.QSizePolicy.Fixed)
        self.FrequencyLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored,QtWidgets.QSizePolicy.Fixed)
        self.VolumeLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored,QtWidgets.QSizePolicy.Fixed)
        self.ShortcutLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored,QtWidgets.QSizePolicy.Fixed)
    
    def changeFrequency(self):
        if self.Frequency.isModified():
            try:
                self.Frequency.value = float(self.Frequency.text())
                self.valueChanged.emit()
            except ValueError:
                self.Frequency.setText(str(self.Frequency.value))
            self.Frequency.setModified(False)

    def changeVolume(self):
        if self.Volume.isModified():
            try:
                self.Volume.value = float(self.Volume.text())
                self.valueChanged.emit()
            except ValueError:
                self.Volume.setText(str(self.Volume.value))
            self.Volume.setModified(False)

    def changeShortcut(self):
        if self.Shortcut.isModified():
            self.valueChanged.emit()
            self.Shortcut.setModified(False)

    def setSettings(self, Frequency, Volume, Shortcut):
        self.Frequency.value = float(Frequency)
        self.Frequency.setText(Frequency)
        self.Volume.value = float(Volume)
        self.Volume.setText(Volume)
        self.Shortcut.setText(Shortcut)
    
    def AddClicked(self):
        self.AddKey.emit(self.index)
        self.valueChanged.emit()

    def DelClicked(self):
        self.DelKey.emit(self.index)
        self.valueChanged.emit()

    def Play(self):
        PlayAudio(self.audio)

class KeyBoard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Create Widgets
        self.EmptySpace = QtWidgets.QWidget()
        self.Key_no = 1 # number of key in the keyboard
        self.Key = [Key()]

        # Create Layout
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.Key[0])
        self.layout.addWidget(self.EmptySpace)

        # Set Size Policy
        self.EmptySpace.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

class Instrument(QtWidgets.QWidget):
    AddInst = QtCore.pyqtSignal(int)
    DelInst = QtCore.pyqtSignal(int)
    MoveUp = QtCore.pyqtSignal(int)
    MoveDown = QtCore.pyqtSignal(int)
    valueChanged = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        # Default values
        self.Parameters = copy.deepcopy(SynthGUI.Parameters)
        self.Overtone_no = 1
        self.synth = SynthGUI.SoundEditorWindow()
        self.index = 0

        # Create Widgets
        self.Label = QtWidgets.QLineEdit()
        self.EditSynth = QtWidgets.QPushButton()
        self.Up = QtWidgets.QPushButton()
        self.Down = QtWidgets.QPushButton()
        self.KeyBoard = KeyBoard()
        self.Add = QtWidgets.QPushButton()
        self.Del = QtWidgets.QPushButton()
        self.Scroll = QtWidgets.QScrollArea()

        # Set Properties
        self.Label.setText('Name')
        self.EditSynth.setText('Edit Sound')
        self.Up.setText('Move Up')
        self.Down.setText('Move Down')
        self.Add.setText('Add')
        self.Del.setText('Delete')

        # Set scroll
        self.Scroll.setWidget(self.KeyBoard)
        self.Scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.Scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # Set Size Policy
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        self.Label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.Add.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.MinimumExpanding)
        self.Del.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.MinimumExpanding)
        self.Scroll.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        self.Scroll.setWidgetResizable(True)

        # Create events
        self.EditSynth.clicked.connect(self.editSynth)
        self.KeyBoard.Key[0].AddKey.connect(self.addKey)
        self.KeyBoard.Key[0].DelKey.connect(self.delKey)
        self.KeyBoard.Key[0].valueChanged.connect(self.SomethingChanged)
        self.Add.clicked.connect(self.AddInstClicked)
        self.Del.clicked.connect(self.DelInstClicked)
        self.Up.clicked.connect(self.MoveUpClicked)
        self.Down.clicked.connect(self.MoveDownClicked)
        self.synth.ButtonBox.Update.clicked.connect(self.SomethingChanged)

        # Create Layout
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.Label,0,0,1,1)
        self.layout.addWidget(self.EditSynth,1,0,1,1)
        self.layout.addWidget(self.Up,2,0,1,1)
        self.layout.addWidget(self.Down,3,0,1,1)
        self.layout.addWidget(self.Scroll,0,1,4,1)
        self.layout.addWidget(self.Add,0,2,2,1)
        self.layout.addWidget(self.Del,2,2,2,1)

    def editSynth(self):
        SynthGUI.Parameters = copy.deepcopy(self.Parameters)
        self.synth.setSettings(self.Overtone_no, 
                                    self.KeyBoard.Key[0].Frequency.value,
                                    self.KeyBoard.Key[0].Volume.value)
        self.synth.exec_()
        self.Parameters = copy.deepcopy(SynthGUI.Parameters)
        self.Overtone_no = self.synth.EQ.Overtone_no

    def addKey(self, index):
        index += 1
        self.KeyBoard.Key_no += 1
        self.KeyBoard.Key.insert((index), Key())
        self.KeyBoard.layout.insertWidget(index,self.KeyBoard.Key[index])
        self.KeyBoard.Key[index].AddKey.connect(self.addKey)
        self.KeyBoard.Key[index].DelKey.connect(self.delKey)
        self.KeyBoard.Key[index].valueChanged.connect(self.SomethingChanged)
        self.KeyBoard.Key[index].index = index - 1
        for x in self.KeyBoard.Key[index:]:
            x.index += 1

    def delKey(self, index):
        if self.KeyBoard.Key_no > 1:
            self.KeyBoard.Key_no -= 1
            self.KeyBoard.layout.removeWidget(self.KeyBoard.Key[index])
            self.KeyBoard.Key[index].setParent(None)
            self.KeyBoard.Key.pop(index)
            for x in self.KeyBoard.Key[index:]:
                x.index -= 1

    def SomethingChanged(self):
        self.valueChanged.emit()

    def AddInstClicked(self):
        self.AddInst.emit(self.index) 

    def DelInstClicked(self):
        self.DelInst.emit(self.index)

    def MoveUpClicked(self):
        self.MoveUp.emit(self.index)

    def MoveDownClicked(self):
        self.MoveDown.emit(self.index)

class Ensemble(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        # Create Widgets
        self.Inst_no = 1 # number of instrument in the ensemble
        self.Instrument = [Instrument()]

        # Size Policy
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.Fixed)

        # Create Layout
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.Instrument[0])

        # Create Events
        self.Instrument[0].AddInst.connect(self.AddInst)
        self.Instrument[0].DelInst.connect(self.DelInst)
        self.Instrument[0].MoveUp.connect(self.MoveUp)
        self.Instrument[0].MoveDown.connect(self.MoveDown)
        self.Instrument[0].valueChanged.connect(self.SomethingChanged)

    def AddInst(self, index):
        index += 1
        self.Inst_no += 1
        self.Instrument.insert((index), Instrument())
        self.layout.insertWidget(index,self.Instrument[index])
        self.Instrument[index].AddInst.connect(self.AddInst)
        self.Instrument[index].DelInst.connect(self.DelInst)
        self.Instrument[index].MoveUp.connect(self.MoveUp)
        self.Instrument[index].MoveDown.connect(self.MoveDown)
        self.Instrument[index].index = index - 1
        self.Instrument[index].valueChanged.connect(self.valueChanged)
        for x in self.Instrument[index:]:
            x.index += 1
        self.valueChanged.emit()

    def DelInst(self, index):
        if self.Inst_no > 1:
            self.Inst_no -= 1
            self.layout.removeWidget(self.Instrument[index])
            self.Instrument[index].setParent(None)
            self.Instrument.pop(index)
            for x in self.Instrument[index:]:
                x.index -= 1
            self.valueChanged.emit()

    def MoveUp(self, index):
        if index > 0:
            self.Instrument[index].index -= 1
            self.Instrument[index-1].index += 1
            self.layout.removeWidget(self.Instrument[index])
            self.layout.insertWidget(index-1,self.Instrument[index])
            self.Instrument[index], self.Instrument[index-1] = self.Instrument[index-1], self.Instrument[index]
            self.valueChanged.emit()

    def MoveDown(self, index):
        if index < (self.Inst_no - 1):
            self.Instrument[index].index += 1
            self.Instrument[index+1].index -= 1
            self.layout.removeWidget(self.Instrument[index])
            self.layout.insertWidget(index+1, self.Instrument[index])
            self.Instrument[index], self.Instrument[index+1] = self.Instrument[index+1], self.Instrument[index]
            self.valueChanged.emit()

    def SomethingChanged(self):
        self.valueChanged.emit()

class HelpAbout(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.Text = QtWidgets.QLabel()
        self.Button = QtWidgets.QPushButton()
        self.Text.setWordWrap = True
        self.Text.setText('Kirama Gamelan Simulator v0.1\nUpdated 17 Oct 2020\n\nby Fauzie Wiriadisastra\n\nReleased Under\nGeneral Public License')
        self.Text.setAlignment(QtCore.Qt.AlignCenter)
        self.Button.setText('Ok')

        self.Button.clicked.connect(self.close)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.Text)
        self.layout.addWidget(self.Button)

        self.exec_()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('pyGamelan - New')

        # Create Widgets
        self.MainWidget = QtWidgets.QWidget()
        self.Ensemble = Ensemble()
        self.Button = ButtonBox()
        self.Scroll = QtWidgets.QScrollArea()

        # Set scroll
        self.Scroll.setWidget(self.Ensemble)
        self.Scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.Scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.Scroll.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.Scroll.setWidgetResizable(True)

        # Menu actions
        newAction = QtWidgets.QAction('&New', self)
        openAction = QtWidgets.QAction('&Open', self)
        saveAction = QtWidgets.QAction('&Save', self)
        exitAction = QtWidgets.QAction('E&xit',self)
        runSimulator = QtWidgets.QAction('&Run Simulator', self)
        runReadText = QtWidgets.QAction('Read &Text', self)
        helpContents = QtWidgets.QAction('&Contents', self)
        helpAbout = QtWidgets.QAction('&About', self)

        # Action triggers
        newAction.triggered.connect(self.NewFile)
        openAction.triggered.connect(self.LoadFile)
        saveAction.triggered.connect(self.SaveFile)
        exitAction.triggered.connect(self.ExitProgram)
        runSimulator.triggered.connect(self.RunSimulator)
        runReadText.triggered.connect(self.ReadText)
        helpContents.triggered.connect(self.Contents)
        helpAbout.triggered.connect(self.About)

        # Create Menu Bar
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)
        runMenu = menuBar.addMenu('&Run')
        runMenu.addAction(runSimulator)
        runMenu.addAction(runReadText)
        helpMenu = menuBar.addMenu('&Help')
        helpMenu.addAction(helpContents)
        helpMenu.addAction(helpAbout)

        # Create Events
        self.Button.Run.clicked.connect(self.RunSimulator)
        self.Ensemble.valueChanged.connect(self.SomethingChanged)

        # Create Layout
        self.MainWidget.layout = QtWidgets.QVBoxLayout()
        self.MainWidget.setLayout(self.MainWidget.layout)
        self.MainWidget.layout.addWidget(self.Button)
        self.MainWidget.layout.addWidget(self.Scroll)
        self.setCentralWidget(self.MainWidget)

        # Size Policy
        
        # Fill audio
        self.Update()

        # Show window
        self.showMaximized()

    def SomethingChanged(self):
        self.isModified = True

    def RunSimulator(self):
        if self.isModified == True:
            self.Update()
        self.RunWindow = Recorder(self.Ensemble)
        self.RunWindow.exec_()
        del self.RunWindow

    def ReadText(self):
        if self.isModified == True:
            self.Update()
        self.RunWindow = TextReader(self.Ensemble)
        self.RunWindow.exec_()
        del self.RunWindow

    def Update(self):
        for i in self.Ensemble.Instrument:
            # Prepare synthesizer
            Synthesizer = i.synth.synth
            Synthesizer.setSettings(i.Overtone_no, i.KeyBoard.Key[0].Frequency.value,
                                    i.KeyBoard.Key[0].Volume.value, i.Parameters)

            # iterate through keys
            for j in i.KeyBoard.Key:
                Synthesizer.Fundamental = j.Frequency.value
                Synthesizer.Volume = j.Volume.value
                Synthesizer.GetWaveform()
                j.audio = Synthesizer.audio
        self.isModified = False

    def Reset(self):
        i = self.Ensemble.Inst_no
        while i > 0:
            self.Ensemble.layout.removeWidget(self.Ensemble.Instrument[-1])
            self.Ensemble.Instrument[-1].setParent(None)
            del self.Ensemble.Instrument[-1]
            i -= 1
        self.Ensemble.Inst_no = 0

    def NewFile(self):
        self.Reset()
        self.Ensemble.AddInst(-1)
        self.setWindowTitle('pyGamelan - New')

    def SaveFile(self):
        FileName, _  = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Ensemble File', 'data/gamelan', '*.gml')
        if FileName:
            f = open(FileName,'wb')
            DataToSave = [self.Ensemble.Inst_no]
            for i in self.Ensemble.Instrument:
                InstData = [i.Label.text(), i.KeyBoard.Key_no, i.Overtone_no, i.Parameters]
                for j in i.KeyBoard.Key:
                    InstData.append([j.Frequency.text(), j.Volume.text(), j.Shortcut.text()])
                DataToSave.append(InstData)

            pickle.dump(DataToSave, f)
            f.close()

    def LoadFile(self):
        FileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Ensemble File', 'data/gamelan/', '*.gml')
        if FileName:
            # Read file
            self.setWindowTitle('pyGamelan - '+ FileName)
            f = open(FileName,'rb')
            LoadedData = pickle.load(f)
            f.close()

            # Reset Ensemble
            self.Reset()
            
            # Build Ensemble
            i = 0
            while i < LoadedData[0]:
                # Create Instrument
                self.Ensemble.AddInst(i-1)
                
                # Instrument Settings
                editedInst = self.Ensemble.Instrument[i]
                k = i+1
                editedInst.Label.setText(LoadedData[k][0])
                editedInst.Overtone_no = LoadedData[k][2]
                editedInst.Parameters = LoadedData[k][3]

                # Build KeyBoard
                j = 1
                editedInst.KeyBoard.Key[0].setSettings(LoadedData[k][4][0], LoadedData[k][4][1], LoadedData[k][4][2])
                while j < LoadedData[k][1]:
                    editedInst.addKey(j-1)
                    l = j+4
                    editedInst.KeyBoard.Key[j].setSettings(LoadedData[k][l][0], LoadedData[k][l][1], LoadedData[k][l][2])
                    j += 1

                i += 1

    def ExitProgram(self):
        self.close()
        exit()

    def Contents(self):
        pass

    def About(self):
        RunWindow = HelpAbout()

def PlayAudio(audio16bit):
    play_obj = sa.play_buffer(audio16bit, 1, 2, SampleRate)

def main():
    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()

if __name__ == '__main__':
    main()
