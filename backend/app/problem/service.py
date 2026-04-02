import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO

from sqlalchemy.orm import Session

from app.config import PROBLEMS_STORAGE_PATH
from app.problem.models import Problem, CheckerType


def get_all(db_session: Session, skip: int = 0, limit: int = 50) -> list[Problem]:
    return db_session.query(Problem).offset(skip).limit(limit).all()


def get_by_id(db_session: Session, problem_id: int) -> Problem | None:
    return db_session.query(Problem).filter(Problem.id == problem_id).first()


def delete(db_session: Session, problem: Problem) -> None:
    if problem.storage_path and os.path.isdir(problem.storage_path):
        shutil.rmtree(problem.storage_path, ignore_errors=True)
    db_session.delete(problem)
    db_session.commit()


def get_test_count(problem: Problem) -> int:
    """Count test cases in polygon format (01, 01.a, 02, 02.a, ...)."""
    tests_dir = os.path.join(problem.storage_path, "tests")
    if not os.path.isdir(tests_dir):
        return 0
    count = 0
    i = 1
    while True:
        if not os.path.isfile(os.path.join(tests_dir, f"{i:02d}")):
            break
        count += 1
        i += 1
    return count


def get_statement(problem: Problem) -> str:
    """Read problem statement from statement-sections/english/ on disk."""
    sections_dir = os.path.join(problem.storage_path, "statement-sections", "english")
    if not os.path.isdir(sections_dir):
        return ""

    def read_file(filename: str) -> str:
        path = os.path.join(sections_dir, filename)
        if os.path.isfile(path):
            with open(path) as f:
                return f.read().strip()
        return ""

    legend = read_file("legend.tex")
    input_spec = read_file("input.tex")
    output_spec = read_file("output.tex")
    notes = read_file("notes.tex")

    examples = []
    i = 1
    while True:
        ex_in_path = os.path.join(sections_dir, f"example.{i:02d}")
        if not os.path.isfile(ex_in_path):
            break
        with open(ex_in_path) as f:
            ex_in = f.read().strip()
        ex_out = ""
        ex_out_path = os.path.join(sections_dir, f"example.{i:02d}.a")
        if os.path.isfile(ex_out_path):
            with open(ex_out_path) as f:
                ex_out = f.read().strip()
        examples.append((ex_in, ex_out))
        i += 1

    parts = []
    if legend:
        parts.append(legend)
    if input_spec:
        parts.append(f"\\textbf{{Input}}\n\n{input_spec}")
    if output_spec:
        parts.append(f"\\textbf{{Output}}\n\n{output_spec}")
    if examples:
        ex_parts = []
        for idx, (ein, eout) in enumerate(examples, 1):
            ex_parts.append(f"\\textbf{{Example {idx}}}\n\nInput:\n{ein}\n\nOutput:\n{eout}")
        parts.append("\n\n".join(ex_parts))
    if notes:
        parts.append(f"\\textbf{{Note}}\n\n{notes}")

    return "\n\n".join(parts)


def import_polygon_package(db_session: Session, zip_bytes: bytes) -> Problem:
    """Import a Codeforces Polygon full problem package from a zip file."""
    with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
        names = zf.namelist()
        root_prefix = _find_package_root(names)

        xml_path = root_prefix + "problem.xml"
        if xml_path not in names:
            raise ValueError("problem.xml not found in package")

        meta = _parse_problem_xml(zf.read(xml_path).decode("utf-8"))

        checker_type = CheckerType.EXACT
        if (root_prefix + "check.cpp") in names or (root_prefix + "files/check.cpp") in names:
            checker_type = CheckerType.SPECIAL

        problem = Problem(
            title=meta["title"],
            time_limit=meta["time_limit"],
            memory_limit=meta["memory_limit"],
            checker_type=checker_type,
            storage_path="",
        )
        db_session.add(problem)
        db_session.flush()

        storage_path = os.path.join(PROBLEMS_STORAGE_PATH, str(problem.id))
        os.makedirs(storage_path, exist_ok=True)
        problem.storage_path = storage_path

        # Extract entire package
        for member in names:
            if member.endswith("/") or not member.startswith(root_prefix):
                continue
            rel_path = member[len(root_prefix):]
            if rel_path.startswith("__") or "/__" in rel_path:
                continue
            dest = os.path.join(storage_path, rel_path)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(zf.read(member))

    db_session.commit()
    db_session.refresh(problem)
    return problem


def _find_package_root(names: list[str]) -> str:
    if "problem.xml" in names:
        return ""
    for name in names:
        if name.endswith("/problem.xml"):
            parts = name.split("/")
            if len(parts) == 2:
                return parts[0] + "/"
    for name in names:
        if name.endswith("problem.xml"):
            return name[: -len("problem.xml")]
    return ""


def _parse_problem_xml(xml_content: str) -> dict:
    root = ET.fromstring(xml_content)

    title = ""
    for name_el in root.findall(".//names/name"):
        if name_el.get("language") == "english":
            title = name_el.get("value", "")
            break
    if not title:
        name_el = root.find(".//names/name")
        if name_el is not None:
            title = name_el.get("value", "")
    
    time_limit = 1.0
    tl_el = root.find(".//judging/testset/time-limit")
    if tl_el is not None and tl_el.text:
        time_limit = int(tl_el.text) / 1000.0

    memory_limit = 256
    ml_el = root.find(".//judging/testset/memory-limit")
    if ml_el is not None and ml_el.text:
        memory_limit = int(ml_el.text) // (1024 * 1024)

    return {"title": title, "time_limit": time_limit, "memory_limit": memory_limit}
