import asyncio,subprocess,wave
from pathlib import Path
import numpy as np
import edge_tts
FF='/tmp/ffmpeg-7.0.2-amd64-static/ffmpeg'
SR=48000
parts=[('I bet you.',0.25,1.65),('Your question. Someone else’s take.',2.5,3.2),('Pick a side.',6,1.15),('Fixed odds. Funded on-chain.',7.35,2.4),('Powered by the IMD Oracle.',10,2.35),('Pepe to Pepe. Take the other side.',12.55,2.35)]
async def voices():
 for i,(s,_,_) in enumerate(parts):
  await edge_tts.Communicate(s,'en-US-GuyNeural',rate='+10%').save(f'production/assets/vo{i}.mp3')
asyncio.run(voices())
a=np.zeros(SR*15); rng=np.random.default_rng(23)
t=np.arange(len(a))/SR
# Original 120 BPM electro: sidechained arpeggio, sub bass, kick, clap and hats.
for k in range(30):
 start=int(k*.5*SR); q=np.arange(min(int(.45*SR),len(a)-start))/SR
 kick=np.sin(2*np.pi*(46*q+65*.035*(1-np.exp(-q/.035))))*np.exp(-q*12)
 a[start:start+len(q)]+=.23*kick
 if k%2:
  clap=rng.normal(0,1,len(q))*np.exp(-q*35); a[start:start+len(q)]+=.035*clap
for k in range(120):
 start=int(k*.125*SR); q=np.arange(min(int(.1*SR),len(a)-start))/SR
 noise=rng.normal(0,1,len(q)); noise=np.r_[0,np.diff(noise)]
 a[start:start+len(q)]+=.008*noise*np.exp(-q*65)
notes=[57,64,69,72,57,64,67,71]
for k in range(60):
 start=int(k*.25*SR); q=np.arange(min(int(.4*SR),len(a)-start))/SR
 hz=440*2**((notes[k%8]-69)/12)
 env=(1-np.exp(-q*100))*np.exp(-q*10)
 a[start:start+len(q)]+=.045*(np.sin(2*np.pi*hz*q)+.3*np.sin(4*np.pi*hz*q))*env
for startsec in [0,2.5,3.75,6,7.5,10,12.5]:
 start=int(startsec*SR); q=np.arange(min(int(.45*SR),len(a)-start))/SR
 a[start:start+len(q)]+=.025*rng.normal(0,1,len(q))*np.exp(-q*10)
# Taper music end; original composition contains no samples.
a*=np.minimum(1,(15-t)/.4)
voice=np.zeros_like(a)
for i,(_,start,dur) in enumerate(parts):
 raw=subprocess.check_output([FF,'-v','error','-i',f'production/assets/vo{i}.mp3','-f','f32le','-ac','1','-ar',str(SR),'-'])
 v=np.frombuffer(raw,dtype=np.float32); nz=np.where(np.abs(v)>.006)[0];v=v[max(0,nz[0]-1000):min(len(v),nz[-1]+1800)]
 if len(v)>dur*SR: v=np.interp(np.linspace(0,len(v)-1,int(dur*SR)),np.arange(len(v)),v)
 n=int(start*SR);voice[n:n+len(v)]+=v*.9
mix=a+voice;mix*=.91/max(1,np.max(np.abs(mix)))
stereo=np.stack([mix,mix],1)
with wave.open('production/assets/mix.wav','wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((stereo*32767).astype('<i2').tobytes())
print('Audio peak',np.max(np.abs(mix)))
