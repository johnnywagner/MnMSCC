'''
This program creates single-cycle waveforms for just intonation chords
for the Elektron Monomachine (MnM) MK2 models based on Luciano Notarfrancesco's original code.
The intended usage is to set your parameters in the drag prepared files this program outputs into Elektron's C6 sysex software
to conver them into "DigiPro" formatted sysex files to then send them to the Monomachine.

Original Code by:
2020/4/18, Luciano Notarfrancesco, github.com/len

Monomachine Adaptation & Additional Signal types
2024/2/28 , JW github.com/

A useful Just Intonation webapp for use in tandem with this program:
https://justintonate.com

Single Cycle Waveform Editor:
http://scw.sheetsofsound.com/editor.html

'''
from math import pi, sin, cos, asin, sqrt, ceil
import wave
import struct
import os
import shutil
import random

# only needed for signal design and debugging
from scipy.io.wavfile import read
import matplotlib.pyplot as plt

###################################
# Global Variables/Constants
###################################
digiProNum = 0
baseEpoch = 315532800
epochInc = 31536000
spacer = '\n█████████████████████████████████████████████████████████████████████████████████████████████████████████\n'
addendumPath = 'userFiles'
uniPath = 'unison waves'

##########################################
# Generation Controls & Chord Defintions
##########################################
F0 = 261.625565 # C4= 261.6255653005986  or 261.625565
SAMPLE_RATE = 10005.0 # 10005 is known good, idk why. common sample rates you may use for other use cases besides the MnM: 22050,24000,44100,48000

#Inversion Parameters
normalizeChords = 1
genInversions = 0
smartInvert = 1
genCustomInversions = 1
genUp1Octave = 0 # will generate an additional chord that is the root position raised 1 octave

#turn this on to generate matplotlib graphs of the waves generated. Useful for debugging new waveform types
printGraphsFlag = 0


oscList = [
'osc_sine',
#'osc_tri',
#'osc_saw',
#'osc_saw1',
#'osc_saw2',
#'osc_sqr',
#'osc_sqr2',
#'osc_fm1',
#'osc_fm2',
#'osc_chor', choir
#'osc_voic', #voice @11025
#'osc_flut', #flute
#'osc_whis', #whistle
#'osc_tsp', #idk
#'osc_tuba', #tuba
#'osc_trum', #trumpet
#'osc_soft',
#'osc_pad',
#'osc_tst1',
#'osc_tst2',
#'osc_bzzy',
#'osc_bzz2',
#'osc_dist',
#'osc_rnd',
#'osc_clp',
]

