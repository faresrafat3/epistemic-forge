# Honest baseline for imbalanced tabular Kaggle — Kaggle Spine

## Problem
What is an honest baseline plan for a noisy imbalanced Kaggle table where leakage is a real risk?

## Skills retrieved
kaggle_baseline_spine

## Plan
1. **Define target & metric** — match leaderboard metric exactly.
2. **Leakage audit** — time, group, target leakage checks.
3. **EDA** — missingness, cardinality, target balance, simple slices.
4. **Baseline** — linear/GBDT simple pipeline; record CV mean±std.
5. **Error analysis** — where does baseline fail?
6. **One improvement** — single ablated idea; measure lift.
7. **Ship** — reproducible seeds, requirements, README.

## Skeleton code
```python
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import HistGradientBoostingClassifier

# df = pd.read_csv('train.csv')
# y = df['target']
# X = df.drop(columns=['target'])

# num_cols = X.select_dtypes(include='number').columns
# cat_cols = X.select_dtypes(exclude='number').columns
# pre = ColumnTransformer([
#     ('num', SimpleImputer(strategy='median'), num_cols),
#     ('cat', Pipeline([
#         ('imp', SimpleImputer(strategy='most_frequent')),
#         ('oh', OneHotEncoder(handle_unknown='ignore')),
#     ]), cat_cols),
# ])
# clf = Pipeline([('pre', pre), ('model', HistGradientBoostingClassifier(random_state=42))])
# cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
# scores = cross_val_score(clf, X, y, cv=cv, scoring='roc_auc')
# print(scores.mean(), scores.std())
```

## Honest claims checklist
- [ ] Metric matches competition
- [ ] Split policy documented
- [ ] No target leakage features
- [ ] Baseline before complexity
