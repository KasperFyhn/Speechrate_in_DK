import os
import glob
import re
import sys

class TextGrid:
    '''A representation of a TextGrid file which loads the different tiers in
    the TextGrid into their respective types. These tiers can be retrieved via
    name from the "items" dictionary.'''
    
    def __init__(self, path):
        self.name = os.path.basename(path).split('.')[0]
        
        raw = open(path, 'r').read()
        items = re.split(r'item \[\d\]:', raw)
        items = [item.split('\n') for item in items[1:]]
        items = [TextTier(item) if '"TextTier"' in item[1] else
                 IntervalTier(item ) if '"IntervalTier"' in item[1] else []
                 for item in items]
        self.items = {item.name: item for item in items}
        
        
class TextTier:
    '''A representation of a TextTier in a TextGrid. All points in the tier are
    loaded into a list of dicts containing mark name/number and times.'''
    
    def __init__(self, lines):
        self.name = lines[2].split('"')[1]
        self.xmin = float(lines[3].split('=')[1].strip())
        self.xmax = float(lines[4].split('=')[1].strip())
        
        raw = '\n'.join(lines)
        points = re.split(r'points \[\d*\]', raw)
        points = [point.split('\n') for point in points[1:]]
        self.points = [{'time': float(point[1].split('=')[1].strip()),
                        'mark': point[2].split('"')[1]}
                       for point in points]
       
class IntervalTier:
    '''A representation of an IntervalTier in a TextGrid. All intervals in the
    tier are loaded into a list of dicts containing the text, start time and
    end time.'''

    def __init__(self, lines):
        self.name = lines[2].split('"')[1]
        self.xmin = float(lines[3].split('=')[1].strip())
        self.xmax = float(lines[4].split('=')[1].strip())

        raw = '\n'.join(lines)
        intervals = re.split(r'intervals \[\d*\]', raw)
        intervals = [interval.split('\n') for interval in intervals[1:]]
        self.intervals = [{'xmin': float(interval[1].split('=')[1].strip()),
                           'xmax': float(interval[2].split('=')[1].strip()),
                           'text': interval[3].split('"')[1]}
                          for interval in intervals]

def dur(interval: dict):
    '''Return the duration of an interval from an IntervalTier.'''
    
    return interval['xmax'] - interval['xmin']

pop_densities = {'BORNHOLM': 68, 'KBH': 6846, 'NAESTV': 122, 'NYB': 115,
                 'SKERN': 39, 'SOEN': 151} # 2016
intra_turn_pause = 1.0

# get the data folder from the user
data = input('Please, provide the folder for the .TextGrid files: ')

# load the .TextGrid files
os.chdir(data)
lefts = sorted(glob.glob('*left.TextGrid'))
rights = sorted(glob.glob('*right.TextGrid'))
if not len(lefts) == len(rights):
    print('WARNING: Non-matching numbers of left and right channels. Exiting.')
    sys.exit()
n_filepairs = len(lefts)

# prepare report file
report = open('../report.csv', 'w+')
print('file,city,popdensity,speaker,gender,turn id,nsyll,npause,dur,'
      + 'phon time,speechrate,articrate,turn start, turn end', file=report)

