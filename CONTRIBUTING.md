# Want to Contribute?
This contribution guide outlines the following options for you to get started:
1. [Get Access](#get-access-)
2. [Add a tip](#add-a-tip-)
3. [Contribute a feature/bugfix](#contribute-a-featurebugfix-)
4. [Report an issue/suggest a feature](#report-an-issuesuggest-a-feature-)

## Get Access ##
You can access the repository through [GitHub](https://github.com/WotsM/greentips-sustainable-p2). Please create a fork to add your changes into and create a pull request with your changes to the repository.

## Add a Tip ##
Do you want to share a tip with the community? You can follow these steps:

1. Open the repository.
2. Navigate to `greentips/tips.json`.
3. Add your new tip in the same JSON structure already used in the file.
4. Commit the change to your fork.
5. Open a pull request describing the tip you added by using the `add-a-tip` template.

Please keep the JSON valid and match the existing formatting so the review can be merged quickly. You can check if the JSON is still valid on mocOS or Linux by running `python3 -m json.tool greentips/tips.json > /dev/null`. If it is still valid, there will be no output.

### Example Tip Format ###
Use an existing tip as a template and add a new object to the JSON array:

```json
{
  "id": "012",
  "title": "Avoid unnecessary retries",
  "tip": "Do not retry failed requests immediately in a tight loop. Use backoff and stop retrying when the failure is not recoverable.",
  "why": "Aggressive retries create avoidable CPU, network, and server load. Smarter retry behavior reduces wasted work and energy use.",
  "category": "network",
  "language": ["general"],
  "impact": "medium",
  "effort": "low",
  "tags": ["retries", "backoff", "network", "resilience"],
  "source": ["Green Software Foundation - Energy Efficiency"],
  "sourceLink": [
    "https://learn.greensoftware.foundation/energy-efficiency/"
  ],
  "future_static_analysis": {
    "detectable": true,
    "pattern": "immediate retry loop without delay or retry limit",
    "languages": []
  }
}
```

### What Each Field Means ###
- `id`: A unique string ID for the tip. Please follow the existing numbering pattern in `tips.json`.
- `title`: A short, clear name for the tip.
- `tip`: The practical recommendation you want developers to follow.
- `why`: A short explanation of why this tip helps sustainability, efficiency, or energy usage.
- `category`: The main topic area, such as `computation`, `memory`, `network`, `database`, `io`, or `energy`.
- `language`: A JSON array listing the relevant programming languages, or use `["general"]` if the tip applies broadly.
- `impact`: A rough estimate of the expected sustainability impact. Match the style already used in the file, such as `high`, `medium`, or `low`.
- `effort`: A rough estimate of how hard the change is to apply, usually `low` (0-1h), `medium`(1h-3h), or `high`(3h+).
- `tags`: A JSON array of short keywords that help describe the tip.
- `source`: A JSON array of source names, articles, papers, or organizations supporting the tip.
- `sourceLink`: A JSON array of URLs matching the entries in `source` in the same order.
- `future_static_analysis`: Metadata for possible automated detection in the future.
- `future_static_analysis.detectable`: Set to `true` if the tip could realistically be detected automatically, otherwise `false`.
- `future_static_analysis.pattern`: A short description of the code smell or pattern a tool might detect.
- `future_static_analysis.languages`: A JSON array of languages where that detection idea would apply. Leave empty if it is not related to a specific language.

If your tip does not have a meaningful static-analysis idea, follow the existing examples or keep this section empty rather than inventing extra fields.

## Contribute a feature/bugfix ##
You can directly add your changes as above via a fork. After adding your changes, you can make your pull request by choosing the corresponding template. For implementation ideas, you can also pickup any open and unassigned issue to work on in our issues list.

## Report an Issue/Suggest a feature ##
We are open to any improvements to GreenTips! If you have ideas, you can create a new issue in our GitHub page, please make sure to choose an appropriate issue template.