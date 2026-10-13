from scripts.build_overleaf_package import mean_sd, science


def test_table_unit_scaling_is_explicit():
    row = {"ndvi_mae_mean": 1.948191306367707e-5, "ndvi_mae_std": 9.940395156651963e-5}
    assert mean_sd(row, "ndvi_mae", scale=1000, digits=4) == "$0.0195 \\pm 0.0994$"


def test_pvalue_latex_uses_balanced_exponent():
    assert science(1.108064560245322e-30) == "$1.11\\times10^{-30}$"
    assert science(0.7427409575850745) == "$0.7427$"
