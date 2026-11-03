# Analysis plan

Written before computing any effects. The idea is to fix from the start what gets measured, how, and with what decision criterion, so that I don't later pick whichever metric or segment looks best.

## 1. Context

An online clothing retailer took 64,000 customers who had bought in the past 12 months and randomly assigned them to three groups:

| Group | Treatment |
|---|---|
| Control | Receives no email |
| Mens | Receives an email featuring men's merchandise |
| Womens | Receives an email featuring women's merchandise |

Over the following two weeks, the data records whether each customer visited the site, whether they bought, and how much they spent.

## 2. Business question

Should the company send email campaigns? If so, which of the two, and to which customers?

## 3. Unit of analysis and population

- Unit: customer (one row per customer).
- Intention-to-treat (ITT) analysis: all customers are compared by their assigned group, whether or not they opened the email. The dataset has no open data, so this is also the only possible analysis, and it is the one that matters for the decision: the company controls who it sends to, not who opens.

## 4. Metrics

| Type | Metric | Definition |
|---|---|---|
| Primary | Revenue per customer | Mean `spend` over the two weeks, zeros included |
| Secondary | Visit rate | Share with `visit = 1` |
| Secondary | Conversion rate | Share with `conversion = 1` |
| Descriptive | Average order value | Mean `spend` among customers who bought |

Why revenue is the primary metric: the final decision is about money. Visits are easier to move and to detect, but a campaign that brings visits without purchases does not pay off.

Guardrails: in a real experiment I would track email list unsubscribes and spam complaints. The dataset does not include them; this remains a limitation.

Average order value is descriptive only: it is computed over customers who bought, a group defined after treatment. Comparing it across groups has no causal interpretation.

## 5. Hypotheses

For each metric:

- H1: Mens vs. Control
- H2: Womens vs. Control
- H3: Mens vs. Womens

Two-sided tests with α = 0.05. The three comparisons for each metric are adjusted with Holm.

## 6. Methods

| Step | Method |
|---|---|
| Balanced assignment | Chi-square *sample ratio mismatch* test against 1/3 per group |
| Covariate balance | Standardized mean difference (warning threshold: \|SMD\| > 0.1) |
| Power | Minimum detectable effect at 80% power for each metric |
| Proportions | Difference in proportions, Wald CI and z-test |
| Revenue | Difference in means with Welch's test and bootstrap (10,000 replicates, percentile CI) |

`spend` has a huge share of zeros and a long tail, so the bootstrap is there to confirm that the normal approximation holds. Extreme values are not trimmed in the main analysis: they are real purchases and total revenue depends on them. As a sensitivity check, the analysis is repeated with `spend` capped at the 99th percentile.

## 7. Effects by segment

Using only variables measured before the experiment:

- `newbie` (new customer in the past 12 months)
- `channel` (purchase channel: Phone, Web, Multichannel)
- `zip_code` (Urban, Surburban, Rural)
- `mens` and `womens` (bought men's / women's merchandise in the past year)
- `recency` grouped into terciles
- `history` grouped into terciles

To avoid mistaking noise for findings, the sample is split at random into two halves:

1. Exploration: segment effects are estimated and the promising interactions are chosen.
2. Confirmation: only those interactions are tested again, with a Holm adjustment.

Anything that is not confirmed is reported as exploratory.

## 8. Uplift model (extension)

One model per group (*T-learner*) predicts each customer's expected revenue with and without each email. The resulting rule ("send each customer the email with the highest expected incremental revenue") is evaluated on 30% of the data the model never saw, with an inverse probability weighting estimator, and compared against simple rules: send nothing, send everyone the men's email, and send everyone the women's email.

## 9. Decision criterion

- A campaign is recommended if the lower bound of the 95% CI for incremental revenue per customer is greater than the cost of sending.
- Between two recommendable campaigns, the one with the higher incremental revenue is chosen, but only if the difference (H3) is significant; otherwise the choice is made on cost or both are tested again.
- A segment rule or a model is only recommended if it beats the best simple rule on data that was not used to build it (the confirmation half or the test set).

## 10. Known limitations

- The experiment is from 2008; email behavior is different today.
- There is no data on cost, margin or list unsubscribes; cost assumptions are labeled as such.
- Two-week window: it does not measure long-term effects or cannibalization of future purchases.
