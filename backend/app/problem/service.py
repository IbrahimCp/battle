import logging
import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO

from sqlalchemy.orm import Session

from app.problem.models import Problem
from app.storage import core as storage

logger = logging.getLogger(__name__)

def get_all(db_session: Session, skip: int = 0, limit: int = 50) -> list[Problem]:
    return db_session.query(Problem).offset(skip).limit(limit).all()


def get_by_id(db_session: Session, problem_id: int) -> Problem | None:
    return db_session.query(Problem).filter(Problem.id == problem_id).first()


def delete(db_session: Session, problem: Problem) -> None:
    logger.info("Deleting problem %d (%s)", problem.id, problem.short_name)
    storage.delete_prefix(f"problems/{problem.id}/")
    db_session.delete(problem)
    db_session.commit()


def get_statement(problem: Problem) -> str:
    """Read problem statement from statement-sections/english/ in MinIO."""
    prefix = f"problems/{problem.id}/statement-sections/english/"

    def read_file(filename: str) -> str:
        try:
            return storage.download(prefix + filename).decode("utf-8")
        except Exception as e:
            logger.debug("Statement file not found: %s%s (%s)", prefix, filename, e)
            return ""

    legend = read_file("legend.tex")
    input_spec = read_file("input.tex")
    output_spec = read_file("output.tex")
    notes = read_file("notes.tex")

    examples = []
    i = 1
    while True:
        ex_in = read_file(f"example.{i:02d}")
        if not ex_in:
            break
        ex_out = read_file(f"example.{i:02d}.a")
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
        if "problem.xml" not in zf.namelist():
            raise ValueError("problem.xml not found in package")

        meta = _parse_problem_xml(zf.read("problem.xml").decode("utf-8"))

        problem = Problem(
            short_name=meta["short_name"],
            title=meta["title"],
            time_limit=meta["time_limit"],
            memory_limit=meta["memory_limit"],
            test_count=meta["test_count"],
        )
        db_session.add(problem)
        db_session.flush()

        prefix = f"problems/{problem.id}/"
        files = [name for name in zf.namelist() if not name.endswith("/")]
        for name in files:
            storage.upload(prefix + name, zf.read(name))

        logger.info("Imported problem %d (%s): %d files uploaded", problem.id, meta["short_name"], len(files))

    db_session.commit()
    db_session.refresh(problem)
    return problem

def _parse_problem_xml(xml_content: str) -> dict:
    root = ET.fromstring(xml_content)

    short_name = root.get("short-name", "")

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

    test_count = 0
    tc_el = root.find(".//judging/testset/test-count")
    if tc_el is not None and tc_el.text:
        test_count = int(tc_el.text)

    return {
        "short_name": short_name,
        "title": title,
        "time_limit": time_limit,
        "memory_limit": memory_limit,
        "test_count": test_count,
    }
