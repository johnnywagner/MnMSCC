#Uncomment this below pip install if using Jupyter Notebook
#%pip install pydub

"""
This program creates single-cycle waveforms for just intonation chords
for the Elektron Monomachine (MnM) MK2 models based on Luciano Notarfrancesco's original code.
The intended usage is to set your parameters in the drag prepared files this program outputs into Elektron's C6 sysex software
to conver them into "DigiPro" formatted sysex files to then send them to the Monomachine.

The C6 software has a funny way of truncating file names to prepare them for the MnM (& Machinedrum). It takes the first
3 ascii characters and the last of the file name, and this is what it will show up as on the monomachine.
for example a file named "Chord Stab 31.wav" would be show up as 'CHO1.wav'

Original Code by:
2020/4/18, Luciano Notarfrancesco, github.com/len

Monomachine Adaptation & Additional Signal types
2024/2/28 , JW github.com/

"""


'''
useful webapps for use in tandem with this program:
http://scw.sheetsofsound.com/editor.html
https://justintonate.com/
'''


from math import pi, sin, cos, asin, sqrt, ceil
import wave
import struct
import os
import shutil
import random
from pydub import AudioSegment, effects

# only needed for signal design and debugging
from scipy.io.wavfile import read
import matplotlib.pyplot as plt

##########################################
# Generation Controls & Chord Defintions
##########################################
F0 = 261.6255653005986 # C4= 261.6255653005986  or 261.625565
SAMPLE_RATE = 20000.0 # 10000 is known good. common sample rates you may use for other use cases besides the MnM: 22050,24000,44100,48000

#Inversion Parameters
normalizeChords = 0
genInversions = 0
inversionLimit = 2 # integer number of inversions for the program to generate. set to value 99 to disable the limit.
onlyGenXInversion = 2 # 0 will disable this flag. integer number of the only inversion you want to generate. must be below the inversion limit. cannot be used in tandem with onlyGenEvenInversions
onlyGenEvenInversions = 0 # only generates the even number inversions for each chord. ex root postion, 2nd inversion, 4th inversion. cannot be used in tandem with onlyGenXInversion
genUp1Octave = 0 # will generate an additional chord that is the root position raised 1 octave

#turn this on to generate matplotlib graphs of the waves generated. Useful for debugging new waveform types
printGraphsFlag = 0

oscList = [
#'osc_sin',
#'osc_tri',
#'osc_saw',
#'osc_sqr',
'osc_choir',
#'osc_voice',
#'osc_flute',
#'osc_whistle',
#'osc_tsp',
#'osc_tuba',
#'osc_trumpet',
#'osc_soft',
#'osc_harmsin',
#'osc_harmsin2',
#'osc_buzzy',
#'osc_buzzy2',
#'osc_distort',
#'osc_clp',
#'osc_rnd',
]

#experimental/buggy wave compression:
#I only get "good" results at F0 ~ 10 with a lowpass of ~180
compressChords = 0
lowPassFreq = 180

