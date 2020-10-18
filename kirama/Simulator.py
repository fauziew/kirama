from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime
from scipy.io.wavfile import write
import simpleaudio as sa
import Synth 
import pickle
import numpy as np
import pyqtgraph as pg

SampleRate = 44100

class KeyLabel(QtWidgets.QWidget):
    # Container for RunWindow keys
    def __init__(self):
        super().__init__()

        self.Freq = QtWidgets.QLabel()
        self.Shortcut = QtWidgets.QLabel()

        self.Freq.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.Shortcut.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.Freq)
        self.layout.addWidget(self.Shortcut)

class InstrumentLabel(QtWidgets.QWidget):
    # Container for RunWindow instruments
    def __init__(self):
        super().__init__()

        self.Key = [KeyLabel()]
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.Key[0])

class Simulator(QtWidgets.QDialog):
    def __init__(self, Ensemble):
        super().__init__()
        self.setWindowTitle('Live')
        self.Ensemble = Ensemble

        # Prepare Layout
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.ButtonBox = QtWidgets.QWidget()
        self.layout.addWidget(self.ButtonBox)
        self.ButtonBox.layout = QtWidgets.QHBoxLayout()
        self.ButtonBox.setLayout(self.ButtonBox.layout)

        # Create variables
        self.Instrument = [InstrumentLabel()]
        self.KeyDict = {}

        # Create Info
        i = 0
        while i < Ensemble.Inst_no:
            j = 0
            while j < Ensemble.Instrument[i].KeyBoard.Key_no:
                self.Instrument[i].Key[j].Freq.setText(Ensemble.Instrument[i].KeyBoard.Key[j].Frequency.text())
                Text = Ensemble.Instrument[i].KeyBoard.Key[j].Shortcut.text()
                if Text == '\\n': Text = '\n'
                if Text == '\\x0c': Text = '\x0c'
                if Text == '\\ufeff': Text = '\ufeff'
                self.Instrument[i].Key[j].Shortcut.setText(Text)
                self.Instrument[i].Key.append(KeyLabel())
                self.Instrument[i].Key[j].trigger = QtWidgets.QShortcut(Text,self)
                self.Instrument[i].Key[j].trigger.activated.connect(Ensemble.Instrument[i].KeyBoard.Key[j].Play)
                self.KeyDict[Text] = Ensemble.Instrument[i].KeyBoard.Key[j].audio
                j += 1
                self.Instrument[i].layout.addWidget(self.Instrument[i].Key[j])
            self.Instrument.append(InstrumentLabel())
            self.layout.addWidget(self.Instrument[i])
            i += 1

        # Create Exit Button
        self.Stop = QtWidgets.QPushButton()
        self.Stop.setText('Stop')
        self.Stop.clicked.connect(self.close)
        self.ButtonBox = QtWidgets.QWidget()
        self.layout.addWidget(self.ButtonBox)
        self.ButtonBox.layout = QtWidgets.QHBoxLayout()
        self.ButtonBox.setLayout(self.ButtonBox.layout)

