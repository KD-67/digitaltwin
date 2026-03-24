# Analysis Strategy: Normalization & Multi-Marker Ensemble Scoring

This document records a design discussion about how to normalize biomarker measurements into a common health score (h-score) and how to eventually combine multiple markers into ensemble scores. It covers the current implementation's limitations, proposed solutions, and trade-offs between approaches.

---

## 1. Current Implementation and Its Limitations

The current normalization function is:

```python
def normalize(raw: float, mid: float, half_range: float) -> float:
    return 1.0 - abs(raw - mid) / half_range
```

Where `mid` and `half_range` are derived from `healthy_min` and `healthy_max`:

```python
mid = (healthy_min + healthy_max) / 2.0
half_range = (healthy_max - healthy_min) / 2.0
```

This produces:
- `1.0` at the center of the healthy range
- `0.0` at the healthy boundary edges
- Unbounded negative values as you move further from the healthy center

**The core problem:** The chart Y-axis spans `[-1, 1]`, but nothing in the math assigns a specific physiological meaning to `-1`. It is just where the SVG viewport ends. A value of `-3` or `-10` is valid output from this formula — it simply renders off-screen.

---

## 2. The Asymmetry Problem

When healthy limits are not centered within the physiologically possible range, the visual scale becomes misleading.

**Example:**
- Healthy range: 5–15 (mid=10, half_range=5)
- Physiologically possible range: 2–100

| Value | Distance from healthy edge | h_score |
|-------|---------------------------|---------|
| 3     | 2 below healthy_min       | −0.4    |
| 90    | 75 above healthy_max      | −14.0   |

A value of 90 is scored at −14, which is 35× worse than a value of 3, even though both are "outside the healthy range." More importantly, there is no shared meaning of what −1 represents across different markers.

---

## 3. Solution A: Four-Zone Asymmetric Normalization

Instead of two zone boundaries, define four per marker:

```
physio_min ... healthy_min ---- CENTER ---- healthy_max ... physio_max
    −1               0             1.0            0              −1
```

Use a **piecewise linear function** that normalizes each arm independently:

```python
def normalize_4zone(
    raw: float,
    healthy_min: float,
    healthy_max: float,
    physio_min: float,
    physio_max: float,
) -> float:
    mid = (healthy_min + healthy_max) / 2.0
    half_range = (healthy_max - healthy_min) / 2.0

    if healthy_min <= raw <= healthy_max:
        # Inside healthy range: 0.0 at edges, 1.0 at center
        return 1.0 - abs(raw - mid) / half_range
    elif raw < healthy_min:
        # Below healthy range: 0.0 at healthy_min, -1.0 at physio_min
        if physio_min >= healthy_min:
            return 0.0  # degenerate case
        return -(healthy_min - raw) / (healthy_min - physio_min)
    else:
        # Above healthy range: 0.0 at healthy_max, -1.0 at physio_max
        if physio_max <= healthy_max:
            return 0.0  # degenerate case
        return -(raw - healthy_max) / (physio_max - healthy_max)
```

**Properties:**
- `1.0` at the healthy center
- `0.0` at both healthy boundaries
- `−1.0` at both physiological extremes, regardless of asymmetry
- Values beyond physio limits go below `−1.0` (can be clamped as a warning flag)

**Key benefit:** `−1.0` now has the same meaning across every marker: "at the physiological limit." This makes cross-marker comparison and weighted combination statistically meaningful.

---

## 4. Solution B: Dataset Min/Max as Implicit Outer Limits

If physiological limits are not known or not specified, the outer bounds can be derived from the observed data:

```python
import numpy as np

def normalize_dataset_relative(
    values: list[float],
    healthy_min: float,
    healthy_max: float,
) -> list[float]:
    physio_min = min(values)
    physio_max = max(values)
    return [
        normalize_4zone(v, healthy_min, healthy_max, physio_min, physio_max)
        for v in values
    ]
```

Only `healthy_min` and `healthy_max` are required from the user. The chart always fills the full `[-1, 1]` range.

### Pros
- Only two user inputs needed
- Works for any marker without published reference ranges
- Good for exploratory, within-session analysis

### Cons

| Problem | Description |
|---------|-------------|
| **Scale instability** | Adding one new extreme measurement retroactively shifts all previous scores. A score of `0.7` from last month has a different meaning today. |
| **Outlier fragility** | A single bad reading (sensor glitch, typo) compresses all other scores toward zero. |
| **Multi-marker comparison breaks** | Marker A's `−1` means "the worst A value seen." Marker B's `−1` means "the worst B value seen." These do not represent equivalent severity, making weighted combination meaningless. |
| **Asymmetry by accident** | The healthy range may sit near one end of the observed data, creating lopsided visual scaling with no physiological meaning. |
| **Cold start** | With only a few data points, min/max are not representative of the real range. |

