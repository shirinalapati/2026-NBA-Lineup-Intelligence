import pandas as pd

from data_pipeline.scoring import compute_uls_for_dataframe, invert_for_defense, normalize_0_100, winsorize_series


def test_winsorize_clip():
    s = pd.Series([0, 1, 2, 100, 200])
    w = winsorize_series(s, low=0.2, high=0.8)
    lo, hi = s.quantile(0.2), s.quantile(0.8)
    assert w.min() >= lo
    assert w.max() <= hi


def test_normalize_range():
    s = pd.Series([0.0, 10.0, 20.0])
    n = normalize_0_100(s)
    assert n.min() == 0.0
    assert n.max() == 100.0


def test_invert_defense():
    s = pd.Series([108.0, 112.0])
    inv = invert_for_defense(s)
    assert inv.iloc[0] == -108.0


def test_uls_finite():
    """ULS is defined only for lineups at or above ULS_MIN_MINUTES (min–max norms on that eligible set)."""
    df = pd.DataFrame(
        {
            "net_rating": [5.0, 3.0, -1.0],
            "offensive_rating": [115.0, 112.0, 108.0],
            "defensive_rating": [110.0, 111.0, 113.0],
            "minutes": [120.0, 110.0, 200.0],
            "possessions": [300.0, 220.0, 400.0],
        }
    )
    u = compute_uls_for_dataframe(df)
    assert len(u) == 3
    assert u.notna().all()


def test_uls_coerces_string_ratings():
    """SQLite / CSV can return object dtypes; ULS should still compute."""
    df = pd.DataFrame(
        {
            "net_rating": ["5.0", "3.0"],
            "offensive_rating": ["115.0", "112.0"],
            "defensive_rating": ["110.0", "111.0"],
            "minutes": ["120.0", "110.0"],
            "possessions": ["300.0", "220.0"],
        }
    )
    u = compute_uls_for_dataframe(df)
    assert u.notna().all()


def test_uls_nan_when_below_minutes_floor():
    df = pd.DataFrame(
        {
            "net_rating": [5.0],
            "offensive_rating": [115.0],
            "defensive_rating": [110.0],
            "minutes": [40.0],
            "possessions": [200.0],
        }
    )
    u = compute_uls_for_dataframe(df)
    assert u.isna().all()
