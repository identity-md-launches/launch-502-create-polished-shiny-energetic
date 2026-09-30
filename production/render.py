"""Offline compositor. Uses preserved live captures; never redraws website UI."""
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,math,subprocess,os
from pathlib import Path
W,H=1920,1080
A=Path('production/assets'); C=Path('production/captures')
FF=os.environ.get('FFMPEG','ffmpeg')
fonts={}
def f(size,kind='headline'):
 key=(size,kind)
 if key not in fonts:fonts[key]=ImageFont.truetype(str(A/(kind+'.ttf')),size)
 return fonts[key]
def txt(im,s,xy,size=60,col='#eefcf6',kind='headline',anchor=None):ImageDraw.Draw(im).text(xy,s,font=f(size,kind),fill=col,anchor=anchor)
logo=Image.open(A/'logo.png').convert('RGBA'); logo=logo.crop(logo.getbbox())
face=Image.open(A/'pepe.png').convert('RGBA');face=face.crop(face.getbbox())
shots={n:Image.open(C/(n+'.png')).convert('RGB') for n in ['home','market10','market12','oracle']}
y,x=np.mgrid[0:H,0:W]; g=np.exp(-((x-600)**2/700**2+(y-450)**2/600**2)); g2=np.exp(-((x-1700)**2/600**2+(y-700)**2/500**2))
bg=np.zeros((H,W,3));bg[:,:,0]=5+8*g+16*g2;bg[:,:,1]=15+32*g+8*g2;bg[:,:,2]=26+32*g+24*g2
base=Image.fromarray(bg.astype('uint8'))
def background(t):
 im=base.copy();d=ImageDraw.Draw(im)
 for k in range(10):
  yy=int(110+k*112+12*math.sin(t*.6+k));d.line((0,yy,1920,yy-180),fill=(18,43,54),width=1)
 for k in range(28):
  xx=int((k*211+t*14)%W);yy=int((k*137)%H);d.ellipse((xx,yy,xx+2,yy+2),fill=(70,115,119))
 d.line((80,1014,1840,1014),fill=(44,71,80),width=1)
 d.line((80,1014,80+int(1760*t/15),1014),fill='#a6f2d5',width=3)
 txt(im,'PEPE2PEPE  /  TAKE THE OTHER SIDE',(82,1031),19,'#89abae','mono')
 txt(im,'pepe2pepe.fun',(1838,1031),21,'#b0f0d9','mono',anchor='ra')
 return im

def asset(im,art,box):
 x,y,w,h=box; layer=art.copy();layer.thumbnail((int(w),int(h)),Image.Resampling.LANCZOS)
 im.paste(layer,(int(x+(w-layer.width)/2),int(y+(h-layer.height)/2)),layer)

def panel(im,name,crop,box,p=0,zoom=.025):
 art=shots[name].crop(crop); x,y,w,h=box
 # Slow optical push with preserved aspect ratio and no UI alterations.
 scale=max(w/art.width,h/art.height)*(1+zoom*p)
 art=art.resize((int(art.width*scale),int(art.height*scale)),Image.Resampling.LANCZOS)
 left=(art.width-w)//2;top=(art.height-h)//2
 art=art.crop((left,top,left+w,top+h))
 mask=Image.new('L',(w,h));ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),20,fill=255)
 im.paste(art,(x,y),mask)
 d=ImageDraw.Draw(im);d.rounded_rectangle((x,y,x+w,y+h),20,outline='#42686b',width=2)
 # Traveling reflected highlight along the frame, outside content.
 sx=x+int((w-180)*p);d.line((sx,y,sx+180,y),fill='#b9fce1',width=3)

def caption(im,s,sub=None):
 txt(im,s,(960,880),76,anchor='mt')
 if sub:txt(im,sub,(960,969),25,'#b0cbc9','interface',anchor='mt')
