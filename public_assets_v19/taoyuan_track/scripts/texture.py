"""MIT: original synthetic turf colour variation, no source imagery used."""
from PIL import Image,ImageFilter
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];rng=np.random.default_rng(11214072)
a=Image.fromarray(rng.integers(0,255,(24,24),dtype=np.uint8)).resize((512,512),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(5));v=(np.asarray(a).astype(float)-128)/128;fine=rng.normal(0,1,(512,512));base=np.array([113,132,77]);out=np.clip(base[None,None,:]+v[:,:,None]*np.array([13,11,8])+fine[:,:,None]*1.7,0,255).astype('uint8');Image.fromarray(out).save(R/'textures/turf_original.png')
