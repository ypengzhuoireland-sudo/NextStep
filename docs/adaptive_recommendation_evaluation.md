# NextStep Adaptive Recommendation Strategy

## 1. Overview

NextStep uses an adaptive recommendation strategy to help students focus on programming concepts that require further practice.

Instead of presenting exercises in a fixed order, the system uses the student’s current mastery profile to identify weaker knowledge components and recommend relevant exercises.

The purpose of this strategy is to make practice more personalised and better aligned with the student’s current learning needs.

## 2. Knowledge Components and Mastery

The programming content in NextStep is divided into knowledge components. Each knowledge component represents a programming concept, such as variables, conditionals, loops, functions or data structures.

Each student has a mastery value for every knowledge component. These values represent the system’s current estimate of the student’s understanding of each concept.

Mastery values are initially produced by the diagnostic assessment and are updated when the student submits exercise solutions.

## 3. Adaptive Recommendation Process

The adaptive recommendation process follows these steps:

1. Retrieve the student’s current mastery profile.
2. Compare the mastery values of all knowledge components.
3. Identify the knowledge component with the lowest mastery value.
4. Find exercises associated with that knowledge component.
5. Exclude the current exercise when another suitable exercise is available.
6. Select an exercise and present it as the recommended next activity.

This process directs the student towards concepts where additional practice may be most useful.

The main recommendation strategy focuses on the weakest knowledge component. It does not currently perform detailed difficulty matching based on the student’s mastery level.

## 4. Mastery Updates

After the student submits an exercise, NextStep uses the result to update the mastery values of the knowledge components associated with that exercise.

A submission is treated as correct only when all required test cases pass. The result is therefore converted into a binary observation:

- Correct when all tests pass;
- Incorrect when one or more tests fail.

The system applies Bayesian Knowledge Tracing to update the student’s mastery estimate. The updated mastery profile is then used when generating future recommendations.

This creates a continuous cycle:

> Student submission → Mastery update → Weakest knowledge component identification → Next exercise recommendation

## 5. Comparison with Random Recommendation

A random recommendation strategy can be used as a baseline for evaluating the adaptive approach.

The random strategy selects an exercise without using the student’s mastery profile. Both strategies should use the same exercise bank and the same rules for excluding the current exercise.

The main difference between the strategies is therefore:

- The adaptive strategy uses the student’s mastery information;
- The random strategy does not use mastery information.

This comparison can help determine whether mastery tracking changes the relevance of the recommended exercises.

## 6. Evaluation Approach

The recommendation strategies can be evaluated using a collection of simulated mastery profiles.

Each profile represents a student with different strengths and weaknesses. For each profile, the weakest knowledge component is identified before a recommendation is generated.

The adaptive and random strategies can then be compared by checking whether their recommendations target the weakest knowledge component.

Random recommendation should be repeated several times because a single random selection may not provide a representative result.

This evaluation examines the behaviour of the recommendation strategies. It does not directly measure student learning outcomes.

## 7. Evaluation Metrics

### 7.1 Weakest-Knowledge-Component Hit Rate

A recommendation is counted as a hit when the recommended exercise is linked to the student’s weakest knowledge component.

**Hit Rate = Recommendations targeting the weakest KC / Total recommendations**

A higher hit rate means that the strategy more consistently directs practice towards the student’s weakest area.

### 7.2 Mastery Priority Score

The mastery priority score represents how weak the knowledge component selected by the recommendation strategy is.

**Priority Score = 1 − M(recommended)**

Here, **M(recommended)** represents the current mastery value of the knowledge component selected by the recommendation strategy.

A higher priority score means that the recommended exercise targets a weaker knowledge component.

### 7.3 Repeated-Recommendation Rate

The repeated-recommendation rate measures how often the current exercise is recommended again when other suitable exercises are available.

**Repeated-Recommendation Rate = Repeated recommendations of the current exercise / Total recommendations**

A lower repeated-recommendation rate indicates greater exercise variety.

This metric should only be used when the current exercise is recorded as part of the evaluation.

## 8. Interpretation

If the adaptive strategy achieves a higher weakest-KC hit rate than random recommendation, this would indicate that mastery information helps direct practice towards identified knowledge gaps.

A higher mastery priority score would also show that the adaptive strategy tends to select exercises associated with weaker areas.

However, these metrics only measure recommendation relevance. They do not demonstrate that the student learned more or achieved better academic results.

Evidence of learning improvement would require a separate study involving real students, learning activities and pre-test/post-test measurements.

## 9. Limitations

The evaluation strategy has several limitations:

- Simulated mastery profiles do not represent the full behaviour of real students.
- The weakest-KC hit rate is closely related to the intended design of the adaptive algorithm.
- The distribution of exercises across knowledge components may affect random recommendation results.
- The main strategy focuses on the lowest mastery value and does not perform detailed difficulty matching.
- Exercise submissions are treated as binary observations, so partially correct solutions do not produce partial mastery updates.
- Recommendation relevance does not directly measure learning improvement.
- A simulation-based comparison cannot replace a controlled user study.

## 10. Future Improvements

The adaptive recommendation strategy could be extended by:

- Matching exercise difficulty to the student’s current mastery level;
- Considering several weak knowledge components instead of only the lowest one;
- Reducing repeated recommendations;
- Using recent submission history when selecting exercises;
- Giving partial credit for partially successful solutions;
- Evaluating the strategy with real student learning data;
- Comparing pre-test and post-test performance;
- Measuring long-term knowledge retention.

## 11. Conclusion

NextStep’s adaptive recommendation strategy uses mastery information to identify a student’s weakest knowledge component and recommend a related programming exercise.

A comparison with random recommendation can be used to evaluate whether mastery information improves the relevance of exercise selection. However, such a comparison only evaluates recommendation behaviour and does not prove that the strategy improves actual learning outcomes.

Further evaluation involving real students would be required to measure learning improvement and long-term educational value.
