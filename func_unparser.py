import ast
from typing import List, Iterable
import shelve
from functools import wraps


def shelve_cache(filename='cache_shelve.db'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args):
            with shelve.open(filename) as cache:
                key = str((func.__name__, args))
                if key in cache:
                    print("Výsledek z cache")
                    return cache[key]
                result = func(*args)
                cache[key] = result
                return result
        return wrapper
    return decorator


def find_top_level_functions(tree: ast.AST) -> List[ast.FunctionDef]:
    """
    Finds all top-level function definition nodes in the provided Python source code.

    Args:
        source_code (ast.AST): A AST tree of module

    Returns:
        List[ast.FunctionDef]: A list of AST nodes representing the top-level function definitions.
    """

    # List to collect top-level function nodes
    function_nodes: List[ast.FunctionDef] = []

    # Traverse the AST
    for node in ast.iter_child_nodes(tree):
        # Check if the node is a function definition
        if isinstance(node, ast.FunctionDef):
            function_nodes.append(node)

    return function_nodes


if __name__ == "__main__":
    # Example usage
    source_code = """
def foo():
    pass

def bar(x):
    return x * 2

def baz():
    return 42
    """

    # Find all top-level function definitions
    with open("func_unparser.py", "rt") as f:
        functions = find_top_level_functions(ast.parse(f.read()))

    for func in functions:
        print(func.name)
        print(ast.unparse(func))
