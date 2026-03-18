import ast
import datetime
import json
import random
import typer
from pathlib import Path

app = typer.Typer(help="GreenTips CLI")

LOOP_NODES = (ast.For, ast.While)

def _get_parent(node):
    return getattr(node, "parent", None)

def _has_ancestor(node, node_types):
    current = _get_parent(node)
    while current is not None:
        if isinstance(current, node_types):
            return True
        current = _get_parent(current)
    return False

def _is_inside_with_context(node):
    current = _get_parent(node)
    while current is not None:
        if isinstance(current, ast.With):
            for with_item in current.items:
                context_expr = with_item.context_expr
                if context_expr is node:
                    return True
        current = _get_parent(current)
    return False

def _call_name(node):
    if not isinstance(node, ast.Call):
        return ""
    if isinstance(node.func, ast.Name):
        return node.func.id.lower()
    if isinstance(node.func, ast.Attribute):
        return node.func.attr.lower()
    return ""

def _constant_string_arg(node):
    if not isinstance(node, ast.Call) or not node.args:
        return None
    first_arg = node.args[0]
    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
        return first_arg.value
    return None

def _is_list_membership_check(node):
    if not isinstance(node, ast.Compare):
        return False
    if not any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops):
        return False
    candidates = [node.left, *node.comparators]
    return any(isinstance(candidate, (ast.List, ast.ListComp)) for candidate in candidates)

def annotate_parents(tree):
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child.parent = parent

def rule_nested_loops(node):
    """Detects O(n^2) nested loops (Tip 001)."""
    if isinstance(node, LOOP_NODES):
        for child in node.body:
            if isinstance(child, LOOP_NODES):
                return "001"
    return None

def rule_eager_list_conversion(node):
    """Detects eager list() conversion from generators (Tip 002)."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id == "list" and node.args and isinstance(node.args[0], ast.GeneratorExp):
            return "002"
    return None

def rule_list_membership_in_loop(node):
    """Detects membership checks on list-like literals inside loops (Tip 003)."""
    if _is_list_membership_check(node) and _has_ancestor(node, LOOP_NODES):
        return "003"
    return None

def rule_polling_loop(node):
    """Detects likely polling loops with sleep calls (Tip 006)."""
    if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True:
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and _call_name(child) == "sleep":
                return "006"
    return None

def rule_io_write_in_loop(node):
    """Detects writes performed one-by-one inside loops (Tip 007)."""
    if isinstance(node, ast.Call) and _has_ancestor(node, LOOP_NODES):
        if _call_name(node) in {"write", "send", "insert", "execute"}:
            return "007"
    return None

def rule_query_or_request_in_loop(node):
    """Detects repeated API/DB calls in loops (Tip 009)."""
    if isinstance(node, ast.Call) and _has_ancestor(node, LOOP_NODES):
        call_name = _call_name(node)
        if call_name in {"get", "post", "put", "delete", "request", "query", "fetch"}:
            return "009"
    return None

def rule_select_star_query(node):
    """Detects SELECT * SQL usage (Tip 010)."""
    query_text = _constant_string_arg(node)
    if query_text and "select *" in query_text.lower():
        return "010"
    return None

def rule_open_without_context_manager(node):
    """Detects open() calls not wrapped in with statements (Tip 013)."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
        if not _is_inside_with_context(node):
            return "013"
    return None

def rule_logging_in_loop(node):
    """Detects logging/printing in loops (Tip 021)."""
    if isinstance(node, ast.Call) and _has_ancestor(node, LOOP_NODES):
        call_name = _call_name(node)
        if call_name in {"print", "debug", "info", "warning", "error", "critical"}:
            return "021"
    return None

def rule_unbounded_read(node):
    """Detects reading entire files into memory (Tip 020)."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr == 'read' and not node.args:
            return "020"
    return None

ACTIVE_RULES = [
    rule_nested_loops,
    rule_eager_list_conversion,
    rule_list_membership_in_loop,
    rule_polling_loop,
    rule_io_write_in_loop,
    rule_query_or_request_in_loop,
    rule_select_star_query,
    rule_open_without_context_manager,
    rule_unbounded_read,
    rule_logging_in_loop,
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
        annotate_parents(tree)
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