def frame(t):
 im=background(t);d=ImageDraw.Draw(im)
 if t<2.5 or t>=12.5:
  end=t>=12.5;p=(t-12.5)/2.5 if end else t/2.5
  # Artwork is intact; floating depth comes from motion and a halo behind it.
  s=1+.018*math.sin(p*math.pi);yy=110-10*math.sin(p*math.pi)
  asset(im,logo,(76,yy,820*s,800*s))
  txt(im,'PERMISSIONLESS PREDICTION MARKETS',(980,225),23,'#a6eed7','mono')
  if end:
   txt(im,'TAKE THE',(976,308),116);txt(im,'OTHER SIDE.',(976,426),116,'#baf6dc')
  else:
   txt(im,'I BET',(976,293),166);txt(im,'YOU.',(976,458),166,'#baf6dc')
  d.rounded_rectangle((978,690,1835,795),24,fill='#102f39',outline='#70b8a5',width=2)
  txt(im,'pepe2pepe.fun',(1406,708),65,'#edfff6','interface',anchor='mt')
  txt(im,'Your question. Someone else’s take.' if not end else 'Ask it. Fund a side. Make it a market.',(984,837),30,'#b9cbd0','interface')
  # Clean sweep above the logo, never obscuring its wordmark.
  sx=int(90+680*p);d.line((sx,90,sx+100,90),fill='#e0fff4',width=4)
 elif t<3.75:
  p=(t-2.5)/1.25
  txt(im,'01  /  THE MARKET IS YOURS',(85,42),24,'#adf0d7','mono')
  panel(im,'home',(225,70,1430,670),(80,110,1760,730),p)
  caption(im,'Your question. Someone else’s take.','Anyone can create a market. No NFT required.')
 elif t<6:
  p=(t-3.75)/2.25
  txt(im,'02  /  REAL QUESTIONS. REAL SIDES.',(85,42),24,'#adf0d7','mono')
  # Two genuine board cards, maintained as a single captured UI region.
  panel(im,'home',(249,1031,1018,1498),(345,105,1230,739),p,zoom=.008)
  caption(im,'Your question. Someone else’s take.','Live markets  /  Robinhood')
 elif t<7.4:
  p=(t-6)/1.4
  txt(im,'03  /  PICK YOUR POSITION',(85,42),24,'#adf0d7','mono')
  panel(im,'market10',(245,151,1412,623),(80,126,1760,712),p,zoom=.012)
  caption(im,'Pick a side.','Back a side — or take the opposite side.')
 elif t<10:
  p=(t-7.4)/2.6
  txt(im,'IMD ABOVE $10?  /  ROBINHOOD MARKET #10',(85,42),24,'#adf0d7','mono')
  panel(im,'market10',(247,629,1410,1119),(80,105,1760,742),p,zoom=.005)
  # Outline actual Back NO / Take YES controls in captured UI.
  d=ImageDraw.Draw(im);pulse=int(160+70*math.sin(p*math.pi)**2)
  d.rounded_rectangle((1350,280,1795,425),16,outline=(150,pulse,205),width=4)
  caption(im,'Fixed odds. Funded on-chain.','Ethereum or Robinhood  •  First in, first matched')
 elif t<12.5:
  p=(t-10)/2.5
  txt(im,'04  /  RESEARCH BEFORE RESOLUTION',(85,42),24,'#adf0d7','mono')
  panel(im,'oracle',(651,2890,1406,3420),(635,108,1198,737),p,zoom=.007)
  # Clearly editorial swarm motif accompanies the real guide.
  for k in range(7):
   ang=k*2*math.pi/7+t*.13;xx=326+190*math.cos(ang);yy=453+244*math.sin(ang)
   d.line((326,453,int(xx),int(yy)),fill='#396b70',width=2);d.ellipse((xx-9,yy-9,xx+9,yy+9),fill='#bbecd9')
  asset(im,face,(158,285,338,338))
  txt(im,'IMD AGENT SWARM',(327,766),25,'#bcf4dc','mono',anchor='mt')
  caption(im,'Powered by the IMD Oracle.','Agent research. Operator review before settlement.')
 # Brief glossy transition line on beat, no black frames.
 for cut in [2.5,3.75,6,7.4,10,12.5]:
  dt=t-cut
  if 0<=dt<.16:
   xx=int(W*dt/.16);ImageDraw.Draw(im).line((xx,85,xx,990),fill='#c6f8e8',width=5)
 return im
if __name__=='__main__':
 if os.environ.get('PREVIEW'):
  for t in [0,2.9,4.8,6.6,8.5,11,14]:frame(t).save(f'test/scratch/frame-{t}.jpg',quality=94)
 else:
  cmd=[FF,'-y','-v','warning','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','-','-i','production/assets/mix.flac','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t','15','-movflags','+faststart','artifacts/video.mp4']
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  for n in range(450):
   proc.stdin.write(frame(n/30).tobytes())
   if n%60==0:print('frame',n,flush=True)
  proc.stdin.close();assert proc.wait()==0