chords = [
['maj', [4,5,6]],                   # major
['mj7', [8,10,12,15]],              # major7
['mj9', [4,5,6,9]],                 # maj add 9
['m+9', [4,5,6,18]],                # maj add 9 but the 9 is up an octave
##['un2',  [4,5,6,8,9]],              # C4,E4,G4,C5,D5
['un3',  [4,5,6,8,9,12,18]],        # C4,E4,G4,C5,D5,G5,D6
['un4', [12,15,18,24,27,32]],       # C4,E4,G4,C5,D5,F5
['min',  [10,12,15]],               # C minor chord. generates a C min cycle => plays as e min on MnM
['mn7', [10,12,15,18]],             # C minor 7 C,Eb,G,Bb
['m7»', [10,12,15,18,30]],          # C minor 7 add g octave C,Eb,G,Bb,G
['m7+', [10,12,15,18,24]],          # C minor 7 C,Eb,G,Bb,Eb
##['7++', [10,12,15,18,24,30]],      # C minor 7 add eb & g octave. C,Eb,G,Bb,Eb,G
['7b5', [5,6,7,9]],                 # Cmin7b5 half-diminished (perfect). Used in Black Cow by Steely Dan
##['mn9', [20,24,30,36,45]],         # minor 9th [20,24,30,36,45]]
##['m9m', [10,12,15,18,22.5]],       # minor 9th [20,24,30,36,45]]
##['n79', [20,24,30,36,45]],         # min 7 add 9  
['b79', [12,16,19,24,29,36]],       # G bass + Minor 7 add 9
['nj9', [8,9,16,19,24,36]],         # Cm(maj9)
##['nt4', [30,36,40,45]],            # C minor triad add 4
['n4 ', [10,12,15,27]],             # C minor triad add 4 but the 4 is up 1 octave
##['n+9', [20,24,30,45,60]],         # A3+C3+E3+B5+E6 too big of ratios
['mno', [10,12,15,24,30]],          # C4, Eb4, G4, Eb5, G5 # minor open
['un5', [10,12,15,25]],             # C3,Eb3, G3, E4
['un6', [10,12,15,25,34]],          # C3, Eb3, G3, E4, A5
['n+7', [10,12,15,19]],              # C min add 7 chord 
##['n72', [8,12,14,18,23]],            # F3 bass on a minor add 7 (F3, C4, Eb4, G4, B4)
['n73', [12,16,19,24,30]],           # G3 bass on a minor add 7 (G3, C4, Eb4, G4, B4)
##['jzy', [20,24,30,45,50,67,75,90]], # idk man calling this one jazzy, root chord is definitely minor. (F3,Ab3,C4,G4,A4,D5,E5,G5)
['su2', [8,9,12]],                  # sus2
['s2!', [4,6,8,9]],                 # csus 2 +c octave + inverted d
['s2@', [12,16,18,24,27]],          # idk G3,C4,D4,G4,A4
['s2#', [8,9,12,16,18]],            # C4,D4,G4,C5,D5
['su4', [6,8,9]],                   # sus4
['s4!', [6,9,12,16,18]],            # Nice open sus 4 chord  C4,G4,C5,F5,G5
['s4@', [6,8,9,12,16,24]],          # C4,F4,G4,C5,F5,C6
['s4#', [12,16,18,23]],             # C maj 7th suspended 4th
['s49', [12,16,18,23,27]],          # C maj 7th suspended 4th add 9
['dim', [5,6,7]],                   # perfect diminished
['di7', [10,12,14,17]],             # Francois-Joseph Fetis dim (17-limit tuning)(idk what this is) B3+D4+F4+Ab4
['i7!', [10,12,14,17,20]],          # Francois-Joseph Fetis dim (17-limit tuning) B3+D4+F4+Ab4+B5
##['di9', [20,24,28,38,45]],          # diminished major 9 chord
['7  ', [4,5,6,7]],                 # C7 (harmonic 7)
['9  ', [4,5,6,7,9]],               # C9 (harmonic 9)
['9+o', [4,5,6,7,9,12]],            # C9 (harmonic 9) + G
['9++', [4,5,6,7,9,12,14]],
##['do7', [10,12.5,15,18]],          # ?dominant7 [20,25,30,36]
##['7b5', [25,30,36,45]],             # ?dom7b5
##['7#9', [20,25,30,36,48]],         # ?dom7#9
['blz', [15,18,20]],                # ? C + Eb + F looks like F harmonic dyad (power chord) add b7 inverted on C
['hmm', [12,16,17,18]],             # originally listed as "dream" chord
['un6',[12,15,20,29]],              # C4,E4,A4,Eb5

# 2 note intervals
#['m-2', [15,16]],                  # minor 2nd,           C+Db    [15,16]
#['M+2', [8,9]],                    # Major 2nd,           C+E    [8,9]
#['m-3', [10,12]],                  # minor 3rd interval,    C+Eb  [5,6]
#['M+3', [8,10]],                   # Major 3rd internval,   C+E  [4,5]
#['4th', [3,4]],                    # Perfect 4th internval, C+F   [3,4]
#['tri', [8,11]],                   # Tritone internval. could be 5/7 or 8/11 too?
#['5th', [8,12]],                   # Perfect 5th internval, C+G [2,3]
#['m-6',[10,16]],                   # minor 6th internval,   C+Ab [5,8]
#['M+6',[6,10]],                    # Major 6th internval,   C+A  [3,5]
#['m-7',[10,18]],                   # minor 7th internval,   C+Bb  [5,9]
#['M+7',[8,15]],                    # Major 7th internval,   C+B

# Weirdness below, try experimenting with non integer ratios for horizontally clipping chords
#['imp',[1.333333,4.4653563465,6.92929292929]],

#the below chords ratios are too large to work well with the mnm, I found to be uninteresting sounding, or not useful in the context of the mnm
#['mm7', [40,48,60,75]],              # ?minmaj7
#['smj', [1,3,5]],                  # open Major C4 E5 G6
#['di2', [20,24,29]],              # diminished
#?['min-1', [12,15,20]],            # F Minor chord. generates a F min cycle => plays as ? on MnM
#?['min-2', [30,20,24]],            #   Minor chord. generates a F min cycle => plays as ? on MnM
##['dim', [20,24,29]],               # true diminished?

# root note
['uni', [1]],                        # C note. set the ratio to 1 for F0 to 4 to raise it 2 octaves, 8 to raise 3
# ['ui0', [1,4]],                        # C note. set the ratio to 1 for F0 to 4 to raise it 2 octaves, 8 to raise 3
# ['u0+', [1,8]],                        # C note. set the ratio to 1 for F0 to 4 to raise it 2 octaves, 8 to raise 3
 ['ui1', [1,2,4]],                        # C note. set the ratio to 1 for F0 to 4 to raise it 2 octaves, 8 to raise 3
# ['ui2', [1,2,4,8]],     #ehh                   # C note. set the ratio to 1 for F0 to 4 to raise it 2 octaves, 8 to raise 3
 ['ui3', [1,16]],       #like this one                 # C note. set the ratio to 1 for F0 to 4 to raise it 2 octaves, 8 to raise 3
# ['ui4', [1,2,16]],                        # C note. set the ratio to 1 for F0 to 4 to raise it 2 octaves, 8 to raise 3
 ['ui5', [1,4,16]],     #like this one                   # C note. set the ratio to 1 for F0 to 4 to raise it 2 octaves, 8 to raise 3
 ['ui6', [1,8,16]],                        # C note. set the ratio to 1 for F0 to 4 to raise it 2 octaves, 8 to raise 3
# ['ui7', [1,2,4,16]],                        # C note. set the ratio to 1 for F0 to 4 to raise it 2 octaves, 8 to raise 3
 ['ui8', [1,2,4,8,16]],                        # C note. set the ratio to 1 for F0 to 4 to raise it 2 octaves, 8 to raise 3
# #['ui5', [1,32]],     #too big                   # C note. set the ratio to 1 for F0 to 4 to raise it 2 octaves, 8 to raise 3


]


