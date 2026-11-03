# Reports

## Figures

Every chart in the README and the notebooks is saved to `figures/` when the notebooks run.

## Data for Power BI

The CSV files in `powerbi/` are generated at the end of `notebooks/03_segments_and_impact.ipynb`.

| File | Contents | Grain |
|---|---|---|
| `group_summary.csv` | Customers, visits, buyers and revenue by group | One row per group |
| `main_effects.csv` | Effect of each comparison with 95% CI, p-value and Holm-adjusted p | Metric × comparison |
| `effects_by_segment.csv` | Effect of each campaign versus control by segment, with 95% CI | Segment × level × campaign |
| `policy_value.csv` | Expected revenue per customer for each targeting rule on the test set | One row per rule |
| `impact_scenarios.csv` | Profit per email and maximum profitable cost by margin | Margin × campaign |

## Decision report (one page)

The report is not meant to repeat the analysis charts but to work as a tool: someone in marketing picks a segment and sees which campaign to use and how much it brings in.

Suggested visuals

1. Cards: incremental revenue per 1,000 emails for each campaign (from `main_effects.csv`, metric `spend`, multiplying `difference` by 1,000).
2. Slicers: filters on `segment` and `level` from `effects_by_segment.csv`.
3. Bar chart with error bars: `effect` by `campaign` for the selected segment, with `ci_low` and `ci_high`.
4. Scenario table: `impact_scenarios.csv` with a margin parameter.
5. Fixed note: the segment effects are exploratory; no difference between segments was confirmed in the confirmation half.

Example DAX measures

```DAX
Incremental revenue per 1000 =
    SUM ( effects_by_segment[effect] ) * 1000

CI width =
    SUM ( effects_by_segment[ci_high] ) - SUM ( effects_by_segment[ci_low] )

Best campaign =
    VAR m = CALCULATE ( SUM ( effects_by_segment[effect] ), effects_by_segment[campaign] = "Mens" )
    VAR w = CALCULATE ( SUM ( effects_by_segment[effect] ), effects_by_segment[campaign] = "Womens" )
    RETURN IF ( m >= w, "Mens", "Womens" )
```
