# by Pavlo Bazilinskyy <pavlo.bazilinskyy@gmail.com>

import os
import pandas as pd
import trust as tr

# Read mapping csv
df = pd.read_csv('process_videos_info.csv')

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
              " -vf scale=1080:720" +
              " -movflags faststart" +
              " -crf 24 " +
              out_file)