'''
the below loop raises a chords ratio to match
the highest base ratio of chord you want to generate
Minor [10,12,15] is the odd man out of simple chords and requires
all other simpler chords/intervals  are pitched up 1 octave to match its pitch
single ratios inputs are ignored (unison)
'''
if normalizeChords == 1:
    for chord in chords:
        ratios = chord[1]
        baseRatio = chord[1][0]
        if len(ratios) == 1: #unique case for unison waves
            continue
        if baseRatio < 8:
            chord[1] = [partialRatio*2 for partialRatio in ratios]
            print(chord[0] + ' raised 1 octave')

#        if len(chord[1]) <= 2: # move unison & dyads up or down octaves to use them as under/over tones for main chords with the DigiPRO Doubledraw (DDRAW) machine
#            ratios = chord[1]
#            chord[1] = [partialRatio*2**2 for partialRatio in ratios]
#            print(chord[0] + ' raised interval 1 octave')

print('Normalized Chord Array:'+str(chords))

###################################
# Global Variables/Constants
###################################
digiProNum = 0
home = os.getcwd()
print('home = '+home)
spacer = '\n█████████████████████████████████████████████████████████████████████████████████████████████████████████\n'
'''
'addendumPath' below defines the folder name where the files to add to the end of
the digipro bank are. This folder needs to be in the same folder as the python code.
These files can be .wav, .syx, or any other audio file type accepted by C6 that has a file extension length of 3 characters (.wav) &
can have any naming convention for ordering them, as long as they end in EXACTLY 4
letters/numbers you want them to show up as on the MnM.
ie: 01tri1.wav" & "01_signaldescription_saw .syx"
will generate: 'tri1.wav' & 'saw .wav' respectively.
notice the space after "saw" on the second one to keep its name 4 characters long.
'''
addendumPath = 'userFiles'