class Recorder(Simulator):
    def __init__(self, Ensemble):
        super().__init__(Ensemble)
        self.setWindowTitle('Gamelan Simulator')

        # Create Widgets
        self.RecordButton = QtWidgets.QPushButton()
        self.Play = QtWidgets.QPushButton()
        self.Clear = QtWidgets.QPushButton()
        self.SaveKey = QtWidgets.QPushButton()
        self.LoadKey = QtWidgets.QPushButton()
        self.SaveAudio = QtWidgets.QPushButton()
        self.graph = pg.PlotWidget()
        self.curve = self.graph.plot()

        self.RecordButton.setText('Record')
        self.Play.setText('Play')
        self.Clear.setText('Clear')
        self.SaveKey.setText('Save')
        self.LoadKey.setText('Load')
        self.SaveAudio.setText('Export')
        self.Stop.setText('Exit')

        # Initial Values
        self.Reset()

        # Create events
        self.RecordButton.clicked.connect(self.Record)
        self.Play.clicked.connect(self.PlayRecording)
        self.Clear.clicked.connect(self.Reset)
        self.SaveKey.clicked.connect(self.SaveKeyStroke)
        self.LoadKey.clicked.connect(self.LoadKeyStroke)
        self.SaveAudio.clicked.connect(self.ExportWav)

        # Create Layout
        self.ButtonBox.layout.addWidget(self.RecordButton)
        self.ButtonBox.layout.addWidget(self.Play)
        self.ButtonBox.layout.addWidget(self.Clear)
        self.ButtonBox.layout.addWidget(self.SaveKey)
        self.ButtonBox.layout.addWidget(self.LoadKey)
        self.ButtonBox.layout.addWidget(self.SaveAudio)
        self.ButtonBox.layout.addWidget(self.Stop)
        self.layout.addWidget(self.graph)

    def Reset(self):
        self.KeyStrokeHistory = []
        self.audio = []
        self.Time = []
        self.curve.setData(self.Time, self.audio)

    def Record(self):
        # Change button to Stop Record
        self.RecordButton.setText('Stop Record')
        self.RecordButton.clicked.disconnect(self.Record)
        self.RecordButton.clicked.connect(self.StopRecord)

        # Activate triggers to record KeyStroke
        i = 0
        while i < self.Ensemble.Inst_no:
            j = 0
            while j < self.Ensemble.Instrument[i].KeyBoard.Key_no:
                Text = self.Instrument[i].Key[j].Shortcut.text()
                self.Instrument[i].Key[j].RecordFunc = lambda x=Text: self.RecordKeyStroke(x)
                self.Instrument[i].Key[j].trigger.activated.connect(self.Instrument[i].Key[j].RecordFunc)
                j += 1
            i += 1

        # Record initial recording time
        self.ti = datetime.timestamp(datetime.now())

    def RecordKeyStroke(self, KeyStroke):
        self.KeyStrokeHistory.append([(datetime.timestamp(datetime.now())-self.ti), KeyStroke])

    def StopRecord(self):
        # Change button to Start Record
        self.RecordButton.setText('Start Record')
        self.RecordButton.clicked.disconnect(self.StopRecord)
        self.RecordButton.clicked.connect(self.Record)

        # Disconnect trigger mechanisms
        i = 0
        while i < self.Ensemble.Inst_no:
            j = 0
            while j < self.Ensemble.Instrument[i].KeyBoard.Key_no:
                self.Instrument[i].Key[j].trigger.activated.disconnect()
                self.Instrument[i].Key[j].trigger.activated.connect(self.Ensemble.Instrument[i].KeyBoard.Key[j].Play)
                j += 1
            i += 1
        self.UpdateAudio()

    def UpdateAudio(self):
        del self.audio, self.Time
        self.audio, self.Time = Key2Audio(self.KeyStrokeHistory, self.KeyDict)
        self.curve.setData(self.Time, self.audio)
        self.graph.setXRange(0, self.Time[-1])
        self.graph.setYRange(-32768,32767)

    def PlayRecording(self):
        PlayAudio(self.audio)

    def SaveKeyStroke(self):
        FileName, _  = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', 'Data/record/', '*.rec')
        if FileName:
            f = open(FileName,'wb')
            pickle.dump(self.KeyStrokeHistory,f)
            f.close()

    def LoadKeyStroke(self):
        FileName, _ = FileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', 'Data/record/', '*.rec')
        if FileName:
            f = open(FileName,'rb')
            self.KeyStrokeHistory = pickle.load(f)
            f.close()
            self.UpdateAudio()

    def ExportWav(self):
        ExportWav(self.audio)

