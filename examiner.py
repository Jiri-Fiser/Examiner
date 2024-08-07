import ast
import multiprocessing
import sys
from io import StringIO
from typing import Callable, Tuple, Any, Optional, Iterable
from ast import parse
from process import process, transform_etree_with_xslt, to_string
from lxml import etree as ET
from py_pyast import pyast_ns, qc_ns
from util import flatten


def func_id(id_val):
    def decorator(func):
        func.id = id_val
        return func
    return decorator


def runnable(code):
    # Zachování původního stdout
    original_stdout = sys.stdout
    # Vytvoření dočasného stdout
    temp_stdout = StringIO()
    sys.stdout = temp_stdout

    try:
        compiled_code = compile(code, filename="<ast>", mode="exec")
        # Spuštění skompilovaného kódu
        exec(compiled_code)
    except Exception as e:
        # Vrácení chyby, pokud se něco pokazí
        return False, ("EXCEPTION", repr(e)), code
    finally:
        # Obnovení původního stdout
        sys.stdout = original_stdout

    # Získání výstupu a jeho vrácení
    output = temp_stdout.getvalue()
    return False, ("NORMAL", output.strip()), code


def runnable_worker(code, queue):
    queue.put(runnable(code))


@func_id(("run status", "run output"))
def runnable_timeout(code, timeout = 3):
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=runnable_worker, args=(code, queue))

    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()  # Násilné ukončení procesu
        process.join()
        return False, ("TIMEOUT", queue.get(False)), code
    else:
        return queue.get()


@func_id("non empty lines")
def count_lines(code: str):
    count = sum(1 for line in code.splitlines() if line.strip() != "")
    return False, count, code

@func_id("non empty code")
def nonempty(code: str):
    if code.strip() == "":
        return True, False, None
    else:
        return False, True, code

@func_id("parsable to AST")
def parsable(code:str):
    try:
        ast = parse(code, type_comments=True)
        return False, True, ast
    except SyntaxError:
        return True, False, None


@func_id("transformation to QC")
def to_qc(ast):
    try:
        return False, True, process(ast)
    except:
        return True, False, None


@func_id("XSLT int metric")
def apply_xslt_int_metric(qc, xslt_file:str, params={}) -> Tuple[bool, int, Any]:
    return False, int(transform_etree_with_xslt(qc, xslt_file, params)), qc

@func_id("XSLT string")
def apply_xslt_str(qc, xslt_file:str, params={}) -> Tuple[bool, int, Any]:
    return False, str(transform_etree_with_xslt(qc, xslt_file, params)), qc


class Examiner:
    def __init__(self, tests: Optional[Iterable[Callable[[Any], Tuple[bool, Any, Any]]]] = None):
        if tests is None:
            self.tests = []
            self._header = []
        else:
            self.tests = tests
            self._header = [f.id for f in tests]
        self.qc = None

    @property
    def header(self):
        return list(flatten(self._header))

    def add_test(self, test: Callable[[Any], Tuple[bool, Any, Any]],
                 dsc:str = None):
        self.tests.append(test)
        if dsc:
            self._header.append(dsc)
        else:
            self._header.append(test.id)

    def __len__(self):
        return len(self.tests)

    def exam(self, code:str):
        self.qc = None
        next_input = code
        results = [None] * len(self)
        for i, test in enumerate(self.tests):
            stop, results[i], next_input = test(next_input)
            if (not isinstance(next_input, str) and
                    not isinstance(next_input, ast.Module) and self.qc is None):
                self.qc = next_input
            if stop:
                break
        return list(flatten(results))


test_prog = """
def g():
    for i in range(2):
        for j in range(2):
            k = 0
            while(k < 2):
                print(i,j)
                k += 1
def f():
    pass
"""
if __name__ == "__main__":
    ex = Examiner([nonempty, parsable, runnable_timeout, to_qc])
    ex.add_test(lambda qc: apply_xslt_int_metric(qc, "maxdepth.xslt"), "max tree depth")
    ex.add_test(lambda qc: apply_xslt_int_metric(qc, "tags_depth.xslt",
                                                 {"class": ET.XSLT.strparam("loop")}), "max depth of loops")
    ex.add_test(lambda qc: apply_xslt_int_metric(qc, "element_count.xslt",
                {"name": ET.XSLT.strparam("foreach"), "ns": ET.XSLT.strparam(qc_ns)}), "count of foreach")
    ex.add_test(lambda qc: apply_xslt_str(qc, "xpath_str_aggregate.xslt",
                                {"xp": f"//*[namespace-uri()='{qc_ns}' and local-name()='function']/@name"}),
                "defined function")
    print(ex.header)
    print(ex.exam(test_prog))
    #print(ex.exam("import time; time.sleep(5)"))
    print(ex.exam("input('a')"))
    print(ex.exam("print('a' + 'b')"))
    print(ex.exam("print(a)"))
    print(ex.exam("print('a'"))