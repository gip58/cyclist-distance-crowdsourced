# by Pavlo Bazilinskyy <pavlo.bazilinskyy@gmail.com>

import os
import pandas as pd
import trust as tr


# read mapping csv
df = pd.read_csv('process_videos_info.csv')

for index, row in df.iterrows():
    in_file = os.path.join(tr.common.get_configs('source_video_files'), row['in'])
    out_file = os.path.join(tr.settings.root_dir, 'public', 'videos', row['out'])
    os.system("ffmpeg -i " + in_file +
              " -vcodec libx265 -vf " +
              "scale=1280:720 " +
              "-ss " + str(row['start']) +
              " -t " + str(row['end']) +
              " -crf 20 " +
              out_file)
