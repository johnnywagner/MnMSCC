# THIS README & CODE IS A WIP but the code works well
to do:
* decide on final chord list. just need to make cuts and decisoons. I definitely want a few inversions in there.
* clean up code section by section
* clean up this github readme
* make final post to elektronauts

# Single Cycle Chord Generator for the Elektron Monomachine (and other samplers) 

This program generates single-cycle just intonation chord waveforms for the Elektron Monomachine giving the user control over the generation parameters, waveform type, and inversion/voicing positions to generate. The program will also append user specified files to the end of the output list for quick importing into Elektron's C6 software.

This tool is based on [original code by lucianon,](https://github.com/len/SCC) adding to its functionality & specializing it for use with Elektron's C6 software & Monomachine Synthesizer. My desire to make this program was originally inspired by Elektronauts forum user Veets in [this video.](https://www.youtube.com/watch?v=6O-p-Kbrt9o)

## Usage
In the "Generation Controls & Chord Defintions" section of `MnMSCC.py` the below parameters are availible to edit to quickly make changes to what chords the program generates, using this part of the code as a GUI of sorts. The below explanation of what each parameter does is not in order to the code, but organized differently here based on 

### Sample Rate
```
SAMPLE_RATE =
```
This will change the sample rate the single cycle samples are generated at. The mnm doesn't *technically* care about sample rate like the Octatrack and other samplers do, but I did find through lots of trial & error that certain sample rates yield better results on the monomachine for different wave types. YMMV, and I found 48005 to sound good for all chords & wave types. 

### Boolean Generation Controls (0 or 1)
```
altChordsFlag =
```
This is kind of a hack-y way to have 2 chord lists in the same program. Turning this on will use the second chord list instead of the first. I did this because I wanted to have 2 banks, one with just a bunch of different large chord and 1 or 2 inversions of each common chord type and another with simpler chords and all of their inversions.

```
normalizeChords =
```
This flag can be 0 (off) or 1 (on) and raises the highest base ratio of the chords you want to generate 1 octave to match the Minor chord whos Just Intonic ratios are [10,12,15]. Without getting into the math (that I don't fully understand) the ratios of the minor chord put it 1 octave above the others relatively speaking so anything lower must be raised to match it so they all play in the same relative octave on the Monomachine. Single ratio inputs are ignored (unison)
```
genInversions =
```
This flag can be 0 (off) or 1 (on) and controls wheather any inversions are generated. If set to 0, none of the other inversionr related flags will do anything.

```
genUp1Octave = 
```
This will generate an additional chord that is the root position raised 1 octave. I found this to not be very useful for the Monomachine but decided to leave it in incase anyone wants to create some chord banks for different purposes.
```
smartInvert = 
```
This will invert chords based on their smallest ratios compared to their largest, rather than just doubling a ratio to create an inversion. For larger chords such as major11, whose ratios are 8:10:12:15:18:23, its 1st inversion would normally be generated as **16**:10:12:15:18:23 where as when smartInvert is enabled, it will raise it 2 octaves instead of 1 to generate an inversion so that the inverted note is always larger than the largest ratio. This would yield **32**:10:12:15:18:23 where 32 is greater than 23.

```
genCustomInversions = 
```
Turning this flag on allows the user to generate their own custom list of inversions, rather than generating all possible inversions for every chord. The custom inversion data for each chord is stored in the 3rd slot of its list inside of the larger chord array. 
* For example:
      
  ```
  chords = [
  [ 'mj7' , [8,10,12,15] , [1,3] ], ]

Would generate the 1st and 3rd inversions of the chord whose ratios are 8:10:12:15. The program will yeild: mj70.wav (it always generates root position), mj71.wav (1st inversions) & mj73.wav (3rd inversion)

```
appendUserFilesFlag = 
```
When turned on, the program can scan a folder named "userFiles" in the same directory as the code and appends whatever single cycle .wavs or .syx files you'd like to the end of the generated list. This folder needs to be in the same folder as the python code. These files can be .wav, .syx, or any other audio file type accepted by C6 that has a file extension length of 3 characters (.wav) & can have any naming convention for ordering them, as long as they end in the letters/numbers you want them to show up as on the MnM.
ie: 01tri1.wav" & "02_signaldescription_saw.syx"
will generate: 'tri1.wav' & 'saw.wav' respectively at the end of the chord file list. The program will remove any '_' characters from the last 4 characters of the filename for convenience. 
I ultimately did not end up using this for the final program, but I decied to leave it in in case anyone ever wanted to use this program for something other than single cycle chords. 

```
printGraphsFlag = 
```
#turn this on to generate matplotlib graphs of the waves generated. Useful for debugging new waveform types & program changes. It will generate a plot for each waveform so I don't reccomend having this on for generating more than one waveform type at a time.

### Signal / Chord Generation Controls
```
oscList = [...]
```
This list controls what oscilattors from the "osccillators" class have their chords genereated. Many of these are experimental. The current list is what I ended up going with for the MnM.

```
chords = [...]
```
This list will tell the program the 3-4 letter name of the chord you want to genereate, it's just intonal ratios, adnd the inversion values you wish to generate. See the above section about for the ```genCustomInversions = ``` flag for a full explanation of how these array entries should be formatted.

→

### Sending the Generated Waveforms to Elektron's C6 Software
After the program completes, there will be a folder containing all of the samples in .wav format to send to the monomachine. C6 only uses 4 letter names for each .wav once it send them to a machine, taking the first three and last characters of an input file to use as the display name.

For example:

**Cho**rdSample0**7**.wav would yield → **CHO7** as a display name on the Monomachine for an input waveform (This works the same way for the Machinedrum UW)

While this works well enough as a catchall way to autoname files, you cannot organize the files numerically without the prefix being used to generate a display name for the waveform on the Monomachine. To get around this, the program appends a dummy modified date to each .wav file increased by 1 year per file. This allows you sort your folder by date modifed and drag them into C6 keeping their 4 letter name in an arbitrary. Once the folder is sorted by date modified, you can drag them into C6, convert to DigiPRO and send to your Monomachine.

### Bonus Feature
As a means to test my ideas for single cycle waves, I made it so that the python script will also genererate all of the oscillator types as unison waves, cleanly named in a seperate folder /Unison Waves/. This means this program can essentially be used as a way to quickly generate a custom bank of regular ol monophonic DigiPRO samples. This folder will genereate all functions in the "osccillators" class no matter what and is not dependant on the contents of the ```oscList``` list.

## Features I Couldn't Figure Out How To Impliment:
* Compressing the waveforms a little bit to increase their percieved loudness. This might be something really easy, but I couldn't figure out an elegant way to do this.
* Reverse engineering the DigiPRO format to auto generate and compile the final waveform banks. user [rumblesan](https://gist.github.com/rumblesan/e520ae4099d0583e3ef4e228beabe2b3) did quiet alot of the heavy lifting already revese engineering the file format, but I lack the techncial expertise to fully reverse engineer the waveform encoding.

