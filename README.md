# THIS README & CODE IS A WIP

# Single Cycle Chord Generator for the Elektron Monomachine 

This program generates single-cycle just intonation chord waveforms for the Elektron Monomachine giving the user control over the generation parameters, waveform type, and inversion/voicing positions to generate. The program will also append user specified files to the end of the output list for quick importing into Elektron's C6 software.

This tool is based on [original code by lucianon](https://github.com/len/SCC), adding to its functionality & specializing it for use with Elektron's C6 software & Monomachine Synthesizer. My desire to make this program was originally inspired by Elektronauts forum user Veets in [this video.](https://www.youtube.com/watch?v=6O-p-Kbrt9o)

## Usage
In the "Generation Controls & Chord Defintions" section of `MnMSCC.py` the below parameters are availible to edit to quickly make changes to what chords the program generates. They are all off/on swtiches except `onlyGenXInversion` which can be an integer value, whos "off" position is also 0.
### Generation Controls
```
normalizeChords
```
This flag can be 0 (off) or 1 (on) and raises the highest base ratio of the chords you want to generate 1 octave to match the Minor chord whos Just Intonic ratios are [10,12,15]. Without getting into the math (that I don't fully understand) the ratios of the minor chord put it 1 octave above the others relatively speaking so anything lower must be raised to match it so they all play in the same relative octave on the Monomachine. Single ratio inputs are ignored (unison)
```
genInversions
```
This flag can be 0 (off) or 1 (on) and controls wheather any inversions are generated. If set to 0, none of the other inversionr related flags will do anything.
```
inversionLimit 
```
3 # integer number of inversions for the program to generate. set to value 99 to disable the limit.

onlyGenXInversion = 0 # 0 will disable this flag. integer number of the only inversion you want to generate. must be below the inversion limit. cannot be used in tandem with onlyGenEvenInversions
onlyGenEvenInversions = 0 # only generates the even number inversions for each chord. ex root postion, 2nd inversion, 4th inversion. cannot be used in tandem with onlyGenXInversion
genUp1Octave = 0 # will generate an additional chord that is the root position raised 1 octave

#turn this on to generate matplotlib graphs of the waves generated. Useful for debugging new waveform types
```
printGraphsFlag = 1
```
→
### Sending the Generated Waveforms to Elektron's C6 Software
After the program completes, there will be a folder containing all of the samples in .wav format to send to the monomachine. C6 only uses 4 letter names for each .wav once it send them to a machine, taking the first three and last characters of an input file to use as the display name.

For example:
**Cho**rdSample0**7**.wav would yield:
**CHO7** as a display name on the Monomachine for an input waveform (and Machinedrum UW)

While this works well enough as a catchall way to autoname files, you cannot organize the files numerically without the prefix being used to generate a display name for the waveform on the Monomachine. To get around this, the program appends a dummy modified date to each .wav file increased by 1 year per file. This allows you sort your folder by date modifed and drag them into C6 in an arbitrary order with out 
