from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_origin

from src.config import load_config
from src.io import load_scene
from src.methods import run_method


def _write_scene(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    h=w=48
    rng=np.random.default_rng(4)
    cube=rng.uniform(0.05,0.4,size=(h,w,4)).astype(np.float32)
    profile=dict(driver="GTiff",height=h,width=w,count=1,dtype="uint16",crs="EPSG:32646",transform=from_origin(0,1000,10,10),nodata=0)
    for i,b in enumerate(["B02","B03","B04","B08"]):
        with rasterio.open(root/f"{b}.tif","w",**profile) as ds:
            ds.write(np.round(cube[...,i]*10000).astype(np.uint16),1)
    mp=profile.copy(); mp.update(dtype="uint8",nodata=None)
    with rasterio.open(root/"cloud_mask.tif","w",**mp) as ds:
        ds.write(np.zeros((h,w),dtype=np.uint8),1)


def test_load_auto_scale_and_run_common_gain(tmp_path):
    d=tmp_path/"x001"; _write_scene(d)
    scene=load_scene(d,"test",reflectance_scale="auto")
    assert scene.scale_used == 10000.0
    cfg=load_config(Path(__file__).resolve().parents[1]/"configs"/"paper.yaml")
    preset=cfg["presets"]["quick"]
    result=run_method(scene,cfg,"CommonGain_CLAHE",preset,123)
    assert result.metrics["ndvi_mae"] < 1e-5
    assert result.metrics["sam_mean_deg"] < 1e-4
