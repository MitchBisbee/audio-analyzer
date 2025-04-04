
# JSON Serialization Guide for Django REST Framework

!!! info "Purpose"
    This guide helps you systematically resolve `TypeError: Object of type X is not JSON serializable` when using DRF, dataclasses, numpy, pandas, and matplotlib.

---

## ✅ DRF JSON Supported Types

!!! tip "DRF can automatically serialize these types"

- `dict`
- `list`
- `str`
- `int`
- `float`
- `bool`
- `None`

---

## ⚠️ Non-Serializable Common Types

| Type | Fix |
|------|------|
| `dataclass` | Use `asdict()` |
| `numpy.ndarray` | Use `.tolist()` |
| `pandas.DataFrame` | Use `.to_dict()` |
| `bytes` | Use `.decode()` or `base64.b64encode()` |
| `matplotlib.Figure` | Save as image + encode |

---

## 🔄 Fix Pattern for Dataclass Collections

```python
from dataclasses import asdict

# Correct way to serialize dict of dataclasses
data = { key: asdict(value) for key, value in analyzer.plot_data.items() }

return Response({"plot_data": data})
```

---

## ✅ Recommended Dataclass Serialization

```python
@dataclass
class PlotData:
    x_axis: np.ndarray
    y_axis: np.ndarray

    def to_serializable(self):
        return {
            "x_axis": self.x_axis.tolist(),
            "y_axis": self.y_axis.tolist()
        }
```

---

## 🐛 Debugging Pattern

```python
import json

try:
    json.dumps(data)
    print("✅ JSON OK")
except Exception as e:
    print("❌ JSON Error:", e)
```

---

## ✅ Suggested Production Pattern

> Always encapsulate the serialization inside your domain classes.

```python
class AudioAnalyzer:

    def to_serializable(self):
        return {
            "plot_data": { key: asdict(value) for key, value in self.plot_data.items() },
            "sample_rate": self.sr,
            "file": self.filename
        }
```

---

## ✅ Optional Utility Module `utils/serializers.py`

```python
# utils/serializers.py
from dataclasses import asdict
import numpy as np

def safe_asdict(obj):
    if hasattr(obj, "to_serializable"):
        return obj.to_serializable()
    elif isinstance(obj, dict):
        return {k: safe_asdict(v) for k, v in obj.items()}
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return asdict(obj)
```

Use it like:

```python
from utils.serializers import safe_asdict
return Response(safe_asdict(data))
```

---

## ✅ Notes

!!! warning "Remember"
    - `asdict()` only works on dataclass instances.
    - `tolist()` is needed for numpy arrays.
    - `to_dict()` is needed for pandas DataFrames.
    - Always validate using `json.dumps()` during development.


