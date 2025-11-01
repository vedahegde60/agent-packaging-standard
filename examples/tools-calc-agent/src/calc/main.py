import sys, json, math, ast, operator

# Safe eval using AST (only numbers and + - * / ** // % parentheses)
ALLOWED = {
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Load,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv,
    ast.USub, ast.UAdd, ast.Constant, ast.Tuple, ast.List, ast.Call, ast.Name
}
SAFE_FUNCS = {"sqrt": math.sqrt, "pow": pow, "abs": abs}
SAFE_NAMES = {"pi": math.pi, "e": math.e, **SAFE_FUNCS}

def safe_eval(expr: str):
    node = ast.parse(expr, mode="eval")
    for n in ast.walk(node):
        if type(n) not in ALLOWED:
            raise ValueError(f"Disallowed construct: {type(n).__name__}")
        if isinstance(n, ast.Call):
            if not isinstance(n.func, ast.Name) or n.func.id not in SAFE_FUNCS:
                raise ValueError("Only sqrt, pow, abs are allowed")
        if isinstance(n, ast.Name) and n.id not in SAFE_NAMES:
            raise ValueError(f"Unknown name: {n.id}")
    return eval(compile(node, "<expr>", "eval"), {"__builtins__": {}}, SAFE_NAMES)

def main():
    raw = sys.stdin.read().strip()
    if not raw:
        print(json.dumps({"status":"error","message":"Empty request"}))
        return
    try:
        req = json.loads(raw)
    except Exception as e:
        print(json.dumps({"status":"error","message":f"Invalid JSON: {e}"}))
        return

    expr = (req.get("inputs") or {}).get("expr", "")
    try:
        val = float(safe_eval(expr))
        print(json.dumps({"status":"ok","outputs":{"result": val}}))
    except Exception as e:
        print(json.dumps({"status":"error","message":str(e)}))

if __name__ == "__main__":
    main()
