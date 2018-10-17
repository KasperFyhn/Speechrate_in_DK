import glob
import os
import parselmouth as psm

def get_sounding_clips(sound: psm.Sound):
    '''Return a list of Sound objects of only sounding areas from the passed
    Sound object'''
    
    # get a grid with sounding and silent areas
    grid = psm.praat.call(sound, 'To TextGrid (silences)', 100, 0, -35, 0.5,
                          0.05, "silent", "sounding")
    
    # clip the Sound into several shorter clips according to the grid
    clipped_files = psm.praat.call([sound, grid], 'Extract intervals where', 1,
                                   "no", "is equal to", "sounding")

    return clipped_files

def concatenate_short_clips(clips: list, clip_time: float):
    '''Return a list of clips with durations no shorter than the specified clip
    time where each clip is a concatenation of consecutive clips shorter than 
    the specified clip time.'''
    
    conc_clips = [] # list for the final concatenated clips
    
    # prepare "tracking" variables to be used in the loop
    short_clips = []
    conc_dur = 0
    
    # loop through each clip and concatenate short clips into longer ones
    for clip in clips:
        dur = clip.get_total_duration()
        
        # if the clip is longer than clip time, append it to the final list
        if dur > clip_time:
            conc_clips.append(clip)  
            
        # if it is shorter, append it to the short clips list
        elif dur < clip_time:
            short_clips.append(clip)
            conc_dur += dur
            
            # when the duration of the short clips exceed the clip time,
            # concatenate the clips, add it to the final list and reset
            # tracking variables
            if conc_dur > clip_time:
                conc_clip = psm.Sound.concatenate(short_clips)
                conc_clips.append(conc_clip)
                short_clips = []
                conc_dur = 0
            
    return conc_clips

# get the data dir and make a list of the .wav files
datadir = input('Please, provide the folder containing data: ')
os.chdir(datadir)
data = glob.glob('*.wav')

# prepare a folder to contain all the clipped files
if not os.path.exists('clipped_data'):
    os.mkdir('clipped_data')

for file in data:
    print('Now processing: ' + file + ' ...', flush=True)
    
    # load the file into a Praat Sound object and extract channels
    print('\tLoading file ...', flush=True)
    sound = psm.Sound(file)   
    print('\tExtracting channels ...', flush=True)
    channels = {'left': sound.extract_left_channel(),
                'right': sound.extract_right_channel()}
    
    for ch in channels:
        # extract the clips
        print(f'\tExtracting sounding clips from {ch} channel ...', flush=True)
        clips = get_sounding_clips(channels[ch])
        
        # concatenate short clips
        if type(clips) == list:
            print('\tConcatenating short clips ...', flush=True)
            clips = concatenate_short_clips(clips, 5)

        # prepare to save the clips
        file_name = file.lower().replace('.wav', '')
        os.chdir('clipped_data')
        
        # if a list is returned, iterate the list and save the files numbered
        print('\tSaving clips ...', flush=True)
        if type(clips) == list:
            for i, clip in enumerate(clips):
                clip.save(f'{file_name}_{ch}_{i}.wav',
                          format=psm.SoundFileFormat.WAV)
        # if just one clip is returned, just save that one
        else:
            clips.save(file_name + '_1.wav', format=psm.SoundFileFormat.WAV)
            
        os.chdir('..')

