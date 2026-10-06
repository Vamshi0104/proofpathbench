# Pilot model selection — provisional

**Status:** prospective recommendation; not frozen and no provider calls made.

The current OpenAI model catalog (checked 2026-09-28) describes `gpt-6-luna` as the
cost-efficient high-volume model, `gpt-6-sol` as the cost/intelligence balance, and
`gpt-6-astra` as the highest-capability tier. All three support the Responses API and
Structured Outputs needed by the implemented adapter.

Official sources:

- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/models/gpt-6-luna
- https://developers.openai.com/api/docs/pricing
- https://developers.openai.com/api/docs/guides/structured-outputs

## Proposed pilot panel

| Provider | Requested model ID | Reasoning effort | Calls | Role |
|---|---|---:|---:|---|
| OpenAI | `gpt-6-luna` | `none` | 768 | efficient high-volume tier |
| OpenAI | `gpt-6-sol` | `none` | 768 | balanced tier |
| OpenAI | `gpt-6-astra` | `low` | 768 | frontier-capability tier |

The estimated combined Standard-processing cost is USD 12.42 under the expected-output
assumption and USD 21.71 under the 300-output-token allowance. This is not a quote; actual
API usage and then-current provider prices are authoritative. See
`research/pilot_cost_estimate.json`.

## Reproducibility limitation

The checked GPT-6 documentation exposes the aliases above but did not expose distinct
dated snapshot identifiers. Each run therefore records the requested model, model string
returned by the API, response ID, UTC time, service tier, and raw token usage. Alias drift
remains a limitation and must be disclosed.

## Generalization limitation

These are three capability tiers from one provider, not three independent model families.
The pilot can validate the benchmark and estimate tier heterogeneity, but a post-Gate-3
main experiment should add independently implemented provider or open-weight families if
credentials and stable snapshots are available. The local Ollama service was not running
when checked, and no external API credential was present in the execution environment.

## Required authorization

Before the config is frozen, a human must approve the panel and maximum spend and configure
credentials outside the repository. Never place an API key in a prompt, config file, raw
record, or manuscript artifact.
