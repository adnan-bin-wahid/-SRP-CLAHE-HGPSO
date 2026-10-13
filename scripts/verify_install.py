from __future__ import annotations
import importlib, platform, sys
mods = ["numpy","pandas","cv2","scipy","skimage","matplotlib","rasterio","psutil","yaml","PIL","tqdm","tabulate","jinja2"]
print("Python:", sys.version)
print("Platform:", platform.platform())
failed=[]
for m in mods:
    try:
        mod=importlib.import_module(m)
        print(f"[OK] {m}", getattr(mod,"__version__",""))
    except Exception as e:
        print(f"[FAIL] {m}: {e}"); failed.append(m)
if failed:
    raise SystemExit(1)
print("Installation verification PASSED")
