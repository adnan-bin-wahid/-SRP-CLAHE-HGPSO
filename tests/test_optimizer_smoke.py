from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_origin

from src.config import load_config
from src.io import load_scene
from src.methods import run_method


def test_proposed_optimizer_smoke(tmp_path):
    h=w=40
    rng=np.random.default_rng(5)
    cube=rng.uniform(0.04,0.35,(h,w,4)).astype(np.float32)
    d=tmp_path/"s001"; d.mkdir()
    profile=dict(driver="GTiff",height=h,width=w,count=1,dtype="uint16",crs="EPSG:32646",transform=from_origin(0,1000,10,10),nodata=0)
    for i,b in enumerate(["B02","B03","B04","B08"]):
        with rasterio.open(d/f"{b}.tif","w",**profile) as ds:
            ds.write((cube[...,i]*10000).astype(np.uint16),1)
    mp=profile.copy(); mp.update(dtype="uint8",nodata=None)
    with rasterio.open(d/"cloud_mask.tif","w",**mp) as ds: ds.write(np.zeros((h,w),np.uint8),1)
    scene=load_scene(d,"test")
    cfg=load_config(Path(__file__).resolve().parents[1]/"configs"/"paper.yaml")
    result=run_method(scene,cfg,"SRP_CLAHE_HGPSO",cfg["presets"]["quick"],123)
    assert result.evaluations_proxy > 0
    assert result.evaluations_full > 0
    assert result.metrics["ndvi_mae"] < 0.005