#['chord name', [the just intonic ratios of the chord],[inversions you want to generate. Ex. generate 1st and 3rd inversions: "[1,3]" ]
chords = [
#major chords
['maj', [4,5,6],             [2,]],                   # major
['mj7', [8,10,12,15],        [2,3]],              # major7
['mj9', [8,10,12,15,18],        [2,3]],              # major9
['mj11', [8,10,12,15,18,23],        [2,3]],              # major7
['m79', [4,5,6,9],           [2,]],                 # maj add 9
['mjo', [4,5,6,10,12],       []],              #major open C4, E4, G4, E5, G5
['mor', [4,5,6,8,12],  [3,4]],           # C4,E4,G4,C5,D5,G5,D6
['mjq', [4,5,6,8,12,15],  [3,4]],           # C4,E4,G4,C5,D5,G5,D6
['jor', [4,5,6,8,9,12,18],  [3,4]],           # C4,E4,G4,C5,D5,G5,D6
['j06', [4,5,6,8,9,12,16,18],  [3,4]],           # C4,E4,G4,C5,D5,G5,D6
['m+9', [4,5,6,18],          [2,]],                # maj add 9 but the 9 is up an octave
['7#11', [8,10,12,15,23],[]],              #Cmaj7#11 C4,E4,G4,B4,F#5
['6  ',[12,15,18,20], [3] ],                #C6 C,E,G,A     third inversion is F/D

#minor chords
['emin', [10,12,15], [] ],               # C minor chord
# ['bmin',  [15,18,23], [] ],
# ['cmin',  [16,19,24], [] ],
# ['gmin', [6,7,9], []],
['mn7', [10,12,15,18],       [2,3]],               # C minor chord
['mn+7',[10,12,15,19], [] ],
['mn9',[10,12,15,18,23],[]],
['mn11',[10,12,15,18,23,27],[]],               # true C minor 11
['m11', [10,12,15,18,27],    [2,3]],          # C minor 7 add f octave C,Eb,G,Bb,f
['m7e', [10,12,15,18,24],    []],          # C minor 7 C,Eb,G,Bb,Eb
['m7+', [10,12,15,18,30],    [2,3]],          # C minor 7 add g up octave C,Eb,G,Bb,G
['mno', [10,12,15,24,30],[]],                 # C4, Eb4, G4, Eb5, G5 # minor open
['n73', [12,16,19,24,30],[]],           # G3 bass on a minor add 7 (G3, C4, Eb4, G4, B4)
['7++', [10,12,15,18,24,30], []],     # C minor 7 add eb & g octave. C,Eb,G,Bb,Eb,G
['b79', [12,16,19,24,29,36],[]],        # G bass + Minor 7 add 9
['7b5', [5,6,7,9],           [2,]],     # Cmin7b5 half-diminished (perfect). Used in Black Cow by Steely Dan
['un6',[12,15,20,29], [] ],              # C4,E4,A4,Eb5
['nj9', [8,9,16,19,24,36],[]],          # Cm(maj9)
#['un6', [10,12,15,25,34],[]],           # C3, Eb3, G3, E4, A5
['n+7', [10,12,15,19],[]],              # C min add 7 chord aka minor(major7)
['n4 ', [10,12,15,27],[]],              # C minor triad add 4 but the 4 is up 1 octave
#['un5', [10,12,15,25],[2,]],              # C3,Eb3, G3, E4

#sus2 chords
['su2', [8,9,12],[2]],                  # sus2
['7s2', [8,9,12,14],[]],               # C7sus2 C,D,G,Bb
['s2#', [8,9,12,16,18],[]],            # C4,D4,G4,C5,D5
['s2!', [4,5,6,8,9],[]],                 # csus 2 +c octave + inverted d
['s2%', [3,4,5,6,8,9],[]],                 # csus 2 +c octave + inverted d
['6s2', [16,18,24,27],[]],             # C6sus2 CDGA
['s2@', [12,16,18,24,27],[]],          # idk G3,C4,D4,G4,A4

#sus4 chords 
['su4', [6,8,9],[2]],                   # sus4
['7s4i',[15,18,20,27],[]],            # C7sus4/G aka C7sus4 inverted on G
['7s41',[15,18,20,27,30],[]],            # C7sus4/G aka C7sus4 inverted on G
['7s42',[15,18,20,27,34],[]],            # C7sus4/G aka C7sus4 inverted on G
#['7s4', [12,16,18,21],[]],             # C7sus4
#['7s4', [12,16,18,23,27],[]],             # C7sus4
#['un2',  [4,5,6,8,9],[]],             # C4,E4,G4,C5,D5
['un4', [12,15,18,24,27,32], [3,4]],   # C4,E4,G4,C5,D5,F5 this sounds more sus than major
['s4!', [6,9,12,16,18],[]],            # Nice open sus 4 chord  C4,G4,C5,F5,G5
['s4@', [6,8,9,12,16,24],[]],          # C4,F4,G4,C5,F5,C6
['s4#', [12,16,18,23],[]],             # C maj 7th suspended 4th
['s49', [12,16,18,23,27],[]],          # C maj 7th suspended 4th add 9
['9s4',[12,18,21,27,32],[]],           # C9sus4 open voicing C4,G4,Bb4,D5,F5

#diminished chords
['dim', [5,6,7],[]],                   # perfect diminished
['di7', [10,12,14,17],[]],             # Francois-Joseph Fetis dim (17-limit tuning)(idk what this is) B3+D4+F4+Ab4
['i7!', [10,12,14,17,20],[]],          # Francois-Joseph Fetis dim (17-limit tuning) B3+D4+F4+Ab4+B5

#Augmented chords
['aug',[16,20,25],[]],                #C,E,G#
['au7',[16,20,25,28],[]],             #C,E,G#,Bb
['au9',[16,20,25,28,36],[]],          #C,E,G#,Bb,

#Number/other Chords
['5+6', [6,9,10], [] ],               #C5 add 6 C,G,A
['7  ', [4,5,6,7], [2] ],              # C7 (harmonic 7)
['9  ', [4,5,6,7,9], [2] ],            # C9 (harmonic 9)
['4¥5',[6,9,10,12,16],[]],            #F/G with a C bass note
#['9 2',  [8,9,10,12,14], [] ],
['9+o', [4,5,6,7,9,12], [] ],         # C9 (harmonic 9) + G
['blz', [15,18,20,27],[2]],                # ? C + Eb + F looks like F harmonic dyad (power chord) add b7 inverted on C
['hmm', [12,16,17,18],[1,2,3]],             # originally listed as "dream" chord

# Weirdness below, try experimenting with non integer ratios for horizontally clipping chords
#['imp',[1.333333,4.4653563465,6.92929292929]],

#the below chords ratios are too big to work well with the mnm, I found to be uninteresting sounding, or not useful in the context of the mnm
#['do7', [20,25,30,36]],              # ?dominant7
#['7b5', [25,30,36,45]],              # ?dom7b5
#['7#9', [20,25,30,36,48]],           # ?dom7#9 aka hendrix chord
#['mm7', [40,48,60,75]],              # ?minmaj7
#['smj', [1,3,5]],                    # open Major C4 E5 G6
#['di2', [20,24,29]],                 # diminished
##['dim',[20,24,29]],                # true diminished?
#['nt4', [30,36,40,45],[]],           # C minor triad add 4
#['n72', [8,12,14,18,23],[]],         # F3 bass on a minor add 7 (F3, C4, Eb4, G4, B4)
#['mn9', [20,24,30,36,45],  [2,3]],   # minor 9th [20,24,30,36,45]]
#['n79', [20,24,30,36,45]],           # min 7 add 9  

# Unison notes. You can generate any combination desired. 1=C4,2=C5,4=C6,
['uni', [1], [] ],
#['Bb', [7], [] ],     
['uni2', [1,16], [] ],       
#['uni3', [1,4,16], [] ],  

]

