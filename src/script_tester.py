import os
import glob
import re
import pandas as pd
import seaborn as sns

class TextGrid:
    '''A representation of a TextGrid file which loads the different tiers in
    the TextGrid into their respective types. These tiers can be retrieved via
    name from the "items" dictionary.'''
    
    def __init__(self, path):
        self.name = os.path.basename(path).split('.')[0]
        
        raw = open(path, encoding='UTF-16').read()
        items = re.split(r'item \[\d\]:', raw, flags=re.UNICODE)
        items = [item.split('\n') for item in items[1:]]
        items = [TextTier(item) if '"TextTier"' in item[1] else
                 IntervalTier(item ) if '"IntervalTier"' in item[1] else None
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

# get the data folder from the user
data = input('Please, provide the folder for the .TextGrid files: ')

# load the .TextGrid files
os.chdir(data)
files = glob.glob('*.TextGrid')
grids = [TextGrid(file) for file in files]

intervals = []

for grid in grids:

    # go over transcribed interval and add the values from the corresponding
    # intervals in the other tiers
    transcript_tier = grid.items['transcription'].intervals
    for i, interval in enumerate(transcript_tier):
        
        # if it is not transcribed, skip to the next
        if (interval['text'] == 'sounding' or
            interval['text'] == 'silent' or
            interval['text'] == ''):
            continue
        
        points = grid.items['syllables'].points
        praat_sylls = [point for point in points
                       if interval['xmin'] < point['time'] < interval['xmax']]
        interval['praat sylls'] = len(praat_sylls)
        
        manual_sylls = grid.items['manual count'].intervals[i]['text']
        interval['manual sylls'] = len(manual_sylls)
        
        phonemic_sylls = grid.items['phonemic sylls'].intervals[i]['text']
        interval['phonemic sylls'] = len(phonemic_sylls)
        
        interval['script rate'] = interval['praat sylls'] / dur(interval)
        interval['manual rate'] = interval['manual sylls'] / dur(interval)
        
        intervals.append(interval)

    
    # report number of script sylls, manual sylls, phonemic sylls, duration,
    # script artic rate, manual artic rate, "phonemic artic rate"

df = pd.DataFrame(intervals)

sns.lmplot('manual sylls', 'praat sylls', df)
sns.lmplot('manual rate', 'script rate', df)













