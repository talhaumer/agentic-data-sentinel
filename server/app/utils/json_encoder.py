"""Custom JSON encoder for handling NumPy and Pandas types."""

import numpy as np
import pandas as pd
from typing import Any
from fastapi.encoders import jsonable_encoder


def numpy_encoder(obj: Any) -> Any:
    """Custom encoder for NumPy and Pandas types."""
    if isinstance(obj, (np.integer, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.bool_, np.bool8)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    elif isinstance(obj, pd.Series):
        return obj.to_list()
    elif isinstance(obj, (pd.Timestamp, pd.DatetimeIndex)):
        return str(obj)
    elif hasattr(obj, 'item'):  # Handle other numpy scalars
        return obj.item()
    elif pd.isna(obj):
        return None
    else:
        return str(obj)


def custom_jsonable_encoder(obj: Any) -> Any:
    """Enhanced jsonable_encoder with NumPy/Pandas support."""
    return jsonable_encoder(
        obj,
        custom_encoder={
            np.int8: int,
            np.int16: int,
            np.int32: int,
            np.int64: int,
            np.uint8: int,
            np.uint16: int,
            np.uint32: int,
            np.uint64: int,
            np.float16: float,
            np.float32: float,
            np.float64: float,
            np.bool_: bool,
            np.ndarray: lambda x: x.tolist(),
            pd.DataFrame: lambda x: x.to_dict(orient="records"),
            pd.Series: lambda x: x.to_list(),
        },
        exclude_none=True
    )