#chords = [
#['uniz', [1], [2,]],                   # major
#['uni2', [1,16], []],                   # major
#['uni3', [1,3], []],                   # major
#['abc', [1,5,6], [2,]],                   # major
#['wxyz', [3,5,6], []],                   # major
#]


if normalizeChords == 1:
    for chord in chords:
        ratios = chord[1]
        baseRatio = chord[1][0]
        if len(ratios) == 1 or ratios[0] == 1: #unique case for unison waves
            continue
        if baseRatio < 8:
            chord[1] = [partialRatio*2 for partialRatio in ratios]
            print(chord[0] + ' raised 1 octave')
print('Normalized Chord Array:'+str(chords))

#####################
# Signal Definitions
#####################
#a quick note, if you plan on designing a new wave type, it cannot return a value larger than 1, else the wav file cannot be written
class oscillators(object):
       
    def osc_sine(x, partials):
      return sin(x)

    def osc_tri(x, partials):
        tri = .63 * asin(sin(x))
        return tri
   
    def osc_saw(x, partials):
      k = pi/2/partials
      v = 0.0
      for n in range(1,partials):
        m = cos((n-1)*k)
        m *= m
        v += sin(n*x)/n * m # reduce amplitude of higher partials to minimize Gibbs effect
      v = v / 2
      return v

    def osc_saw1(x, partials):
      k = pi/2/partials
      v = 0.0
      for n in range(1,partials):
        m = cos(2*(n-1)*k)
        m *= m
        v += sin(n*x)/n * m # reduce amplitude of higher partials to minimize Gibbs effect
      v = v / 2
      return v

    def osc_saw2(x, partials):
      k = pi/2/partials
      v = 0.0
      for n in range(2,50):
        m = cos((n-1)*k)
        m *= m
        v += sin(n*x)/n * m # reduce amplitude of higher partials to minimize Gibbs effect
      v = v / 2
      return v
   
    def osc_sqr(x, partials):
      k = pi/2/partials
      v = 0.0
      for n in range(1,partials):
        if n%2==0: continue
        m = cos((n-1)*k)
        m *= m
        v += sin(n*x)/n * m # reduce amplitude of higher partials to minimize Gibbs effect
      return v

    def osc_sqr2(x, partials):
      k = pi/2
      v = 0.0
      for n in range(1,100):
        v += sin(x*(2*n-1))/(2*n-1)
      return v
       
    def osc_fm1(x,partials):
        #https://www.desmos.com/calculator/dpbikmtqnq
        wc = 3
        kw = 4.8
        wm = 2
        return sin(wc*x+kw*sin(wm*x))

    def osc_fm2(x,partials):
        #https://www.desmos.com/calculator/dpbikmtqnq
        wc = 1
        kw = 1.6
        wm = 3
        return sin(wc*x+kw*sin(wm*x))
       
    def osc_chor(x, partials):
      k = pi/2/partials
      v = 0.0
      for n in range(1,3): #change send value of range to change how many bumps in the wave
        m = cos((n-1)*k)
        m *= m
        v += sin(n*x)/n * m # reduce amplitude of higher partials to minimize Gibbs effect
      v = v / 2
      return v
   
    def osc_voic(x, partials):
      k = pi/2/partials
      v = 0.0
      for n in range(1,6): #change send value of range to change how many bumps in the wave
        m = cos((n-1)*k)
        m *= m
        v += sin(n*x)/n * m # reduce amplitude of higher partials to minimize Gibbs effect
      v = v / 2
      return v

    def osc_flut(x, partials):
      k = pi/2/partials
      v = 0.0
      for n in range(1,4): #change send value of range to change how many bumps in the wave
        if n%2==0: continue
        m = cos((n-1)*k)
        m *= m
        v += sin(n*x)/n * m # reduce amplitude of higher partials to minimize Gibbs effect
      return v
   
    def osc_whis(x, partials):
      k = pi/2/partials
      v = 0.0
      for n in range(1,3): #change send value of range to change how many bumps in the wave
        if n%2==0: continue
        m = cos((n-1)*k)
        m *= m
        v += sin(n*x)/n * m # reduce amplitude of higher partials to minimize Gibbs effect
      return v
   
    def osc_tsp(x,partials): #starts as a triangle and rounds out in the second half, calling it "triangle sine pulse" or tsp. Sounds cool
        max = 1
        ssp=  0.78*  ( (asin(cos(x/2 - 0.463) ) )**2) - 1.0002
        if ssp <= -max:
            ssp = -max
        if ssp >= max:
            ssp = max
        return ssp

    def osc_tuba(x,partials):
        return (sin(1+2*x+sin(-1+x+sin(x)))+sin(x))/2

    def osc_trum(x,partials):
        return (sin(1+2*x+sin(1+x+sin(x)))+sin(x))/2

    def osc_soft(x,partials):
        return 0.2+(sin(1+2*x+sin(2*x+sin(x)))+sin(x))/1.8
   
    def osc_pad(x,partials):
        return (sin(1+2*x+sin(2*x+sin(2*x)))+sin(x))/2

    def osc_tst1(x,partials):
        x /= 2
        y=3 # change this to get interesting varitations of the wave, 3 is pretty sounding, 8 and above add lots of noise
        return -(sin((2*x+sin((33+sin(y*x))))+2.13))
   
    def osc_tst2(x,partials):
        x /= 2
        y=9 # change this to get interesting varitations of the wave, 3 is pretty sounding, 8 and above add lots of noise
        return -(sin((2*x+sin((33+sin(y*x))))+2.13))

    def osc_bzzy(x,partials):
        x /= 2
        y= 8 # change this to get interesting varitations of the wave, 4 is pretty sounding, 8 and above add lots of noise
        return -0.62*asin(sin((2*x+sin((33+sin(y*x))))+2.13))
   
    def osc_bzz2(x,partials):
        x /= 2
        y= 4 # change this to get interesting varitations of the wave, 4 is pretty sounding, 8 and above add lots of noise
        return -0.62*asin(sin((2*x+sin((33+sin(y*x))))+2.13))

    def osc_dist(x,partials):
        return sin(1+x+sin(1+3*x+sin(9*x)))
   
    def osc_rnd(x, partials):
      return random.uniform(-1, 1)

    def osc_clp(x,partials): #easily clip a wave to make new sounds
        funcToClip = oscillators.osc_dist(x,partials)
        clipFactor = 2.2
        max = 1
        clippedSignal = clipFactor * funcToClip
        if clippedSignal <= -max:
            clippedSignal = -max
        if clippedSignal >= max:
            clippedSignal = max
        return clippedSignal

