# by Pavlo Bazilinskyy <pavlo.bazilinskyy@gmail.com>

import os
import pandas as pd
import trust as tr

# Read mapping csv
df = pd.read_csv('process_videos_info.csv')
# black file to be added in the beginning of the stimuli
black_file = os.path.join(tr.common.get_configs('path_source'),
                          'black_video.mp4')
# go over all stimuli
for index, row in df.iterrows():
    in_file = os.path.join(tr.common.get_configs('path_source'), row['in'])
    out_file = os.path.join(tr.common.get_configs('path_stimuli'), row['out'])
    # Using FFmpeg command to process video and compress audio
    os.system("ffmpeg -r 60" +
              " -ss " + str(row['start']) +
              " -to " + str(row['end']) +
              " -i " + in_file +
              " -c:v libx264 -crf 23 -profile:v baseline -level 3.0 -pix_fmt yuv420p" +  # noqa: E501
              " -c:a aac -b:a 32k" +
              " -vf scale=1280:720" +
              " -movflags faststart" +
              " -crf 24 " +
              out_file)
    # Using FFmpeg command to add 1 sec of black in the beginning
    # # based on https://stackoverflow.com/a/22688066/46687
    # os.system("ls " + black_file + " " + out_file + " |" +
    #           "perl -ne 'print \"file $_\"' |"
    #           "ffmpeg -f concat -i - -c copy " + out_file)
    # based on https://stackoverflow.com/a/22958746/46687
    os.system("ffmpeg -i " + black_file +
              " -i " + out_file +
              " -filter_complex \"concat=n=2:v=0:a=1\" -vn -y " +
              out_file)
