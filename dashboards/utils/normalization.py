import pandas as pd


def minmax_normalize(series: pd.Series) -> pd.Series:
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(0.5, index=series.index)
    return (series - min_val) / (max_val - min_val)


def normalize_monthly(df: pd.DataFrame, value_col: str = "avg_value") -> pd.DataFrame:
    result = df.copy()
    result["normalized"] = result.groupby("pollutant")[value_col].transform(minmax_normalize)
    return result