#######################
# Function Definitions
#######################

def write_chord_sample(filename, f0, ratios, func): #no idea how this one works but it works
    global digiProNum
    i = 1
    while os.path.isfile(filename) == True:
        print(filename+' already exists')
        filename = filename[:-4]+'('+str(i)+').wav'
        i += 1
    wav = wave.open(filename,'w')
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(SAMPLE_RATE)
    f0 = SAMPLE_RATE / round(SAMPLE_RATE / f0) # round it for perfect loops!
    period = int(SAMPLE_RATE / f0)
    i = 0
    while i < period:
        t = i*pi*2/SAMPLE_RATE
        v = 0.0
        for r in ratios:
            f = f0 * r
            partials = int(SAMPLE_RATE/2/f) # Nyqist frequency / note frequency
            #print('in loop '+str(partials))
            v += func(f*t, partials)
        v /= len(ratios)
        data = struct.pack('<h', int(32767*v))
        wav.writeframes(data)
        i += 1
    wav.close()
    print('GENERATED: '+filename+'  IT`S RATIOS: '+str(ratios))
    os.utime(filename,(0,baseEpoch+epochInc * digiProNum)) #write iterating timestamp to file to organize wavs. old:1009836000 + 31536000 * digiProNum
    digiProNum += 1


def write_all_chords(func):
    path = func.__name__
    os.makedirs(path)
    for chord in chords:
        name = chord[0][:3]
        ratios = chord[1]
        customInversions = chord[2]
        print('\nGENERATING '+chord[0])
        #skip everything for unison waves
        if len(ratios) == 1 or len(customInversions) == 0 or ratios[0] == 1:
            name = chord[0][:4]
            print('in loop '+name)
            filename = path+'/'+name+'.wav'
            write_chord_sample(filename, F0 / ratios[0], ratios, func)
            continue
        else:
            filename = path+'/'+name+'0.wav'
        write_chord_sample(filename, F0 / ratios[0], ratios, func) # root position, root at 0

        #print('largest ratio / smallest ratio = '+str(ratios[len(ratios)-1]/ratios[0]))

        inversionFactor=2
        if smartInvert == 1:
            while(inversionFactor <= ratios[len(ratios)-1]/ratios[0]):
                inversionFactor*=2
            #print('smart power = '+str(inversionFactor))
       
        #Do all of the inversion generation logic
        if genInversions == 1:
            print('GENERATING INVERSIONS:')
            if genCustomInversions == 1:
                print('Custom Inversions for '+name+'are '+str(customInversions))
            inversionCount = 1
            for position in range(1,len(ratios)): # second value in range controls how many inversions are generated. len(ratios) will generate all inversions
                inversion = list(map(lambda ratio: ratio*inversionFactor, ratios[:position]))+ratios[position:]
                #print('inversion= '+str(inversion))
                filename = path+'/'+name+str(inversionCount)+'.wav'
                if genCustomInversions == 1:
                    if inversionCount in customInversions:
                        pass
                    else:
                        print('skipping   '+filename+'  IT`S RATIOS: '+str(ratios))
                        inversionCount += 1
                        continue
                write_chord_sample(filename, F0 / ratios[0], inversion, func)
                inversionCount += 1
               
            if genUp1Octave == 1:
                ratiosUp1Octave=[]
                for ratio in ratios:
                    ratiosUp1Octave.append(ratio * 2)
                filename = path+'/'+name+'+.wav'
                #print('doubled root ratios: '+str(ratiosUp1Octave))
                write_chord_sample(filename, F0 / ratios[0], ratiosUp1Octave, func)
            #print('\n')


