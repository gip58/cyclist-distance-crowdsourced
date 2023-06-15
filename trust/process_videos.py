# by Pavlo Bazilinskyy <pavlo.bazilinskyy@gmail.com>

import os
import pandas as pd

# read mapping csv
df = pd.read_csv('process_videos_info.csv')

for index, row in df.iterrows():
    unity_file = '../public/videos/' + row['unity_file']
    out_file = '../public/videos/compressed/' + row['video_file']
    cmd = "ffmpeg -i " + unity_file + \
          " -vcodec libx265 -vf " + \
          "scale=1280:720 " + \
          "-ss " + str(row['start']) + \
          " -t " + str(row['end']) + \
          " -crf 20 " + \
          out_file
    print(cmd)
    os.system(cmd)
