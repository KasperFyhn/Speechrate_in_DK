import os
import re
import glob

class TextGrid:
    '''A representation of a TextGrid file which loads the different tiers in
    the TextGrid into their respective types. These tiers can be retrieved via
    name from the "items" dictionary.'''
    
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path).split('.')[0]
        
        self.raw = open(path, 'r').read()
        items = re.split(r'item \[\d\]:', self.raw)
        self.xmin = items[0].split('\n')
        
        items = [item.split('\n') for item in items[1:]]
        items = [TextTier(item) if '"TextTier"' in item[1] else
                 IntervalTier.from_lines(item) if '"IntervalTier"' in item[1]
                 else []
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

    def __init__(self, name, xmin, xmax, intervals):
        self.name = name
        self.xmin = xmin
        self.xmax = xmax
        self.intervals = intervals
        
    @classmethod
    def from_lines(cls, lines):
        name = lines[2].split('"')[1]
        xmin = float(lines[3].split('=')[1].strip())
        xmax = float(lines[4].split('=')[1].strip())

        raw = '\n'.join(lines)
        intervals = re.split(r'intervals \[\d*\]', raw)
        intervals = [interval.split('\n') for interval in intervals[1:]]
        intervals = [{'xmin': float(interval[1].split('=')[1].strip()),
                      'xmax': float(interval[2].split('=')[1].strip()),
                      'text': interval[3].split('"')[1]}
                     for interval in intervals]
        return cls(name, xmin, xmax, intervals)

def append_interval_tier(tier: IntervalTier, textgrid: TextGrid):
    '''Append a tier (TextTier or IntervalTier) to a .TextGrid file.'''
    
    # update the size line
    sz = len(textgrid.items)
    n_sz = sz + 1
    textgrid.raw = textgrid.raw.replace(f'size = {sz}', f'size = {n_sz}',1)
    
    # prepare headerlines
    n_inter = len(tier.intervals)
    header = (f'item[{n_sz}]:\n'
              f'class = "IntervalTier"\n'
              f'name = "{tier.name}"\n'
              f'xmin = {tier.xmin}\n'
              f'xmax = {tier.xmax}\n'
              f'intervals: size = {n_inter}\n')
              
    # prepare intervals
    intervals = []
    for i, inter in enumerate(tier.intervals):
        n = i + 1
        xmin = inter['xmin']
        xmax = inter['xmax']
        text = inter['text']
        s = (f'intervals[{n}]\n'
             f'xmin = {xmin}\n'
             f'xmax = {xmax}\n'
             f'text = "{text}"\n')
        intervals.append(s)
            
    # write to file
    grid_file = open(textgrid.path, 'a+')
    print(header, *intervals, end='', sep='', file=grid_file)
    grid_file.close()
    
def dur(interval: dict):
    '''Return the duration of an interval from an IntervalTier.'''
    
    return interval['xmax'] - interval['xmin']

# get the relevant input from the user
data = input('Please, provide the folder for the .TextGrid files: ')
intra_turn_pause = float(input('Max duration of an intra-turn pause (s): '))

# load the .TextGrid files
os.chdir(data)
files = glob.glob('*.TextGrid')

# prepare report file
report = open('../report.csv', 'w+')

print('file,turn id,nsyll,npause,dur (s),phonation time,' +
      'speechrate (nsyll/dur),articulation rate (nsyll/phonation time),' +
      'turn start, turn end', file=report)

for file in files:
    file_name = file.replace('.TextGrid', '')
    
    grid = TextGrid(file)
    
    # geet the list of syllable points
    points = grid.items['syllables'].points
    
    # make a list of turns where each turn can contain several intervals
    turns = []
    intervals = grid.items['silences'].intervals
    if intervals[0]['text'] == 'silent': # remove first interval if silent
        intervals.remove(intervals[0])
    turn = [] # temporary list to contain a full turn
    for interval in intervals:
        # when an actual pause is encountered, append the full turn to turns
        # and move on to assemble the next turn
        if interval['text'] == 'silent' and dur(interval) > intra_turn_pause:
            turns.append(turn)
            turn = []
        # else, add the interval to the current turn
        else:
            turn.append(interval)
            
    turn_inters = []
    for i, turn in enumerate(turns):
        # prepare some relevant numbers and lists
        start = turn[0]['xmin']
        end = turn[-1]['xmax']
        soundings = [inter for inter in turn if inter['text'] == 'sounding']
        pauses = [inter for inter in turn if inter['text'] == 'silent']
        sylls = [point for point in points if start < point['time'] < end]
        
        # calculate the numbers to be reported
        nsyll = len(sylls)
        npause = len(pauses)
        turn_dur = end - start
        phon_time = sum(dur(sound) for sound in soundings)
        speech_rate = nsyll / turn_dur
        artic_rate = nsyll / phon_time
        
        print(f'{file_name},{i},{nsyll},{npause},{turn_dur:.3},' + 
              f'{phon_time:.3},{speech_rate:.4},{artic_rate:.4},{start},{end}', 
              file=report)
        
        turn_inters.append({'xmin': start, 'xmax': end, 'text': 'turn'})
    
    turn_tier = IntervalTier('turns', 0, grid.items['syllables'].xmax,
                             turn_inters)
    append_interval_tier(turn_tier, grid)

report.close()