#####################
# Signal Definitions
#####################
#a quick note, if you plan on designing a new wave type, it cannot return a value larger than 1, else the program will fail.
class oscillators(object):
       
    def osc_sin(x, partials):
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
    
    def osc_sqr(x, partials):
    # graphical representation of how this works: https://www.desmos.com/calculator/uocla9yrrf
      k = pi/2/partials
      v = 0.0
      for n in range(1,partials):
        if n%2==0: continue
        m = cos((n-1)*k)
        m *= m
        v += sin(n*x)/n * m # reduce amplitude of higher partials to minimize Gibbs effect
      return v
   
    def osc_choir(x, partials):
      k = pi/2/partials
      v = 0.0
      for n in range(1,3): #change send value of range to change how many bumps in the wave
        m = cos((n-1)*k)
        m *= m
        v += sin(n*x)/n * m # reduce amplitude of higher partials to minimize Gibbs effect
      v = v / 2
      return v
    
    def osc_voice(x, partials):
      k = pi/2/partials
      v = 0.0
      for n in range(1,6): #change send value of range to change how many bumps in the wave
        m = cos((n-1)*k)
        m *= m
        v += sin(n*x)/n * m # reduce amplitude of higher partials to minimize Gibbs effect
      v = v / 2
      return v

    def osc_flute(x, partials):
      k = pi/2/partials
      v = 0.0
      for n in range(1,4): #change send value of range to change how many bumps in the wave
        if n%2==0: continue
        m = cos((n-1)*k)
        m *= m
        v += sin(n*x)/n * m # reduce amplitude of higher partials to minimize Gibbs effect
      return v
    
    def osc_flute2(x, partials):
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

    def osc_trumpet(x,partials):
        return (sin(1+2*x+sin(1+x+sin(x)))+sin(x))/2

    def osc_soft(x,partials):
        return 0.2+(sin(1+2*x+sin(2*x+sin(x)))+sin(x))/1.8

    def osc_harmsin(x,partials):
        x /= 2
        y=3 # change this to get interesting varitations of the wave, 3 is pretty sounding, 8 and above add lots of noise
        return -(sin((2*x+sin((33+sin(y*x))))+2.13))
    
    def osc_harmsin2(x,partials):
        x /= 2
        y=9 # change this to get interesting varitations of the wave, 3 is pretty sounding, 8 and above add lots of noise
        return -(sin((2*x+sin((33+sin(y*x))))+2.13))

    def osc_buzzy(x,partials):
        x /= 2
        y= 8 # change this to get interesting varitations of the wave, 4 is pretty sounding, 8 and above add lots of noise
        return -0.62*asin(sin((2*x+sin((33+sin(y*x))))+2.13))
    
    def osc_buzzy2(x,partials):
        x /= 2
        y= 4 # change this to get interesting varitations of the wave, 4 is pretty sounding, 8 and above add lots of noise
        return -0.62*asin(sin((2*x+sin((33+sin(y*x))))+2.13))

    def osc_distort(x,partials):
        return sin(1+x+sin(1+3*x+sin(9*x)))
   
    def osc_rnd(x, partials):
      return random.uniform(-1, 1)

    def osc_clp(x,partials): #easily clip a wave to make new sounds
        funcToClip = oscillators.osc_buzzy(x,partials)
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
def ratios_string(ratios):
  answer = ''
  first = True
  for r in ratios:
    if first:
      first = False
      if r < 10: answer += ' ' # pad with space so chords with small ratios show up first when browsing samples in octatrack
      answer += '%d' % r
    else:
      answer += ',%d' % r
  if len(ratios) == 1 and ratios[0] == 1:
    answer += ',1' # special notation for unison
  return answer


def write_chord_sample(filename, f0, ratios, func): #no idea how this one works but it works
    global digiProNum
    
    i = 1
    while os.path.isfile(filename) == True:
        print(filename+' already exists')
        filename = filename[:-4]+' ('+str(i)+').wav'
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
    print(filename+'  Ratios: '+str(ratios))

    if compressChords == 1:    
        compress_dyanmics(filename)
    
    os.utime(filename,(0,1009836000 + 31536000 * digiProNum)) #write iterating timestamp to file to organize wavs
    digiProNum += 1


def compress_dyanmics(filename):  #try turning off the low pass with compressor parameters:-100.0,2.0,1,1 for intersting distortion
    wav2compress = AudioSegment.from_file(filename, format="wav")
    sourceLength = len(wav2compress)#+1
    #print('File sample length= '+ str(sourceLength) + '\nDoubledfile sample length= '+ str(sourceLength*2))
    wav2compress *= 3 #oversample wave to compress so that it can be offset by 0.2
    wav2compress = effects.compress_dynamic_range(wav2compress,
    -8.0, # threshold in dB
    4.0,   # ratio x:1
    .8,   # attack in ms
    .8)   # release in ms
    wav2compress = effects.low_pass_filter(wav2compress,lowPassFreq) # cutoff freq needed will be affected by F0
    #print('compressed length:'+str(len(wav2compress)))
    wav2compress = wav2compress[sourceLength:2*sourceLength] # sourceLength*2
    #print('compressed length /2 :'+str(len(wav2compress)))
    wav2compress.export(filename[:-4]+'compressed.wav', format='wav') #chop off .wav and add compressed  filename[:-4]+'compressed.wav'