**The sharpest problem for ensemble scoring:** once you want to combine multiple markers into a composite score, dataset-relative normalization fails because each marker's scale is only meaningful relative to itself. Equal-weight averaging of such scores has no statistical basis.

### Improvement: Use 5th/95th Percentile Instead of Min/Max

```python
def normalize_percentile_relative(
    values: list[float],
    healthy_min: float,
    healthy_max: float,
    lower_pct: float = 5.0,
    upper_pct: float = 95.0,
) -> list[float]:
    physio_min = np.percentile(values, lower_pct)
    physio_max = np.percentile(values, upper_pct)
    return [
        normalize_4zone(v, healthy_min, healthy_max, physio_min, physio_max)
        for v in values
    ]
```

Same UX (no extra inputs), but one outlier cannot collapse the scale. All other cons above still apply.

---

## 5. Where Zone Boundaries Should Live

Currently the toolbox asks the user to supply `healthy_min` and `healthy_max` at plot time. This has two problems:
1. The user must re-enter them every session
2. There is no place to store `physio_min` / `physio_max`

The right home for zone boundaries is **on the marker record itself** as database columns:

```
markers table:
  ...existing fields...
  healthy_min   REAL
  healthy_max   REAL
  physio_min    REAL    (nullable — if NULL, computed from dataset)
  physio_max    REAL    (nullable — if NULL, computed from dataset)
```

Benefits:
- Each marker normalizes itself — no user input at analysis time
- Normalization can run automatically on data ingest
- Composite analysis becomes a pure computation over already-normalized h-scores
- The toolbox becomes an editor for these limits, not a required step before every analysis

---

## 6. Multi-Marker Ensemble Scoring

Once every marker produces an h-score on a shared `[-1, 1]` scale with shared semantics (which requires proper zone boundaries, not dataset-relative limits), combining them is natural.

### Weighted Average (Baseline)

```python
def composite_h_score(
    h_scores: dict[str, float],  # {marker_id: h_score}
    weights: dict[str, float],   # {marker_id: weight}
) -> float:
    total_weight = sum(weights.get(k, 1.0) for k in h_scores)
    weighted_sum = sum(h_scores[k] * weights.get(k, 1.0) for k in h_scores)
    return weighted_sum / total_weight if total_weight > 0 else 0.0
```

Weights can be:
- **Equal** (default, no assumptions)
- **Clinician-specified** (domain knowledge)
- **Data-derived** (PCA loadings, correlation structure)

### PCA-Derived Weights

PCA on a matrix of h-scores (rows = time points, columns = markers) identifies which markers co-vary and by how much. Loadings from PC1 can serve as weights:

```python
from sklearn.decomposition import PCA
import numpy as np

def pca_weights(h_score_matrix: np.ndarray) -> np.ndarray:
    """
    h_score_matrix: shape (n_timepoints, n_markers)
    Returns weights from the first principal component.
    """
    pca = PCA(n_components=1)
    pca.fit(h_score_matrix)
    loadings = pca.components_[0]          # shape (n_markers,)
    loadings = np.abs(loadings)            # use magnitude, not sign
    return loadings / loadings.sum()       # normalize to sum=1
```

**Important caveat:** PCA maximizes variance, not health relevance. If a cluster of correlated markers dominates the dataset (e.g., all inflammatory), PC1 will be dominated by them regardless of clinical importance. PCA is best used as an **exploratory tool** to understand the marker space structure, not necessarily as the weighting mechanism for a clinical score.

### UMAP and t-SNE: Visualization, Not Scoring

UMAP and t-SNE reduce high-dimensional marker trajectories to 2D/3D for visualization. They are useful for:
- Spotting clusters (healthy vs. disease states)
- Visualizing a subject's trajectory through marker space over time
- Comparing trajectories across subjects

They do **not** produce a scalar health score. They are most powerful once you have multiple subjects to compare trajectories against.

```python
import umap

def embed_trajectories(h_score_matrix: np.ndarray, n_components: int = 2) -> np.ndarray:
    """
    h_score_matrix: shape (n_timepoints, n_markers)
    Returns 2D (or 3D) embedding for visualization.
    """
    reducer = umap.UMAP(n_components=n_components, random_state=42)
    return reducer.fit_transform(h_score_matrix)
```

### Factor Analysis for Domain-Based Scoring

If markers can be grouped into clinical domains (inflammatory, metabolic, cardiovascular), factor analysis can identify a latent score per domain:

```python
from sklearn.decomposition import FactorAnalysis

def domain_scores(
    h_score_matrix: np.ndarray,
    n_factors: int = 3,
) -> np.ndarray:
    """
    h_score_matrix: shape (n_timepoints, n_markers)
    Returns shape (n_timepoints, n_factors) — one latent score per domain.
    """
    fa = FactorAnalysis(n_components=n_factors, random_state=42)
    return fa.fit_transform(h_score_matrix)
```

