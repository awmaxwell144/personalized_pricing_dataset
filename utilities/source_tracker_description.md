

# Source Tracker Field Descriptions

Each company should have its own `source_tracker.csv`. The tracker is meant to give a quick overview of the sources collected for that company and support later analysis of how the company, media, policymakers, or other actors describe pricing practices.

| Field | Description |
|---|---|
| `source_id` | Short unique ID for the source, matching or resembling the dataset folder name. |
| `industry` | Industry category, e.g. `aviation`, `grocery`, `rideshare`, `accommodation`. |
| `company` | Company the source is about. |
| `source_title` | Title of the source, enclosed in double quotation marks in the cell, e.g. `"Delta Air Lines Q2 2025 Earnings Call Corrected Transcript"`. |
| `source_publisher` | Outlet, organization, agency, court, company, or platform that published the source. |
| `source_type` | Kind of source, e.g. `news article`, `company statement`, `privacy policy`, `lawsuit`, `letter`, `earnings call`, `social media post`. |
| `source_origin` | Whether the source is `company`, `third party`, or `third party with company statement`. Use `third party with company statement` when an outside source includes a quoted, paraphrased, or otherwise attributable response or statement from the company. |
| `url` | Original URL for the source. |
| `publication_date` | Date the source was published, posted, filed, released, or last updated. |
| `access_date` | Date you accessed or saved the source. |
| `pricing_terms_used` | Exact pricing-related terms used in the source, such as `dynamic pricing`, `personalized pricing`, `AI pricing`, `surveillance pricing`, or `personalized discounts` etc. |
| `company_position` | The company's stance, if present: for example, `admits`, `denies`, `clarifies/qualifies`, `no response`, `third-party allegation`, or `unclear`. |
| `summary` | Concise but informative summary of the source and how it discusses the company's pricing practices. Include enough detail to understand the source's main point, the pricing practice or allegation at issue, relevant data or AI claims, and any company response or legal/policy context. Keep it to a few sentences.|
| `key_excerpts` |  Useful excerpt or excerpts that capture the source's main claim, framing, or evidence. |
 