def write_all_chords(func):
    os.chdir(home)
    path = func.__name__
    if not os.path.exists(path):
        os.makedirs(path)
    for chord in chords:
        name = chord[0]
        ratios = chord[1]

        #skip everything for unison waves. you could comment this out
        if len(ratios) == 1: 
            filename = path+'/'+name+'.wav'
            write_chord_sample(filename, F0 / ratios[0], ratios, func) # root position, root at 0
            continue
        else:
            filename = path+'/'+name+'0.wav'
        write_chord_sample(filename, F0 / ratios[0], ratios, func) # root position, root at 0

        #Do all of the inversion generation logic
        if genInversions == 1:
            inversionCount = 1
            
            #get the actual number of inversions to generate if the number of inversion that would be generated is less than the user set limit
            trueInversionLimit = inversionLimit
            if len(ratios) < inversionLimit:
                trueInversionLimit = len(ratios)-1
                print('trueInversionLimit for '+name+' is '+str(trueInversionLimit))
                
                
            for position in range(1,trueInversionLimit+1): # second value in range controls how many inversions are generated. len(ratios) will generate all inversions
            
                if onlyGenXInversion != 0 and onlyGenEvenInversions == 0:
                        if inversionCount != onlyGenXInversion:
                            print('skipping '+name+str(inversionCount))
                            inversionCount += 1
                            continue
                    
                if onlyGenEvenInversions == 1 and onlyGenXInversion == 0:
                    if (inversionCount % 2) != 0:
                        print('skipping '+name+str(inversionCount))
                        inversionCount += 1
                        continue
                        
                inversion = list(map(lambda ratio: ratio*2, ratios[:position]))+ratios[position:]
                filename = path+'/'+name+str(inversionCount)+'.wav'
                write_chord_sample(filename, F0 / ratios[0], inversion, func)
                inversionCount += 1
                
            if genUp1Octave == 1:
                ratiosUp1Octave=[]
                for ratio in ratios:
                    ratiosUp1Octave.append(ratio * 2)
                filename = path+'/'+name+'+.wav'
                #print('doubled root ratios: '+str(ratiosUp1Octave))
                write_chord_sample(filename, F0 / ratios[0], ratiosUp1Octave, func)


# this function adds files from a user defined directory to the end of the generated file list for the MnM
# this can be useful to add a few extra monophonic tones to the end of the digipro bank such as a noise oscilator and some bass notes
def append_other_waves(func,addendumPath):
    os.chdir(home)
    global digiProNum
    print('in append '+os.getcwd())
    if not os.path.exists(addendumPath):
        os.makedirs(addendumPath)
        print('test')
    path = func.__name__
    #print(path+'/')
    #print(addendumPath+'/')
    filesToAppend = os.listdir(addendumPath+'/')
    print('Unsorted filesToAppend='+str(filesToAppend)+'\n')
    filesToAppend = sorted(filesToAppend)
    print('Sorted filesToAppend='+str(filesToAppend)+'\n')
    for fileToAppend in filesToAppend:
        truncFileName = fileToAppend[-8:] #chop off everything except 1234.XYZ from file name
        shutil.copyfile(addendumPath+'/'+fileToAppend, path+'/'+truncFileName)
        os.utime(path+'/'+truncFileName,(0,1009836000 + 31536000 * digiProNum))
        digiProNum += 1


# Oscillator Design/ Debugging Graph Generation
def printGraphs(func):
    os.chdir(home)
    path = os.getcwd()+'/'+func.__name__
    print(os.getcwd())
    os.chdir(path)
    print(os.getcwd())
    filesToPlot = os.listdir(os.getcwd())
    filesToPlot.sort(key=lambda x: os.path.getmtime(x))
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
    #os.chdir('/') #close directory to release read onyl latch on files



#######################
# .Wav File Generation
#######################
for oscToGen in oscList:
    digiProNum = 0
    try:
        func = getattr(oscillators, oscToGen)
    except AttributeError:
        raise NotImplementedError("No signal `{}` in oscillators class".format(oscToGen))
    if os.path.exists(func.__name__) and os.path.isdir(func.__name__): #delete chords & export dir if they already exist
        shutil.rmtree(func.__name__)
    write_all_chords(func)
    if printGraphsFlag == 1:
        printGraphs(func)
    chordWavsGenerated = digiProNum # gets number of files generated before appending pre-exising files
    append_other_waves(func,addendumPath)

print(spacer)
print('Oscillators generated: '+ str(oscList))
print (str(len(chords)) + ' chord types')
print (str(chordWavsGenerated) + ' chords generated per oscillator') # prints number of chords in folder/length of digipronum before files are appended
print(str(len(os.listdir(addendumPath)))+' files added from /'+addendumPath+'/')
print(os.getcwd())
print(str(digiProNum)+' files per oscillator to export to C6, must be below 64 for MnM')
print(spacer)
