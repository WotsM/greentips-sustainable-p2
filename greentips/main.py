from pathlib import Path
from typing import Optional

import typer

from greentips.analyzers import analyze_python_target
from greentips.language_detection import detect_majority_language
from greentips.tips import load_tips, pick_general_tip, pick_language_tip

app = typer.Typer(help="GreenTips CLI")


@app.callback()
def root():
    """GreenTips command group."""


def _print_tip(source_label, tip_data, details=None):
    typer.echo(f"GreenTips ({source_label}):")
    if details:
        typer.echo(details)
    typer.echo(f"\n{tip_data['tip']}")
    typer.echo(f"Why? {tip_data['why']}")
    typer.echo(f"Effort: {tip_data['effort'].title()}")


@app.command()
def tip(
    target: Optional[Path] = typer.Argument(None, help="Optional: file or folder path to inspect"),
):
    """Return one sustainability tip using context-aware fallback hierarchy.

    If no path provided:
    1) majority language tip (current directory)
    2) general tip of the day

    If path provided:
    1) specific static analysis tip (currently Python rules)
    2) majority language tip
    3) general tip of the day
    """
    try:
        tips = load_tips()
    except FileNotFoundError:
        typer.echo("Error: Could not find 'tips.json'.")
        raise typer.Exit(code=1)

    # Mode 1: No path specified, language + general only
    if target is None:
        majority_language = detect_majority_language(Path("."))
        if majority_language:
            language_tip = pick_language_tip(tips, majority_language)
            if language_tip:
                details = f"Majority language detected: {majority_language}"
                _print_tip("Majority Language", language_tip, details)
                return

        general_tip = pick_general_tip(tips)
        if general_tip is None:
            typer.echo("Error: No general tips available in tips database.")
            raise typer.Exit(code=1)
        _print_tip("General", general_tip, "No language tip matched for current directory.")
        return

    # Mode 2: Path specified, full hierarchy
    if not target.exists():
        typer.echo(f"Error: Path '{target}' does not exist.")
        raise typer.Exit(code=1)

    static_result = analyze_python_target(target, tips)
    if static_result:
        tip_data = static_result["tip"]
        details = (
            f"Matched in {static_result['file'].name} at line {static_result['line']} "
            f"(Tip {tip_data['id']}: {tip_data['title']})"
        )
        _print_tip("Specific Analysis", tip_data, details)
        return

    majority_language = detect_majority_language(target)
    if majority_language:
        language_tip = pick_language_tip(tips, majority_language)
        if language_tip:
            details = f"Majority language detected: {majority_language}"
            _print_tip("Majority Language", language_tip, details)
            return

    general_tip = pick_general_tip(tips)
    if general_tip is None:
        typer.echo("Error: No general tips available in tips database.")
        raise typer.Exit(code=1)

    _print_tip("General", general_tip, "No specific/static or language tip matched.")


if __name__ == "__main__":
    app()
