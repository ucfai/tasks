# from moviepy.editor import VideoFileClip, clips_array, vfx, CompositeVideoClip
from moviepy.video.tools.segmenting import findObjects
from moviepy.editor import *

# Load the background image and required video files
img = ImageClip("background.png")
bg = img.set_duration((2,0)) #TODO: Don't hardcode the time
slideshow = VideoFileClip("truckla.mp4")

speaker = slideshow.fx( vfx.mirror_x )
speaker = speaker.resize(0.50)
speaker.set_pos(("right", "top"))

slideshow = slideshow.resize(0.70)

# Store the video images into a list for compositing and find the regions on the background image
clips = [bg, slideshow, speaker]
# regions = findObjects(bg)

# # process the clips and match them to regions in the background
# comp_clips = [c.resize(r.size)
#                 .set_mask(r.mask)
#                 .set_pos(r.screenpos)
#                for c,r in zip(clips,regions)]

# Output the video
video = CompositeVideoClip(clips)
final_video = video.write_videofile("output.mp4")

