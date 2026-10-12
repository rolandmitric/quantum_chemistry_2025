from pathlib import Path
import csv,json
import numpy as np
from PIL import Image
from scipy import ndimage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

folder=Path(__file__).resolve().parent
source_image=folder.parent/'source_panels'/'ce2_2025_spectrum_fig2.png'
img=np.asarray(Image.open(source_image).convert('RGB'))
H,W,_=img.shape
x0,x1=57,834
baseline,common_height=620.,556.
R,G,B=(img[:,:,i] for i in range(3))
red=(R>180)&(G<125)&(B<125)&((R.astype(float)-G)>100)&((R.astype(float)-B)>100)
black=(R<85)&(G<85)&(B<85)
allowed=np.zeros((H,W),bool)
allowed[50:620,61:835]=True
allowed[:375,:390]=False
red &= allowed
black &= allowed
black[615:,:]=False  # main trace cannot be separated from the black x-axis here
# The broadened red trace has horizontal thickness; isolated narrow red sticks do not.
red=ndimage.binary_opening(red,structure=np.ones((1,3),bool))
# Avoid axis boundary and remaining antialias fragments when selecting the black curve.
black=ndimage.binary_opening(black,structure=np.ones((1,2),bool))

def extract(mask):
 y=np.full(W,np.nan)
 for x in range(x0,x1+1):
  ys=np.flatnonzero(mask[:,x])
  if not len(ys):continue
  groups=np.split(ys,np.flatnonzero(np.diff(ys)>1)+1)
  groups=[g for g in groups if len(g)>=2]
  if not groups:continue
  # Highest connected run is the main trace; baseline bars are below it.
  g=min(groups,key=lambda a:a[0])
  y[x]=float(np.median(g))
 return y

yexp,ysim=extract(black),extract(red)
xs=np.arange(x0,x1+1)
energy=(xs-x0)*1.2/(x1-x0)
iexp=(baseline-yexp[xs])/common_height
isim=(baseline-ysim[xs])/common_height
# Outlier QA only: identify large jumps, never replace, smooth, or interpolate them.
for name,ys in [('experiment',yexp[xs]),('simulation',ysim[xs])]:
 jumps=np.flatnonzero(np.isfinite(ys[:-1])&np.isfinite(ys[1:])&(np.abs(np.diff(ys))>25))
 print(name,'valid',int(np.isfinite(ys).sum()),'jump_columns',xs[jumps].tolist(),'minmax',float(np.nanmin(ys)),float(np.nanmax(ys)))

csvpath=folder/'spectrum_digitized.csv'
with csvpath.open('w',newline='') as f:
 writer=csv.writer(f)
 writer.writerow(['x_pixel','eBE_eV','experiment_y_pixel','experiment_relative','simulation_y_pixel','simulation_relative','experiment_status','simulation_status'])
 for k,x in enumerate(xs):
  def fmt(a):return '' if not np.isfinite(a) else f'{a:.8f}'
  writer.writerow([x,fmt(energy[k]),fmt(yexp[x]),fmt(iexp[k]),fmt(ysim[x]),fmt(isim[k]),'digitized' if np.isfinite(yexp[x]) else 'unresolved_or_occluded','digitized' if np.isfinite(ysim[x]) else 'unresolved_or_occluded'])

fig,ax=plt.subplots(figsize=(12,10),dpi=130)
ax.imshow(img)
ax.scatter(xs[::5],yexp[xs[::5]],s=10,c='#00b6db',label='Extracted experiment centers',zorder=4)
ax.scatter(xs[::5],ysim[xs[::5]],s=10,c='#7b22bd',label='Extracted simulation centers',zorder=4)
ax.axhline(baseline,color='#21a16b',lw=.8,ls='--')
ax.set_xlim(45,845);ax.set_ylim(650,35)
ax.legend(loc='upper left',bbox_to_anchor=(.05,.16),fontsize=9)
ax.set_title('Digitization QA: point centers over the original Figure 2 raster',fontsize=13)
fig.tight_layout();fig.savefig(folder/'ce2-spectrum-digitization-overlay.png');plt.close(fig)

fig,ax=plt.subplots(figsize=(8.1,4.8),dpi=180)
ax.plot(energy,iexp,color='black',lw=1.7,label='Experiment (digitized)')
ax.plot(energy,isim,color='#e53924',lw=1.9,label='SO-CASSCF simulation (digitized; shifted −0.24 eV)')
ax.set_xlim(0,1.2);ax.set_ylim(0,1.05)
ax.set_xlabel('Electron binding energy / eV');ax.set_ylabel('Relative photoelectron intensity')
ax.spines[['right','top']].set_visible(False)
ax.legend(frameon=False,fontsize=8,loc='upper left')
fig.tight_layout();fig.savefig(folder/'ce2-spectrum-digitized-preview.png');plt.close(fig)

meta={
 'source':'Published Figure 2 raster, ce2-fig2-original.png, from Jin et al., JACS 2025, DOI 10.1021/jacs.5c07348',
 'data_status':'Digitized curve centers from a published figure; not raw instrument measurements or original simulation output.',
 'shape_pixels':[W,H],
 'x_calibration':{'pixel_57_eV':0.,'pixel_834_eV':1.2,'eV_per_pixel':1.2/777},
 'intensity_calibration':'Both traces use I=(620-y_pixel)/556, with no independent normalization, fitting, smoothing, energy shifts or missing-value interpolation.',
 'simulation_shift':'The source figure already includes the published -0.24 eV SO-CASSCF energy shift. No additional shift applied.',
 'mask':'Inset and legend excluded: x<390,y<375. Black x-axis excluded: y>=615. Red sticks removed by 3-pixel horizontal binary opening.',
 'missing_values':'Unresolved or occluded curve centers are blank. The experimental baseline at low energy merges with the black x-axis and is not assigned an inferred value.',
 'nominal_pixel_resolution_eV':1.2/777,
 'estimated_line_center_uncertainty_pixels':2.5,
 'estimated_energy_uncertainty_eV':2.5*1.2/777,
 'estimated_intensity_uncertainty':2.5/556,
 'limitations':'Uncertainty is an estimated raster-reading precision, not an experimental error bar. Neighboring pixel samples are correlated. Thick-curve upper/lower overlap and raster antialiasing may increase local uncertainty; full source figure retained for QA.'
}
(folder/'ce2-spectrum-digitization-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
print(csvpath)
