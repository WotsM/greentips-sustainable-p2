from pathlib import Path
from typing import Optional

import typer

from greentips.analyzers import analyze_python_target
from greentips.language_detection import detect_majority_language
from greentips.tips import load_tips, pick_general_tip, pick_language_tip

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

app = typer.Typer(
    help="🌱 Get sustainability tips for your codebase"
)

console = Console()


@app.callback()
def root():
    """GreenTips command group."""

def _print_tip(source_label, tip_data, details=None, is_general=False):
    # Header
    title = f"[bold green]🌱 GreenTip • {source_label}"
    title += "[/bold green]"

    # Body
    body = ""

    if details:
        body += f"[dim]{details}[/dim]\n\n"

    body += f"💡 [bold]Tip[/bold]\n{tip_data['tip']}\n\n"
    body += f"🔍 [cyan]Why[/cyan]\n{tip_data['why']}\n\n"
    body += f"⚡ [yellow]Effort[/yellow]\n{str.capitalize(tip_data['effort'])}"

    if is_general:
        body += "\n\n[dim]Random suggestion • Run again for another tip[/dim]"

    # Sources
    sources = tip_data.get("source")
    links = tip_data.get("sourceLink")
    if sources and links:
        body += "\n\n📚 [magenta]Sources[/magenta]\n"
        for name, link in zip(sources, links):
            # render the source name as clickable
            body += f"• [link={link}]{name}[/link]\n"

    console.print(
        Panel(
            body,
            title=title,
            border_style="green",
            padding=(1, 2),
            width=80,
        )
    )



@app.command()
def tip(
    target: Optional[Path] = typer.Argument(None, help="Optional: file or folder path to inspect"),
):
    """Return one sustainability tip using context-aware fallback hierarchy.

    If no path provided:
    1) majority language tip (current directory)
    2) general tip

    If path provided:
    1) specific static analysis tip (currently Python rules)
    2) majority language tip
    3) general tip
    """
    try:
        tips = load_tips()
    except FileNotFoundError:
        console.print("[bold red]❌ Error:[/bold red] Could not find 'tips.json'.")
        raise typer.Exit(code=1)

    # Mode 1: No path specified, language + general only
    if target is None:
        majority_language = detect_majority_language(Path("."))
        if majority_language:
            language_tip = pick_language_tip(tips, majority_language)
            if language_tip:
                details = f"Majority language detected: {majority_language}"
                _print_tip(f"{majority_language} Language Tip", language_tip, details)
                return

        general_tip = pick_general_tip(tips)
        if general_tip is None:
            console.print("[bold red]❌ Error:[/bold red] No general tips available in tips database.")
            raise typer.Exit(code=1)
        _print_tip("General Tip", general_tip, "No language tip matched for current directory.", True)
        return

    # Mode 2: Path specified, full hierarchy
    if not target.exists():
        console.print(f"[bold red]❌ Error:[/bold red] Path '{target}' does not exist.")
        raise typer.Exit(code=1)

    static_result = analyze_python_target(target, tips)
    if static_result:
        tip_data = static_result["tip"]
        details = (
            f"Matched in {static_result['file'].name} at line {static_result['line']} "
            f"(Tip {tip_data['id']}: {tip_data['title']})"
        )
        _print_tip("Specific Analysis Tip", tip_data, details)
        return

    majority_language = detect_majority_language(target)
    if majority_language:
        language_tip = pick_language_tip(tips, majority_language)
        if language_tip:
            details = f"Majority language detected: {majority_language}"
            _print_tip(f"{majority_language} Language Tip", language_tip, details)
            return

    general_tip = pick_general_tip(tips)
    if general_tip is None:
        console.print("[bold red]❌ Error:[/bold red] No general tips available in tips database.")
        raise typer.Exit(code=1)

    _print_tip("General Tip", general_tip, "No specific/static or language tip matched.", True)


if __name__ == "__main__":
    app()
