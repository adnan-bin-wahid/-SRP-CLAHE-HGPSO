from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin


def make_scene(seed: int, h=96, w=96):
    rng=np.random.default_rng(seed)
    y,x=np.mgrid[0:h,0:w]
    veg=np.exp(-((x-0.3*w)**2+(y-0.45*h)**2)/(2*(0.22*w)**2))
    water=np.exp(-((x-0.75*w)**2+(y-0.35*h)**2)/(2*(0.16*w)**2))
    texture=0.03*np.sin(x/5)+0.02*np.cos(y/7)
    B=0.10+0.05*veg+0.10*water+texture
    G=0.13+0.15*veg+0.08*water+texture
    R=0.12+0.08*veg+0.05*water+texture
    N=0.16+0.38*veg+0.02*water+texture
    cube=np.stack([B,G,R,N],-1)+rng.normal(0,0.006,(h,w,4))
    cube=np.clip(cube,0.01,0.9)
    cloud=np.zeros((h,w),np.uint8)
    if seed%3==0:
        cloud[5:10,5:14]=1
    return cube, cloud


def write_scene(root: Path, split: str, chip: str, seed: int):
    cube, cloud=make_scene(seed)
    d=root/split/chip; d.mkdir(parents=True,exist_ok=True)
    transform=from_origin(500000,3000000,10,10)
    profile=dict(driver="GTiff",height=cube.shape[0],width=cube.shape[1],count=1,dtype="uint16",crs="EPSG:32646",transform=transform,nodata=0,compress="deflate")
    for i,b in enumerate(["B02","B03","B04","B08"]):
        with rasterio.open(d/f"{b}.tif","w",**profile) as ds:
            ds.write(np.round(cube[...,i]*10000).astype(np.uint16),1)
    p2=profile.copy(); p2.update(dtype="uint8",nodata=None)
    with rasterio.open(d/"cloud_mask.tif","w",**p2) as ds:
        ds.write(cloud,1)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",default="data/demo_dataset"); args=ap.parse_args()
    root=Path(args.output); root.mkdir(parents=True,exist_ok=True)
    rows=[]
    for split,n in [("validation",4),("test",6)]:
        for i in range(n):
            chip=f"{split[:1]}{i:03d}"; seed=1000+i+(0 if split=="validation" else 100)
            write_scene(root,split,chip,seed)
            rows.append({"chip_id":chip,"split":split,"location":f"LOC_{split}_{i}","datetime":"2020-01-01T00:00:00","cloud_fraction":0.0})
    pd.DataFrame(rows).to_csv(root/"dataset_manifest.csv",index=False)
    print("Demo dataset created:",root.resolve())

if __name__=="__main__": main()
