"""Inspect delivery bytes, decode every frame, and extract editorial review sheets."""
import sys
sys.dont_write_bytecode = True
import bootstrap
import hashlib, json, os, struct, subprocess
from pathlib import Path
from PIL import Image, ImageDraw

os.chdir(bootstrap.ROOT)
video=Path('artifacts/video-v2.mp4')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames',
    '-show_streams','-show_format','-of','json',str(video)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video')
a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['codec_name'],v['pix_fmt'],v['width'],v['height'],v['r_frame_rate'])==('h264','yuv420p',1920,1080,'30/1')
assert int(v['nb_read_frames'])==600
assert abs(float(probe['format']['duration'])-20)<1/30
assert a['codec_name']=='aac' and a['channels']==2 and a['sample_rate']=='48000'
assert video.stat().st_size<64*1024**2
with Image.open('artifacts/hero.png') as im:
    assert im.size==(1920,1080) and im.format=='PNG'
raw=video.read_bytes(); pos=0; atoms=[]
while pos+8<=len(raw):
    size,kind=struct.unpack('>I4s',raw[pos:pos+8])
    if size==1:size=struct.unpack('>Q',raw[pos+8:pos+16])[0]
    if size==0:size=len(raw)-pos
    atoms.append({'type':kind.decode('ascii'),'offset':pos,'size':size})
    pos+=size
assert next(x['offset'] for x in atoms if x['type']=='moov')<next(x['offset'] for x in atoms if x['type']=='mdat')
decode=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True,check=True)
assert not decode.stderr.strip(),decode.stderr
old_hash=hashlib.sha256(Path('artifacts/video.mp4').read_bytes()).hexdigest()
assert old_hash=='df5eef512b4ab68f16b53eb4640c03c2aa7dbfe13d66fbce0dea31ed6095dc0f'

dest=Path('test/scratch/v2-encoded-review');dest.mkdir(parents=True,exist_ok=True)
indices=sorted(set(range(0,600,30))|set([599])|
    set(range(117,124))|set(range(267,274))|set(range(417,424))|set(range(493,528)))
selection='+'.join('eq(n\\,%d)'%n for n in indices)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-vf',
    f'select={selection},scale=960:540','-fps_mode','vfr','-q:v','2',str(dest/'frame-%03d.jpg')],check=True)
frames={n:Image.open(dest/f'frame-{i+1:03d}.jpg').copy() for i,n in enumerate(indices)}
def sheet(name,nums,cols=4):
    w,h=480,296
    out=Image.new('RGB',(cols*w,((len(nums)+cols-1)//cols)*h),'#071822')
    d=ImageDraw.Draw(out)
    for i,n in enumerate(nums):
        x=(i%cols)*w;y=(i//cols)*h
        out.paste(frames[n].resize((480,270)),(x,y))
        d.text((x+8,y+275),f'frame {n:03d}   {n/30:05.2f}s',fill='white')
    out.save(dest/(name+'.jpg'),quality=92)
sheet('whole-film',list(range(0,600,30))+[599])
sheet('cuts',[117,118,119,120,121,122,123,267,268,269,270,271,272,273,417,418,419,420,421,422,423])
sheet('oracle-to-hero',list(range(493,528)))
report={'output':str(video),'duration_seconds':float(probe['format']['duration']),
    'width':1920,'height':1080,'fps':'30/1','decoded_video_frames':600,
    'video_codec':v['codec_name'],'pixel_format':v['pix_fmt'],
    'audio_codec':a['codec_name'],'audio_channels':a['channels'],'audio_sample_rate':48000,
    'bytes':video.stat().st_size,'MiB':round(video.stat().st_size/1024**2,3),
    'faststart':True,'atoms':atoms,'full_decode_errors':decode.stderr,
    'sha256':hashlib.sha256(raw).hexdigest(),'v1_unchanged_sha256':old_hash,
    'hero':{'width':1920,'height':1080,'format':'PNG','bytes':Path('artifacts/hero.png').stat().st_size},
    'review_frames_extracted':indices,
    'review_limitations':'No continuous audiovisual playback or auditory perception available. Frames and transition sequences inspected visually; audio measured, not listened to.'}
Path('production/v2/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['duration_seconds','decoded_video_frames','video_codec','audio_codec','bytes','MiB','faststart']},indent=2))
