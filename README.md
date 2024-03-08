# Elektron Monomachine Single Cycle Chord Generator

This program generates single-cycle just intonation chord waveforms for the Elektron Monomachine with full control over the generation parameters, waveform type, and inversion positions. The program will also append user specified files to the end of the output list.

This tool is based on [original code by lucianon](https://github.com/len/SCC), adding to its functionality & specializing it for use with Elektron's C6 software & Monomachine Synthesizer.

## Usage
In the "Generation Controls & Chord Defintions" section of `MnMSCC.py` the below parameters are availible to edit to quickly make changes to what chords the program generates:
```
normalizeChords = 1
genInversions = 0
inversionLimit = 3 # integer number of inversions for the program to generate. set to value 99 to disable the limit.
onlyGenXInversion = 0 # 0 will disable this flag. integer number of the only inversion you want to generate. must be below the inversion limit. cannot be used in tandem with onlyGenEvenInversions
onlyGenEvenInversions = 0 # only generates the even number inversions for each chord. ex root postion, 2nd inversion, 4th inversion. cannot be used in tandem with onlyGenXInversion
genUp1Octave = 0 # will generate an additional chord that is the root position raised 1 octave

#turn this on to generate matplotlib graphs of the waves generated. Useful for debugging new waveform types
printGraphsFlag = 1
```