The final composite then combines domain scores with clinician-specified domain weights. This is more interpretable than raw PCA because each factor maps to a clinical concept.

---

## 7. Temporal Alignment

Multiple markers measured at different times and frequencies must be placed on a common timeline before combination. Options from simplest to most rigorous:

### Last-Known-Value (Step Function)

```python
def last_known_value(
    times: list[float],
    values: list[float],
    query_times: list[float],
) -> list[float]:
    """Use the most recent measurement at each query time."""
    result = []
    for t in query_times:
        past = [(tv, v) for tv, v in zip(times, values) if tv <= t]
        result.append(past[-1][1] if past else float('nan'))
    return result
```

Works well for slowly-changing markers. Simple, no extrapolation.

### Linear Interpolation

```python
import numpy as np

def linear_interp(
    times: list[float],
    values: list[float],
    query_times: list[float],
) -> list[float]:
    return list(np.interp(query_times, times, values))
```

Works for smooth, frequently-sampled markers. Fails for markers that change suddenly.

### Gaussian Process Regression (Future Goal)

GP regression is the mathematically correct approach for irregular, noisy biomarker time series. It gives not just a value at each time point but a **probability distribution** — mean and confidence interval. This naturally feeds into uncertainty-aware composite scores.

```python
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
import numpy as np

def gp_interpolate(
    times: np.ndarray,      # shape (n,)
    values: np.ndarray,     # shape (n,)
    query_times: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns (mean, std) at each query time.
    std gives uncertainty — larger gaps = wider confidence intervals.
    """
    kernel = RBF(length_scale=30.0) + WhiteKernel(noise_level=0.1)
    gpr = GaussianProcessRegressor(kernel=kernel, normalize_y=True)
    gpr.fit(times.reshape(-1, 1), values)
    mean, std = gpr.predict(query_times.reshape(-1, 1), return_std=True)
    return mean, std
```

GP regression handles:
- Irregular sampling intervals
- Missing data gaps
- Measurement noise
- Uncertainty quantification (confidence bands on the chart)

Worth investing in if prediction and trajectory forecasting are long-term goals.

---

## 8. Recommended Architecture (Layered)

```
Layer 1: Per-Marker Normalization
  - 4-zone asymmetric piecewise function
  - Zone definitions stored on the marker record (healthy_min/max, physio_min/max)
  - physio limits: explicit if known, else 5th/95th percentile of observed data
  - Output: h_score ∈ [−1, 1] per measurement

Layer 2: Temporal Alignment
  - Align each marker's h_scores to a common timeline
  - Start: last-known-value or linear interpolation
  - Future: Gaussian Process per marker (also gives uncertainty bands)

Layer 3: Composite Score
  - Input: matrix of h_scores (n_timepoints × n_markers), all on same timeline
  - Start: equal-weight or manual-weight average
  - Future: PCA/factor-analysis-derived weights
  - Output: scalar composite h_score per time point, plotted on same −1 to 1 axis

Layer 4: Advanced Analysis (future)
  - Population comparison: how does this subject compare to a reference cohort?
  - Anomaly detection: isolation forest or autoencoder on h_score trajectories
  - Prediction: GP extrapolation, survival models
  - Visualization: UMAP/t-SNE trajectory maps across subjects
```

---

## 9. Subject-Relative vs. Population-Relative Normalization

An important design question: whose reference ranges define the zone boundaries?

| Mode | Zone boundaries from | Answers the question |
|------|---------------------|----------------------|
| **Subject-relative** | The individual's own healthy range | "How is this person doing vs. their own optimum?" |
| **Population-relative** | Published or cohort-derived reference ranges | "How is this person doing vs. the average person?" |

Both are valid and answer different clinical questions. The architecture supports both: store a subject-specific override alongside the population-default on the marker record, and let the analysis choose which to use.

---

## 10. Open Design Decisions

1. **What does `−1` mean clinically?** Options: (a) absolute physiological extreme, (b) threshold requiring clinical intervention, (c) worst value observed in the dataset. The answer determines how physio limits are set and what the score communicates.

2. **Should physio limits be stored per-marker in the DB, or computed per-session from the loaded data?** Storing them enables auto-normalization on ingest and cross-session consistency. Computing them per-session is simpler but unstable.

3. **What is the primary timescale for ensemble scoring?** If markers range from daily glucose to annual VO2max, the common timeline needs a decision: day? week? month?

4. **How should missing data be handled in composite scoring?** Options: skip the marker for that time point, carry forward last known value, treat as NaN and propagate uncertainty.