def write_all_unison():
    print('in write all unison '+os.getcwd())
    print(uniPath)
    print('/'+uniPath+'/')
    if os.path.exists(uniPath) and os.path.isdir(uniPath): #delete chords & export dir if they already exist
        shutil.rmtree(uniPath)
        print('deleted unison export path')
    if not os.path.exists(uniPath):
        os.makedirs(uniPath)
        print('made unipath directory')
    global digiProNum
    digiProNum = 0
    #os.chdir(home)
    allOscillators = [func for func in list(oscillators.__dict__.keys()) if callable(getattr(oscillators(), func)) and not func.startswith("__")]
    for oscToGen in allOscillators:
        func = getattr(oscillators, oscToGen)
        funcStr = func.__name__.replace('osc_','')+'.wav'
        print(funcStr)
        write_chord_sample(uniPath+'/'+funcStr, F0, [1], func)


# this function adds files from a user defined directory to the end of the generated file list for the MnM
# this can be useful to add a few extra monophonic tones to the end of the digipro bank such as a noise oscilator and some bass notes
def append_other_waves(func,addendumPath):
    global digiProNum
    print('in append '+os.getcwd())
    if not os.path.exists(addendumPath):
        os.makedirs(addendumPath)
    path = func.__name__
    filesToAppend = os.listdir(addendumPath+'/')
    #print('Unsorted filesToAppend='+str(filesToAppend)+'\n')
    filesToAppend = sorted(filesToAppend)
    #print('Sorted filesToAppend='+str(filesToAppend)+'\n')
    for fileToAppend in filesToAppend:
        truncFileName = fileToAppend[-8:] #chop off everything except 1234.XYZ from file name
        truncFileName = truncFileName.replace('_','') #if the desired appeneded file is only 3 letters ie tri, remove leading underscore
        shutil.copyfile(addendumPath+'/'+fileToAppend, path+'/'+truncFileName)
        os.utime(path+'/'+truncFileName,(0,baseEpoch+epochInc * digiProNum))
        print('appended "'+fileToAppend+'" as "'+truncFileName+'"')
        digiProNum += 1

