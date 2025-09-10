
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Union
import numpy as np
import pandas as pd

@dataclass
class ScoringParams:
    # Prior mean for ratings. If None, computed as weighted global mean by counts.
    C: Optional[float] = None
    # Prior strength ("m" pseudo-count). If None, use median count (robust) or a provided value.
    m: Optional[float] = None
    # Alternative to fixed m: if m is None and m_method="p50", use median count;
    # if "p75", use 75th percentile; if "fixed", require m.
    m_method: str = "p50"  # options: "p50", "p75", "fixed"
    # Age handling
    today: Optional[Union[str, pd.Timestamp]] = None  # override current date (ISO8601 or Timestamp) for reproducibility
    min_age_years: float = 1/12  # avoid division by ~0 for brand-new apps (default 1 month)
    # Engagement factor based on reviews per year
    alpha: float = 0.25  # how strongly to weight engagement vs. rating (0=no effect, 1=linear)
    lower_cap: float = 0.5  # clamp engagement index to avoid runaway effects
    upper_cap: float = 1.5

def _to_timestamp(x):
    if isinstance(x, pd.Timestamp):
        return x
    if isinstance(x, str):
        try:
            return pd.to_datetime(x, utc=True)
        except Exception:
            return pd.NaT
    return pd.to_datetime(x, utc=True, errors="coerce")

def score_apps(
    df: pd.DataFrame,
    rating_col: str = "average_user_rating",
    count_col: str = "user_rating_count",
    release_col: str = "release_date",
    params: Optional[ScoringParams] = None,
) -> pd.DataFrame:
    """
    Compute a comparison score for App Store games that accounts for:
      1) average rating (quality),
      2) number of ratings (evidence reliability) via a Bayesian shrinkage mean,
      3) age of the app via an engagement factor based on reviews per year.

    Formulae
    --------
    Bayesian/shrinkage mean (posterior expected rating):
        bayes_mean = (v/(v+m))*R + (m/(v+m))*C
      where R = app's average rating, v = rating count,
            C = prior/global mean, m = prior strength ("pseudo-count").

    Reviews-per-year:
        rpy = v / max(age_years, min_age_years)

    Engagement index (dimensionless, centered around 1):
        EI = clip((rpy / median_rpy) ** alpha, lower_cap, upper_cap)

    Final score:
        score = bayes_mean * EI

    Parameters
    ----------
    df : DataFrame containing at least the three columns named above.
    rating_col, count_col, release_col : column names to use.
    params : ScoringParams to tune behavior. Reasonable defaults provided.

    Returns
    -------
    A copy of df with added columns:
      - age_years
      - bayes_mean
      - reviews_per_year
      - engagement_index
      - score
    """
    if params is None:
        params = ScoringParams()

    out = df.copy()

    # Parse dates and compute age in years
    today_ts = (
        pd.to_datetime(params.today, utc=True)
        if params.today is not None
        else pd.Timestamp.utcnow()
    )

    rel = out[release_col].apply(_to_timestamp)
    age_days = (today_ts - rel).dt.total_seconds() / (60 * 60 * 24)
    age_years = age_days / 365.25
    # Handle negative/NaT ages gracefully
    age_years = age_years.fillna(params.min_age_years).clip(lower=params.min_age_years)

    out["age_years"] = age_years

    # Coerce numeric
    R = pd.to_numeric(out[rating_col], errors="coerce")
    v = pd.to_numeric(out[count_col], errors="coerce").fillna(0).clip(lower=0)

    # Prior mean C (weighted global mean by counts unless overridden)
    if params.C is None:
        # Weighted by v so high-v apps influence prior appropriately
        total_votes = v.sum()
        if total_votes > 0:
            C = (R.fillna(0) * v).sum() / total_votes
        else:
            # Fallback to simple mean if counts are all zero
            C = R.mean(skipna=True)
    else:
        C = float(params.C)

    # Prior strength m
    if params.m is not None:
        m = float(params.m)
    else:
        if params.m_method == "p75":
            m = float(np.nanpercentile(v, 75)) if np.isfinite(np.nanpercentile(v, 75)) else 100.0
        else:  # default p50 (median)
            med = np.nanmedian(v)
            m = float(med if np.isfinite(med) and med > 0 else 100.0)
        if m <= 0:
            m = 100.0

    # Bayesian mean
    denom = (v + m)
    bayes_mean = (v / denom) * R + (m / denom) * C
    out["bayes_mean"] = bayes_mean

    # Reviews per year & engagement index
    rpy = v / age_years.replace(0, params.min_age_years)
    out["reviews_per_year"] = rpy

    median_rpy = np.nanmedian(rpy[rpy > 0]) if (rpy > 0).any() else 1.0
    ratio = (rpy / (median_rpy if median_rpy > 0 else 1.0)).replace([np.inf, -np.inf], np.nan).fillna(1.0)
    EI = np.power(ratio, params.alpha).clip(lower=params.lower_cap, upper=params.upper_cap)
    out["engagement_index"] = EI

    # Final score
    out["score"] = out["bayes_mean"] * out["engagement_index"]

    # Useful metadata
    out.attrs["prior_mean_C"] = C
    out.attrs["prior_strength_m"] = m
    out.attrs["median_reviews_per_year"] = median_rpy
    out.attrs["alpha"] = params.alpha

    return out
