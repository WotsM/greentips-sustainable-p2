from collections import Counter
from pathlib import Path

EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".java": "java",
    ".swift": "swift",
    ".rs": "rust",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "c",
    ".cs": "csharp",
    ".go": "go",
    ".rb": "ruby",
    ".php": "php",
    ".sql": "sql",
}


def detect_majority_language(target: Path):
    if target.is_file():
        return EXTENSION_TO_LANGUAGE.get(target.suffix.lower())

    language_counts = Counter()
    for file_path in target.rglob("*"):
        if not file_path.is_file():
            continue
        language = EXTENSION_TO_LANGUAGE.get(file_path.suffix.lower())
        if language:
            language_counts[language] += 1

    if not language_counts:
        return None

    most_common = language_counts.most_common()
    top_count = most_common[0][1]
    top_languages = sorted(language for language, count in most_common if count == top_count)
    return top_languages[0]
