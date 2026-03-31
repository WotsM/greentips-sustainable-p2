# greentips-sustainable-p2
GreenTips is a Command Line Interface (CLI) tool that enables developers to explore alternative sustainable design patterns by providing tips during coding.

## Fallback hierarchy (context-aware)

GreenTips returns exactly one tip with two possible hierarchies:

**No path provided** (quick random tip):
1. Majority-language tip (detected from current directory)
2. Random general tip

**Path provided** (full analysis):
1. Specific analysis tip (currently Python rules)
2. Majority-language tip (based on file extensions in the target path)
3. Random general tip

## Installation

You can install the GreenTips CLI directly from this GitHub repository using `pip`:

`pip install git+https://github.com/WotsM/greentips-sustainable-p2.git`

## Usage

Two modes available:

**Quick mode** (language + general tip):
```bash
greentips tip
```

**Analysis mode** (analysis + language + general tip):
```bash
greentips tip <TARGET_PATH>
```

Examples:
```bash
greentips tip                  # Language tip from current directory, then general
greentips tip ./src            # Analyze ./src folder
greentips tip ./app.py         # Analyze specific file
```

If you'd like to contribute, see [CONTRIBUTING.MD](./CONTRIBUTING.MD).
