import parselmouth as psm
import os
import glob

# get a list of the sound files recursively
data = input('Please, provide the folder for your data: ')
os.chdir(data)
files = glob.glob('**/*.wav', recursive=True)

# make a directory for the extracted mono files
if not os.path.exists('split_channels'):
    os.mkdir('split_channels')

for file in files:
    print('Now processing ' + file + ' ...')
    
    # load the file and extract channels
    sound = psm.Sound(file)
    channels = {'left': sound.extract_left_channel(),
                'right': sound.extract_right_channel()}
    
    # save the channels as mono files
    os.chdir('split_channels')
    file_name = os.path.basename(file)
    file_name = file_name.replace('.WAV', '')
    for ch in channels:
        channels[ch].save(f'{file_name}_{ch}.wav',
                          format=psm.SoundFileFormat.WAV)

    os.chdir(data)