# Oscillator Design/ Debugging Graph Generation
def printGraphs(path):
    print('in printgraphs '+os.getcwd())
    filesToPlot = os.listdir(path)
    filesToPlot.sort(key=lambda x: os.path.getmtime(path+'/'+x))
    print('filesToPlot='+str(filesToPlot)+'\n')
    i = 0
    gs = sqrt(len(filesToPlot)) #find square root of total samples to begin building a NxN grid
    gs = ceil(gs) # round up the grid size
    print(str(gs)+'x'+str(gs)+' grid for all samples')
    figure, axis = plt.subplots(gs, gs,figsize=(gs*5,gs*4),squeeze=False) #
    plt.rc('font', size=8)
    plt.rc('axes', titlesize=8)     # fontsize of the axes title
    plt.rc('axes', labelsize=4)     # fontsize of the x and y labels
    figure.suptitle('samples',y=-.01)

    row = 1
    col = 1
    gridControl = gs

    while i < len(filesToPlot):
        filename = filesToPlot[i]
        input_data = read(path+'/'+filename)
        audio = input_data[1]
        # plot the wav
        axis[row-1, col-1].plot(audio[0:])
        #axis[row-1, col-1].yaxis.set_visible(False)
        axis[row-1, col-1].set_title(path+'/'+filename)
       
        if col*row == gridControl:
            row += 1
            gridControl = gridControl + gs
            col = 1
        else:
            col +=1
        i+=1
       
    plt.subplots_adjust(wspace=.2, hspace=.3)
    plt.show()
    plt.close()
    #os.chdir('/') #close directory to release read onyl latch on file


#######################
# .Wav File Generation
#######################
allOscillators = [func for func in list(oscillators.__dict__.keys()) if callable(getattr(oscillators(), func)) and not func.startswith("__")]
print('All Oscillators: '+str(allOscillators))
for osc in allOscillators:
    if os.path.exists(osc) and os.path.isdir(osc): #delete chords & export dir if they already exist
        shutil.rmtree(osc)
        print('deleted '+osc+' folder')

for oscToGen in oscList:
    digiProNum = 0
    try:
        func = getattr(oscillators, oscToGen)
    except AttributeError:
        raise NotImplementedError("No signal `{}` in oscillators class".format(oscToGen))
    write_all_chords(func)
    if printGraphsFlag == 1:
        printGraphs(func.__name__)
    chordWavsGenerated = digiProNum # gets number of files generated before appending pre-exising files
    append_other_waves(func,addendumPath)

write_all_unison()
#printGraphs(uniPath)


if len(oscList) != 0:
    print(spacer)
    print('Oscillators generated: '+ str(oscList))
    print (str(len(chords)) + ' chord types')
    print (str(chordWavsGenerated) + ' chords generated per oscillator')# prints number of chords in folder/length of digipronum before files are appended
    print(str(len(os.listdir(addendumPath)))+' files added from /'+addendumPath+'/')
    print(os.getcwd())
    print(str(chordWavsGenerated+len(os.listdir(addendumPath)))+' files per oscillator to export to C6, must be below 64 for MnM')
    print(spacer)
