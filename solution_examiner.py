import csv

from lxml import etree

from examiner import Examiner, nonempty, count_lines, parsable, runnable_timeout, to_qc, apply_xslt_int_metric, apply_xslt_str
from py_pyast import qc_ns

def process(xml_file, solution_header, result_csv, codes_file):
    tree = etree.parse(xml_file)
    root = tree.getroot()

    header = ["task"] + solution_header

    ex = Examiner([nonempty, count_lines, parsable, runnable_timeout, to_qc])
    ex.add_test(lambda qc: apply_xslt_int_metric(qc, "maxdepth.xslt"), "max tree depth")
    ex.add_test(lambda qc: apply_xslt_int_metric(qc, "tags_depth.xslt",
                                                 {"tag": etree.XSLT.strparam("loop")}), "max depth of loops")
    ex.add_test(lambda qc: apply_xslt_int_metric(qc, "element_count.xslt",
                    {"name": etree.XSLT.strparam("foreach"), "ns": etree.XSLT.strparam(qc_ns)}), "foreach")
    ex.add_test(lambda qc: apply_xslt_int_metric(qc, "element_count.xslt",
                    {"name": etree.XSLT.strparam("interpolated_string"), "ns": etree.XSLT.strparam(qc_ns)}),
                     "interpolated strings")
    ex.add_test(lambda qc: apply_xslt_str(qc, "xpath_str_aggregate.xslt",
                                    {"xp": f"//*[namespace-uri()='{qc_ns}' and local-name()='function']/@name"}),
                "defined functions")
    ex.add_test(lambda qc: apply_xslt_str(qc, "xpath_str_aggregate.xslt",
                                    {"xp": f"//*[namespace-uri()='{qc_ns}' and local-name()='call']/@name"}),
                "called functions and methods")
    ex.add_test(lambda qc: apply_xslt_int_metric(qc, "tags_count.xslt",
                                                 {"tag": etree.XSLT.strparam("boolean")}),
                                                 "number of boolean operators")
    ex.add_test(lambda qc: apply_xslt_int_metric(qc, "element_count.xslt",
                    {"name": etree.XSLT.strparam("comprehension"), "ns": etree.XSLT.strparam(qc_ns)}),
                     "number of comprehensions")
    header += ex.header

    with (open(result_csv, mode='w', newline='', encoding='utf-8') as file,
          open(codes_file, mode="wt") as codes
          ):
        writer = csv.writer(file)

        writer.writerow(header)
        for task in root.findall('.//Task'):
            taskid = task.get('id')

            for solution in task.xpath("*[local-name() = 'solution' or local-name() = 'Solution']"):
                ids = [taskid] + [solution.get(name) for name in solution_header]
                print(ids)
                code = solution.text
                result = ex.exam(code)
                writer.writerow(ids + result)
                if result[2]:
                    print(ids, file=codes)
                    print(code, file=codes)
                    print("-" * 40, file=codes)

#process("solutions.xml", ["group", "version", "student"], "result.csv", "codes.py")

process("projects.xml", ["group", "class", "student_name"], "projects_result.csv",
        "projects_code.py")