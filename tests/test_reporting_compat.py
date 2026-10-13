from pathlib import Path

import pandas as pd

from src.reporting import plot_metric_boxplots


def test_boxplot_api_compatibility(tmp_path: Path):
    df = pd.DataFrame({
        "method": ["CLAHE", "CLAHE", "SRP_CLAHE_HGPSO", "SRP_CLAHE_HGPSO"],
        "entropy": [7.1, 7.2, 7.3, 7.4],
    })
    paths = plot_metric_boxplots(df, ["entropy"], tmp_path)
    assert len(paths) == 1
    assert Path(paths[0]).exists()
