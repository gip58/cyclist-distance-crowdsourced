import os
for x in range(0, 21):
    f1 = '../public/videos/video_' + str(x) + '.mp4'
    out = '../public/videos/compressed/video_' + str(x) + '.mp4'
    os.system("ffmpeg -i " + f1 + " -vcodec libx265 -vf scale=1280:720 -crf 20 " + out)