# iterate over pairs of files
for n, (l_file, r_file) in enumerate(zip(lefts, rights)):
    print(f'\rProcessing file pair {n + 1} of {n_filepairs}', end='')
    
    # make sure that the zipped files are a pair
    l_name = '_'.join(l_file.split('_')[:4])
    r_name = '_'.join(r_file.split('_')[:4])
    if not l_name == r_name:
        print(f'\n{l_file} and {r_file} were loaded zipped but are not a pair.',
              'Skipping to next pair of files.')
        continue
    
    # load grids, point tiers and interval tiers
    grids = {'l': TextGrid(l_file), 'r': TextGrid(r_file)}
    points = {'l': grids['l'].items['syllables'].points,
              'r': grids['r'].items['syllables'].points}
    inters = {'l': grids['l'].items['silences'].intervals,
              'r': grids['r'].items['silences'].intervals}
    
    # remove first interval if silent
    for inter in inters.values():
        if inter[0]['text'] == 'silent': 
            inter.remove(inter[0])
            
    # make a sorted list of sounding intervals with speaker info and number of
    # syllables. Merge silent and silent "sounding" areas
    all_inters = []
    for spkr in ['l', 'r']:
        for inter in inters[spkr]:
            if inter['text'] == 'sounding':
                nsyll = len([point for point in points[spkr]
                             if inter['xmin'] < point['time'] < inter['xmax']])
                if nsyll > 0:
                    inter['nsyll'] = nsyll
                    inter['spkr'] = spkr
                    all_inters.append(inter)
    all_inters = sorted(all_inters, key=lambda inter: inter['xmin'])
    
    # determine first speaker
    if all_inters[0]['spkr'] == 'l':
        spkr = 'l'
        other = 'r'
    elif all_inters[0]['spkr'] == 'r':
        spkr = 'r'
        other = 'l'
    
    # make lists of turns where each turn can contain several utterances
    # and each utterance can contain several intervals
    turns = {'l': [], 'r': []}
    interjected_turns = {'l': [], 'r': []}
    turn = {'l': [[]], 'r': [[]]} # temporary for turns and embedded utterances
    
    for inter in all_inters:
        # determine "owner" of the interval and append to his/her turn
        owner = inter['spkr']
        if turn[owner] == [[]]: # completely empty turn
            turn[owner][-1].append(inter)
        elif inter['xmin'] - turn[owner][-1][-1]['xmax'] > intra_turn_pause:
            turn[owner].append([inter]) # start as new utterance in the turn
        else:
            turn[owner][-1].append(inter)
        
        # if the speech is not from the current speaker and ...
        if owner != spkr:
            # if the new turn extends over the current turn, terminate
            # the current turn, append it to the appropriate turns list and
            # switch speakers
            if turn[spkr][-1][-1]['xmax'] < inter['xmax']:
                turns[spkr].append(turn[spkr])
                turn[spkr] = [[]]
                spkr, other = other, spkr
                    
            # if the new turn does not extend over the current, add it to
            # the owner's list of interjected turns without breaking the
            # current turn
            elif turn[spkr][-1][-1]['xmax'] > inter['xmax']:
                interjected_turns[owner].append(turn[owner])
                turn[owner] = [[]]
    
    for spkr in ['l', 'r']:
        
        # settle basic info on speaker based on file name
        if spkr == 'l':
            file_name = os.path.basename(l_file)
        elif spkr == 'r':
            file_name = os.path.basename(r_file)
        info = file_name.split('_')
        
        city = info[0]
        spkr_id = city + info[1] + spkr
        gender = info[2]
        if spkr == 'l':
            gender = info[2][0]
        elif spkr == 'r':
            gender = info[2][1]
        pop_d = pop_densities[city]

        utterances = [utter
                      for turn in turns[spkr] + interjected_turns[spkr]
                      for utter in turn if not utter == []]

        for i, utter in enumerate(utterances):
            
            # prepare relevant numbers and lists
            start = utter[0]['xmin']
            end = utter[-1]['xmax']

            soundings = [inter for inter in utter
                         if inter['text'] == 'sounding']
            sylls = [point for point in points[spkr]
                     if start < point['time'] < end]
            
            # calculate the numbers to be reported
            nsyll = len(sylls)
            npause = len(soundings) - 1
            utter_dur = end - start
            phon_time = sum(dur(sound) for sound in soundings)
            speech_rate = nsyll / utter_dur
            artic_rate = nsyll / phon_time
            
            if artic_rate != 0:
                print(f'{file_name},{city},{pop_d},{spkr_id},{gender},{i},'
                      + f'{nsyll},{npause},{utter_dur},{phon_time},'
                      + f'{speech_rate},{artic_rate},{start},{end}',
                      file=report)

report.close()