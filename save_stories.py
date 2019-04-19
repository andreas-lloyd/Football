import sys
import pandas as pd
import json
from pathlib import Path

def loop_csv(stories_loc):
    """
    Wrapper to scan over the location given to find the stories jsons
    """
    # Glob for domain, year, month, day
    json_files = stories_loc.glob('*/*/*/*/*.json')
    stories = []
    for json_file in json_files:
        with json_file.open() as file:
            # If the len is 2 then it means we have the changed
            story = json.load(file)
            if len(story) != 2:
                stories.append(story)
            else:
                stories.extend(story['stories'])
    
    return stories

def save_stories(stories_loc, save_loc):
    """
    Wrapper to get the stories and then save them
    """
    stories = pd.DataFrame(loop_csv(stories_loc))

    if not save_loc.exists():
        save_loc.mkdir(parents = True)

    stories.to_csv(save_loc / 'stories.csv', index = False)

if __name__ == '__main__':
    """
    Feed in two arguments, where the first tells us the root of the data, and the second where we want to save
    """
    STORIES_LOC = Path(sys.argv[1]) / 'Stories'
    SAVE_LOC = Path(sys.argv[2]) / 'Saved_stories'

    save_stories(STORIES_LOC, SAVE_LOC)