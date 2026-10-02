"""Pepe2Pepe: The Other Side. Five compositions, 600 frames, offline render.

Original brand artwork is composited intact. Website pixels come exclusively
from hydrated Chromium captures. No website text or balances are reconstructed.
Run from repository root: python production/v2/render.py --preview
                         python production/v2/render.py
"""
import sys
sys.dont_write_bytecode = True
import bootstrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, subprocess, argparse, functools, os

ROOT = bootstrap.ROOT
os.chdir(ROOT)
W, H, FPS, FRAMES = 1920, 1080, 30, 600
A = Path('production/v2/assets')
C = Path('production/v2/captures')
OLD = Path('production/assets')
MINT = '#b4e9d6'
LILAC = '#c8b5ef'
WHITE = '#eef4f2'
MUTED = '#9bafb5'

@functools.lru_cache(maxsize=64)
def font(size, weight=500):
    f = ImageFont.truetype(str(OLD/'interface.ttf'), size)
    f.set_variation_by_axes([weight])
    return f

def text(im, s, x, y, size, color=WHITE, weight=500, anchor='lt'):
    ImageDraw.Draw(im).text((x,y), s, font=font(size,weight), fill=color, anchor=anchor)

def tracked(im, s, x, y, size=20, color=MUTED, spacing=3):
    f=font(size,500); d=ImageDraw.Draw(im)
    for char in s:
        d.text((x,y+size),char,font=f,fill=color,anchor='ls')
        x += d.textlength(char,font=f) + spacing

def ease(p):
    p=max(0,min(1,p))
    return p*p*p*(p*(p*6-15)+10)

environment=Image.open(A/'hero-environment.webp').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
logo=Image.open(OLD/'logo.png').convert('RGBA')
logo=logo.crop(logo.getbbox())

def optical(im, zoom=1, center=(960,540), output=(W,H)):
    ow,oh=output
    cw,ch=ow/zoom,oh/zoom
    cx,cy=center
    return im.transform(output,Image.Transform.EXTENT,(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2),Image.Resampling.BICUBIC)

def paste_art(im, art, center, width, opacity=1):
    h=round(width*art.height/art.width)
    layer=art.resize((round(width),h),Image.Resampling.LANCZOS)
    if opacity<1:
        layer.putalpha(layer.getchannel('A').point(lambda p:round(p*max(0,opacity))))
    im.paste(layer,(round(center[0]-width/2),round(center[1]-h/2)),layer)

def backdrop(p=0, quiet=False):
    im=optical(environment,1+0.008*p,(960+3*p,540-2*p))
    if quiet:
        im=Image.blend(im,Image.new('RGB',(W,H),'#081b24'),.88)
    return im

def hero(t, closing=False, art_opacity=1):
    p=ease(min(t,3.25)/3.25) if not closing else 1
    im=backdrop(p)
    # Large current official two-Pepe mark, unwarped and unpainted.
    paste_art(im,logo,(1492+4*p,532-5*p),690+8*p,art_opacity)
    tracked(im,'OPEN MARKETS. REAL TAKES.',120,168,21,MINT,3)
    if closing:
        text(im,'Take the',114,320,112,WHITE,600)
        text(im,'other side.',114,446,112,MINT,600)
        text(im,'pepe2pepe.fun',120,737,68,WHITE,600)
    else:
        text(im,'A question.',114,320,112,WHITE,600)
        text(im,'Two sides.',114,446,112,MINT,600)
        text(im,'pepe2pepe.fun',120,737,60,WHITE,600)
    ImageDraw.Draw(im).line((120,680,204,680),fill=MINT,width=2)
    text(im,'Fixed odds. Funds on-chain.',120,853,29,MUTED,400)
    return im

def brand_corner(im):
    text(im,'pepe2pepe.fun',112,70,29,MINT,500)
    paste_art(im,logo,(1761,87),95)

def caption(im,s):
    text(im,s,112,916,57,WHITE,500)

captures={}
def capture(name):
    if name not in captures:
        src=Image.open(C/(name+'.webp')).convert('RGB')
        if name=='home-crypto-900':
            # Restore the original coordinate space. Only source rows
            # 1700:2820 are sampled; the blank padding is never on camera.
            # This preserves the original subpixel arithmetic exactly.
            canvas=Image.new('RGB',(1800,3648))
            canvas.paste(src,(0,1700))
            src=canvas
        captures[name]=src
    return captures[name]

