

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
| `url` | Original URL for the source. |
| `publication_date` | Date the source was published, posted, filed, released, or last updated. |
| `access_date` | Date you accessed or saved the source. |
| `pricing_terms_used` | Exact pricing-related terms used in the source, such as `dynamic pricing`, `personalized pricing`, `AI pricing`, `surveillance pricing`, or `personalized discounts` etc. |
| `pricing_characterization` | How the source frames the pricing practice, such as `consumer benefit`, `consumer harm`, `routine pricing`, `legal concern`, `transparency issue`, `denial`, or `unclear`. |
| `company_position` | The company's stance, if present: for example, `admits`, `denies`, `clarifies/qualifies`, `no response`, `third-party allegation`, or `unclear`. |
| `summary` | Brief summary of the source's discussion of the project topics. This can include what the source claims, how it relates to personal data, public pressure, legal milestones, or company communications |
| `key_excerpts` |  Useful excerpt or excerpts that capture the source's main claim, framing, or evidence. |
