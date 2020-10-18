import numpy as np
import simpleaudio as sa

def GetEnvelope(A,D,S,R,Peak_A, Sustain_A,Time):
    envelope = Time.copy()
    i = 0
    
    for t in Time:
        if t<A:
            envelope[i] = (Peak_A/A)*t
        elif t<(A+D):
            envelope[i] = Peak_A - ((Peak_A - Sustain_A)/D)*(t-A)
        elif t<(A+D+S):
            envelope[i] = Sustain_A
        elif t<(A+D+S+R):
            envelope[i] = Sustain_A - (Sustain_A/R)*(t-(A+D+S))
        else:
            envelope[i] = 0
        i += 1

    return envelope

class Synth():
    def __init__(self):
        
        # Default values
        self.samplerate = 44100
        self.Fundamental = 440.0
        self.Overtone_no = 1
        self.Peak_A = [100.0]
        self.Sustain_A = [50.0]
        self.Attack = [0.1]
        self.Decay = [0.1]
        self.Sustain = [1.0]
        self.Release = [0.1]
        self.FreqRatio = [100]
        self.Phase = [0]
        self.Volume = 25.0
        
        # Generate empty arrays
        self.Reset()

        # Generate default waveform
        self.GetWaveform()

    def Reset(self):
        self.duration = np.max(np.add(np.add(np.add(self.Attack,self.Decay),self.Sustain),self.Release))
        self.Time = np.linspace(0, self.duration, int(self.duration*self.samplerate), False)
        self.harm = np.zeros(len(self.Time))
        self.env = self.harm.copy()
        self.env_harm = self.harm.copy()
        self.audio = self.harm.copy()
        self.audiograph = self.harm.copy()

    def GetOvertones(self):
        self.Frequency = np.zeros(self.Overtone_no)
        i = 0
        while i<self.Overtone_no:
            self.Frequency[i] = self.Fundamental*(self.FreqRatio[i]/self.FreqRatio[0])
            i += 1

    def addOvertones(self):
        self.Peak_A.append(100.0)
        self.Sustain_A.append(50.0)
        self.Attack.append(0.1)
        self.Decay.append(0.1)
        self.Sustain.append(1.0)
        self.Release.append(0.1)
        self.Phase.append(0)
        self.Overtone_no += 1
        self.FreqRatio.append(100*self.Overtone_no)

    def delOvertones(self):
        del self.Peak_A[-1]
        del self.Sustain_A[-1]
        del self.Attack[-1]
        del self.Decay[-1]
        del self.Sustain[-1]
        del self.Release[-1]
        del self.FreqRatio[-1]
        self.Overtone_no -= 1

    def GetWaveform(self):
        i = 0
        self.note = np.zeros(len(self.Time))  #reset note
        self.GetOvertones() #find frequencies

        # Generate waveform and envelope
        while i < self.Overtone_no:
            self.harm = np.sin(self.Frequency[i]*self.Time*2*np.pi)
            self.env = GetEnvelope(self.Attack[i],self.Decay[i],self.Sustain[i],self.Release[i],
                    self.Peak_A[i],self.Sustain_A[i],self.Time) 
            self.env_harm = np.multiply(self.env, self.harm)
            self.note = np.add(self.note,self.env_harm)
            i += 1

        # Ensure that the highest value is in 16-bit range, use this for ploting
        self.audiograph = (self.Volume/100) * self.note * (2**15 - 1) / np.max(np.abs(self.note))

        #Convert to 16-bit data, use this for playing
        self.audio = self.audiograph.astype(np.int16)

    def Play(self):
        self.play_obj = sa.play_buffer(self.audio, 1, 2, self.samplerate)

    def Wait(self):
        self.play_obj.wait_done()

    def setSettings(self, Overtone_no, Fundamental, Volume, Parameters):
        # Parameters is a dictionary with a format
        # {'Peak Amplitude':[minval, maxval, value1, value2, value3, ...],'Sustain Amplitude': ...
        # the minval and maxval values are used for GUI and may be filled with arbitrary values if there is no GUI

        # reset synth parameters
        self.Peak_A = [] 
        self.Sustain_A = []
        self.Attack = []
        self.Decay = []
        self.Sustain = []
        self.Release = []
        self.FreqRatio = []
        self.Phase = []

        # Set basic properties
        self.Overtone_no = Overtone_no
        self.Fundamental = Fundamental
        self.Volume = Volume

        # Set overtone wave parameters
        i = 0
        j = 2
        while i < self.Overtone_no:
            self.Peak_A.append(Parameters['Peak Amplitude'][j])
            self.Sustain_A.append(Parameters['Sustain Amplitude'][j])
            self.Attack.append(Parameters['Attack Time'][j])
            self.Decay.append(Parameters['Decay Time'][j])
            self.Sustain.append(Parameters['Sustain Time'][j])
            self.Release.append(Parameters['Release Time'][j])
            self.FreqRatio.append(Parameters['Frequency Ratio'][j])
            self.Phase.append(Parameters['Phase'][j])
            i += 1
            j += 1

        # Create a new waveform
        self.Reset()
        self.GetWaveform()

    def setFundamental(self,Freq):
        self.Fundamental = Freq
        self.GetWaveform()

    def setVolume(self,vol):
        self.Volume = vol
        self.GetWaveform()

if __name__ == "__main__":
    import sys
    import pyqtgraph as pg
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        Sine = Synth()
        pg.plot(Sine.audiograph)
        Sine.Play()

        pg.QtGui.QApplication.exec_()
        Sine.Wait()