class TextReader(Simulator):
    def __init__(self, Ensemble):
        super().__init__(Ensemble)

        self.setWindowTitle('Text Reader')

        # Create widgets
        self.Warning_ = QtWidgets.QLabel()
        self.TempoLabel = QtWidgets.QLabel()
        self.TempoEdit = QtWidgets.QLineEdit()
        self.Load = QtWidgets.QPushButton()
        self.Generate = QtWidgets.QPushButton()
        self.Play = QtWidgets.QPushButton()
        self.Export = QtWidgets.QPushButton()

        self.Tempo = 100
        self.crotchet = 60/self.Tempo # Time for each crotchet
        self.quaver = 30/self.Tempo # Time for each quaver
        self.TempoEdit.setText(str(self.Tempo))
        self.Warning_.setText('WARNING: Text Reader is a highly experimental feature. It may not work or even crash')
        self.TempoLabel.setText('Tempo (bpm)')
        self.Load.setText('Load Textfile')
        self.Generate.setText('Generate')
        self.Play.setText('Play')
        self.Export.setText('Export')
        self.Text =''
        self.audio = []
        self.KeyStroke = []

        # Create events
        self.TempoEdit.editingFinished.connect(self.TempoChanged)
        self.Load.clicked.connect(self.LoadTextFile)
        self.Generate.clicked.connect(self.GenerateMusic)
        self.Play.clicked.connect(self.PlayMusic)
        self.Export.clicked.connect(self.ExportWav)

        self.layout.insertWidget(0,self.Warning_)
        self.ButtonBox.layout.addWidget(self.TempoLabel)
        self.ButtonBox.layout.addWidget(self.TempoEdit)
        self.ButtonBox.layout.addWidget(self.Load)
        self.ButtonBox.layout.addWidget(self.Generate)
        self.ButtonBox.layout.addWidget(self.Play)
        self.ButtonBox.layout.addWidget(self.Export)
        self.ButtonBox.layout.addWidget(self.Stop)

    def TempoChanged(self):
        try:
            self.Tempo = float(self.TempoEdit.text())
            self.crotchet = 60/self.Tempo
            self.quaver = 30 / self.Tempo
        except ValueError:
            self.TempoEdit.setText(str(self.Tempo))

    def GenerateMusic(self):
        TotalLength = len(self.Text)
        i = 0
        BeatTime = 0 # Start of word
        while i < TotalLength:
            # Detect word
            space = min( self.Text.find(' ',i), self.Text.find('\n',i) )
            if space:
                word = self.Text[i:space]
            else:
                word = self.Text[i:] # EOF

            WordLength = len(word)
            if WordLength:   # If there is a word, not just space
                Arpegio = self.quaver/WordLength # time between arpegiated keystrokes
                PunchTime = BeatTime # Start of letter
                for letter in word:
                    # Assign time to each letter
                    self.KeyStroke.append([PunchTime, letter])
                    PunchTime += Arpegio
            i += WordLength + 1
            BeatTime += self.crotchet
        self.audio, self.Time = Key2Audio(self.KeyStroke, self.KeyDict)

    def PlayMusic(self):
        PlayAudio(self.audio)

    def LoadTextFile(self):
        FileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', 'Data/text/', '*.txt')
        if FileName:
            f = open(FileName,'r')
            self.Text = f.read()
            f.close()

    def ExportWav(self):
        ExportWav(self.audio)

def ExportWav(audio):
    FileName, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Export As Wave', 'Data/wav/', '*.wav')
    if FileName:
        write(FileName, SampleRate, audio)

def Key2Audio(KeyStroke, KeyDict):
    # Make sure KeyStroke history is not empty
    if KeyStroke == []:
        audio = [0]
        Time = [0]
    else:
        # Calculate total time needed and prepare audio variable
        LastNoteDuration = len(KeyDict[KeyStroke[-1][1]])/SampleRate
        TotalDuration = KeyStroke[-1][0] + LastNoteDuration + 30 
        TotalKeyStroke = len(KeyStroke)
        WorkDone = 0
        Time = np.linspace(0, TotalDuration, TotalDuration*SampleRate, False)
        audio = np.zeros(len(Time))

        # Put the waveforms for each keystroke
        for x in KeyStroke:
            i = int(x[0]*SampleRate)
            for y in KeyDict[x[1]]:
                audio[i] += y
                i += 1
            WorkDone += 1
            if WorkDone % 1000 == 0:
                print((WorkDone / TotalKeyStroke)*100)

    audio16 = audio.astype(np.int16)
    return audio16, Time

def PlayAudio(audio16bit):
    play_obj = sa.play_buffer(audio16bit, 1, 2, SampleRate)

