# OULAD Day-40 Snapshot Profile

This is a preprocessing profile, not a model-performance result.

## Cohort construction

- Prediction cutoff: day 40 after module presentation begins
- Included: students registered by day 40 with a supported final outcome
- Excluded: students whose unregistration was already recorded on or before day 40
- Unit: one student-module-presentation
- Snapshot rows: 27,042
- Duplicate unit keys: 0
- Snapshot columns: 36

## Later outcomes

| Final outcome | Rows |
|---|---:|
| Pass | 12,355 |
| Distinction | 3,024 |
| Fail | 7,033 |
| Withdrawn after cutoff | 4,630 |

For the initial binary experiment:

- Successful (`Pass` or `Distinction`): 15,379
- Adverse (`Fail` or later `Withdrawn`): 11,663

## Selected feature checks

- Assessments due by day 40: 0–2 per student-module snapshot
- Assessment completion rate never exceeded 1.0
- Mean assessment score is unavailable for 16.42% of rows, mainly where no scored assessment was available by the cutoff
- Median total VLE clicks by day 40: 284
- Median active VLE days by day 40: 17
- Median clicks during the final 14-day window: 52
- Median days since last VLE activity: 2

Missing assessment scores must be handled inside each training fold. They must not be filled using statistics calculated from the complete dataset.

## Interpretation boundary

VLE activity is an engagement indicator, not classroom attendance or proof of learning. A low click count may have several explanations, including offline study. Model explanations must describe associations in the available data and must not claim causation.

