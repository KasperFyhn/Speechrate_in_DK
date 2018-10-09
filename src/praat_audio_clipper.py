import glob
import os
import parselmouth as psm

def get_sounding_clips(sound: psm.Sound):
    '''Return a list of Sound objects of only sounding areas from the passed
    Sound object'''
    
    # get a grid with sounding and silent areas
    grid = psm.praat.call(sound, 'To TextGrid (silences)', 100, 0, -25, 1,
                          0.1, "silent", "sounding")
    # clip the Sound into several shorter according to the grid
    clipped_files = psm.praat.call([sound, grid], 'Extract intervals where', 1,
                               "no", "is equal to", "sounding")
    return clipped_files

# get the data dir and make a list of the .wav files
datadir = input('Please, provide the folder containing data: ')
os.chdir(datadir)
data = glob.glob('*.wav')

# prepare a folder to contain all the clipped files
os.mkdir('clipped_data')

for file in data:
    print('Now processing: ' + file)
    
    # load the file into a Praat Sound object and extract channels
    sound = psm.Sound(file)    
    channels = {'left': sound.extract_left_channel(),
                'right': sound.extract_right_channel()}
    
    # extract clips for both channels
    for ch in channels:
        # prepare to save the clips
        file_name = file.lower().replace('.wav', '')
        os.chdir('clipped_data')
        
        # extract the clips
        clips = get_sounding_clips(channels[ch])

        # if a list is returned, iterate the list and save the files numbered
        if type(clips) == list:
            for i in range(len(clips)):
                clips[i].save(f'{file_name}_{ch}_{i}.wav',
                              format=psm.SoundFileFormat.WAV)
        # if just one clip is returned, just save that one
        else:
            clips.save(file_name + '_1.wav', format=psm.SoundFileFormat.WAV)
            
        os.chdir('..')

