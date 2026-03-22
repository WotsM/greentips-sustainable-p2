import ast
from pathlib import Path

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
    if isinstance(node, LOOP_NODES):
        for child in node.body:
            if isinstance(child, LOOP_NODES):
                return "001"
    return None


def rule_eager_list_conversion(node):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id == "list" and node.args and isinstance(node.args[0], ast.GeneratorExp):
            return "002"
    return None


def rule_list_membership_in_loop(node):
    if _is_list_membership_check(node) and _has_ancestor(node, LOOP_NODES):
        return "003"
    return None


def rule_polling_loop(node):
    if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True:
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and _call_name(child) == "sleep":
                return "006"
    return None


def rule_io_write_in_loop(node):
    if isinstance(node, ast.Call) and _has_ancestor(node, LOOP_NODES):
        if _call_name(node) in {"write", "send", "insert", "execute"}:
            return "007"
    return None


def rule_query_or_request_in_loop(node):
    if isinstance(node, ast.Call) and _has_ancestor(node, LOOP_NODES):
        if _call_name(node) in {"get", "post", "put", "delete", "request", "query", "fetch"}:
            return "009"
    return None


def rule_select_star_query(node):
    query_text = _constant_string_arg(node)
    if query_text and "select *" in query_text.lower():
        return "010"
    return None


def rule_open_without_context_manager(node):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
        if not _is_inside_with_context(node):
            return "013"
    return None


def rule_logging_in_loop(node):
    if isinstance(node, ast.Call) and _has_ancestor(node, LOOP_NODES):
        if _call_name(node) in {"print", "debug", "info", "warning", "error", "critical"}:
            return "021"
    return None


def rule_unbounded_read(node):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr == "read" and not node.args:
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
    def __init__(self, tips_db):
        self.tips_db = tips_db
        self.warnings = []

    def generic_visit(self, node):
        for rule_function in ACTIVE_RULES:
            tip_id = rule_function(node)
            if tip_id:
                tip_data = next((tip for tip in self.tips_db if tip["id"] == tip_id), None)
                if tip_data:
                    self.warnings.append(
                        {
                            "line": getattr(node, "lineno", "Unknown"),
                            "data": tip_data,
                        }
                    )
        super().generic_visit(node)


def _python_files_in_target(target: Path):
    if target.is_file():
        return [target] if target.suffix.lower() == ".py" else []
    return sorted(path for path in target.rglob("*.py") if path.is_file())


def _analyze_python_file(filepath: Path, tips_db):
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None

    annotate_parents(tree)
    analyzer = ScalableAnalyzer(tips_db)
    analyzer.visit(tree)
    if analyzer.warnings:
        first_warning = analyzer.warnings[0]
        return {
            "file": filepath,
            "line": first_warning["line"],
            "tip": first_warning["data"],
        }
    return None


def analyze_python_target(target: Path, tips_db):
    for filepath in _python_files_in_target(target):
        result = _analyze_python_file(filepath, tips_db)
        if result is not None:
            return result
    return None
