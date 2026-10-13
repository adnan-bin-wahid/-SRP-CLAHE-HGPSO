import pandas as pd
import pytest
from scipy.stats import rankdata

from scripts.analyze_paper_evidence import MAIN_METRICS, PROPOSED, paired_audit


def paired_frame(differences):
    rows = []
    for chip, difference in enumerate(differences):
        for method, value in (("CLAHE", 1.0), (PROPOSED, 1.0 + difference)):
            rows.append({"chip_id": str(chip), "method": method,
                         **{metric: value for metric in MAIN_METRICS}})
    return pd.DataFrame(rows)


def test_identical_pairs_have_neutral_effect_and_pvalue():
    audit = paired_audit(paired_frame([0.0] * 8), "chip_id")
    assert audit.n_pairs.eq(8).all()
    assert audit.n_nonzero.eq(0).all()
    assert audit.rank_biserial_exact_ties.eq(0).all()
    assert audit.p_holm.eq(1).all()
    assert not audit.significant_holm.any()


def test_effect_direction_depends_on_metric():
    audit = paired_audit(paired_frame([0.1] * 8), "chip_id").set_index("metric")
    assert audit.loc["local_rms_contrast", "rank_biserial_exact_ties"] == 1.0
    assert audit.loc["runtime_sec", "rank_biserial_exact_ties"] == -1.0


def test_effect_uses_exact_not_near_ties():
    frame = paired_frame([0.1, -0.10000000001, 0.3, -0.4, 0.5, 0.0])
    pivot = frame.pivot(index="chip_id", columns="method", values="entropy")
    differences = (pivot[PROPOSED] - pivot["CLAHE"]).to_numpy()
    nonzero = differences[differences != 0]
    ranks = rankdata(abs(nonzero), method="average")
    expected = (ranks[nonzero > 0].sum() - ranks[nonzero < 0].sum()) / ranks.sum()
    result = paired_audit(frame, "chip_id").set_index("metric").loc["entropy"]
    assert result.n_pairs == 6
    assert result.n_nonzero == 5
    assert result.rank_biserial_exact_ties == pytest.approx(expected)
    assert result.rank_biserial_exact_ties == pytest.approx(0.2)