def viewport(im,src,box,region):
    x,y,w,h=box
    # Subpixel camera sampling. Captured CSS and all original UI stay intact.
    plane=src.transform((w,h),Image.Transform.EXTENT,region,Image.Resampling.BICUBIC)
    mask=Image.new('L',(w,h),0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),radius=17,fill=255)
    im.paste(plane,(x,y),mask)
    ImageDraw.Draw(im).rounded_rectangle((x,y,x+w-1,y+h-1),radius=17,outline='#2b4952',width=1)

def home(t):
    im=backdrop(1,quiet=True);brand_corner(im)
    src=capture('home-crypto-900')
    p=ease(min(t,1.8)/1.8)
    box=(300,185,1320,651)
    top=1740+180*p
    region=(24,top,1776,top+864)
    viewport(im,src,box,region)
    caption(im,'Your question. Someone else’s take.')
    return im

def market(t):
    im=backdrop(1,quiet=True);brand_corner(im)
    src=capture('market10')
    p=ease(min(t,2.6)/2.6)
    box=(112,182,1696,670)
    left=478+8*p
    top=296+4*p
    width=2360-12*p
    region=(left,top,left+width,top+width*670/1696)
    viewport(im,src,box,region)
    caption(im,'Pick a side. Fixed odds.')
    return im

def oracle(t, art_opacity=1):
    im=backdrop(1)
    tracked(im,'RESEARCH BEFORE RESOLUTION',120,168,21,MINT,2)
    text(im,'Powered by',114,340,91,WHITE,500)
    text(im,'the IMD Oracle.',114,449,91,MINT,500)
    text(im,'Agent research. Operator review.',120,748,28,MUTED,400)
    mark=Image.new('RGBA',(W,H))
    text(mark,'IMD',1498,425,142,WHITE,500,anchor='mt')
    tracked(mark,'O R A C L E',1370,595,24,MINT,2)
    if art_opacity<1:
        mark.putalpha(mark.getchannel('A').point(lambda p:round(p*max(0,art_opacity))))
    im.paste(mark,(0,0),mark)
    return im

@functools.lru_cache(maxsize=5)
def settled(which):
    if which=='opening': return hero(3.9)
    if which=='home': return home(4.9)
    if which=='market': return market(4.9)
    if which=='oracle': return oracle(0)
    return hero(2.9,closing=True)

def frame(n):
    t=n/FPS
    if n<120:
        return hero(t) if n<98 else settled('opening')
    if n<270:
        return home(t-4) if n<174 else settled('home')
    if n<420:
        return market(t-9) if n<348 else settled('market')
    if n<510:
        return settled('oracle') if n<495 else oracle(t-14,art_opacity=1-ease((n-495)/14))
    # Matched right-hand circular anchor. Only artwork dissolves; the left
    # CTA and URL are fully opaque from 17.0. No overlapping website text.
    if n<525:
        p=ease((n-510)/14)
        return hero(t-17,closing=True,art_opacity=p)
    return settled('end')

def preview(hero_output=Path('artifacts/hero.png')):
    dest=Path('test/scratch/v2-preview');dest.mkdir(parents=True,exist_ok=True)
    for n in [0,75,119,120,150,190,269,270,320,390,419,420,465,509,510,524,599]:
        frame(n).save(dest/f'{n:03d}.jpg',quality=94)
    hero_output.parent.mkdir(parents=True,exist_ok=True)
    hero(0).save(hero_output,optimize=True)

def render(output=Path('artifacts/video-v2.mp4'),hero_output=Path('artifacts/hero.png')):
    output.parent.mkdir(parents=True,exist_ok=True)
    hero_output.parent.mkdir(parents=True,exist_ok=True)
    hero(0).save(hero_output,optimize=True)
    cmd=['ffmpeg','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-',
         '-i',str(A/'audio-mix.flac'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','slow',
         '-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-ac','2',
         '-t','20','-movflags','+faststart',str(output)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for n in range(FRAMES):
            p.stdin.write(frame(n).tobytes())
            if n%60==0:print(f'Rendered {n}/{FRAMES}',flush=True)
    finally:p.stdin.close()
    if p.wait()!=0:raise RuntimeError('FFmpeg render failed')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--hero-only',action='store_true')
    parser.add_argument('--output',type=Path,default=Path('artifacts/video-v2.mp4'))
    parser.add_argument('--hero-output',type=Path,default=Path('artifacts/hero.png'))
    args=parser.parse_args()
    if args.hero_only:
        args.hero_output.parent.mkdir(parents=True,exist_ok=True)
        hero(0).save(args.hero_output,optimize=True)
    elif args.preview:preview(args.hero_output)
    else:render(args.output,args.hero_output)
