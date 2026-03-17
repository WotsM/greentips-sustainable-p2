import ast
import datetime
import json
import random
import typer
from pathlib import Path

app = typer.Typer(help="GreenTips CLI")

def rule_nested_loops(node):
    """Detects O(n^2) nested loops (Tip 001)."""
    if isinstance(node, ast.For):
        for child in node.body:
            if isinstance(child, ast.For):
                return "001"
    return None

def rule_unbounded_read(node):
    """Detects reading entire files into memory (Tip 020)."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr == 'read' and not node.args:
            return "020"
    return None

ACTIVE_RULES = [
    rule_nested_loops,
    rule_unbounded_read,
]

class ScalableAnalyzer(ast.NodeVisitor):
    """Applies all ACTIVE_RULES to every node."""
    def __init__(self, tips_db):
        self.tips_db = tips_db
        self.warnings = []

    def generic_visit(self, node):
        for rule_function in ACTIVE_RULES:
            tip_id = rule_function(node)
            
            if tip_id:
                tip_data = next((t for t in self.tips_db if t["id"] == tip_id), None)
                if tip_data:
                    self.warnings.append({
                        "line": getattr(node, 'lineno', 'Unknown'),
                        "data": tip_data
                    })
        
        super().generic_visit(node)

def load_tips():
    """Loads 'tips.json'."""
    current_dir = Path(__file__).parent
    json_path = current_dir / "tips.json"
    
    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)

def get_daily_tip(tips_list):
    """Selects a random tip based on calendar day."""
    today_string = datetime.date.today().isoformat()
    random.seed(today_string)
    return random.choice(tips_list)

@app.command()
def daily():
    """Get your daily sustainability tip."""
    try:
        tips = load_tips()
    except FileNotFoundError:
        typer.echo("Error: Could not find 'tips.json'.")
        raise typer.Exit(code=1)
    
    daily_tip = get_daily_tip(tips)
    
    typer.echo("GreenTips Daily Sustainability Tip:")
    typer.echo(f"\n{daily_tip['tip']}")
    typer.echo(f"Why? {daily_tip['why']}")
    typer.echo(f"\nEffort: {daily_tip['effort'].title()}")

@app.command()
def analyze(filepath: Path = typer.Argument(..., help="Path to the Python file to analyze")):
    """Analyze a Python file for more sustainable patterns."""
    if not filepath.exists() or not filepath.is_file():
        typer.echo(f"Error: File '{filepath}' does not exist.")
        raise typer.Exit(code=1)

    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
        tips_db = load_tips()
    except SyntaxError as e:
        typer.echo(f"Syntax Error in file: {e}")
        raise typer.Exit(code=1)
    except FileNotFoundError:
        typer.echo("Error: Could not find 'tips.json'.")
        raise typer.Exit(code=1)

    analyzer = ScalableAnalyzer(tips_db)
    analyzer.visit(tree)

    if not analyzer.warnings:
        typer.echo(f"No obvious imporvements found in {filepath.name}.")
    else:
        typer.echo(f"GreenTips found {len(analyzer.warnings)} potential improvements in {filepath.name}:\n")
        for warning in analyzer.warnings:
            tip = warning['data']
            typer.echo(f"Line {warning['line']} -> {tip['title']} (Tip {tip['id']})")
            typer.echo(f"  {tip['tip']}\n")

if __name__ == "__main__":
    app()