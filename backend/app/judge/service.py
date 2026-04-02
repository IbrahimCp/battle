import logging
import os
from pathlib import Path

from sqlalchemy.orm import Session

from app.database.core import engine
from app.judge.client import GoJudgeClient, CompilationError
from app.judge.languages import LANG_CONFIGS
from app.problem.models import Problem, CheckerType
from app.submission.models import Submission, Verdict, SubmissionVerdictUpdate
from app.submission import service as submission_service

logger = logging.getLogger(__name__)

# Read testlib.h once at module level
_TESTLIB_PATH = Path(__file__).parent / "testlib.h"
_testlib_content: str | None = None


def _get_testlib() -> str:
    global _testlib_content
    if _testlib_content is None:
        _testlib_content = _TESTLIB_PATH.read_text()
    return _testlib_content


def _get_test_cases(problem: Problem) -> list[tuple[str, str]]:
    """Read test cases from problem storage (Polygon format: 01, 01.a, 02, 02.a, ...)."""
    tests_dir = os.path.join(problem.storage_path, "tests")
    cases = []
    i = 1
    while True:
        in_file = os.path.join(tests_dir, f"{i:02d}")
        out_file = os.path.join(tests_dir, f"{i:02d}.a")
        if not os.path.isfile(in_file) or not os.path.isfile(out_file):
            break
        with open(in_file) as f:
            input_data = f.read()
        with open(out_file) as f:
            expected_output = f.read()
        cases.append((input_data, expected_output))
        i += 1
    return cases


def _check_exact(participant: str, expected: str) -> bool:
    """Exact match: compare lines after stripping trailing whitespace."""
    p_lines = [line.rstrip() for line in participant.rstrip().splitlines()]
    e_lines = [line.rstrip() for line in expected.rstrip().splitlines()]
    return p_lines == e_lines


def judge_submission(submission_id: int) -> None:
    """Main judging entry point. Runs in a background thread."""
    with Session(engine) as db:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            logger.error(f"Submission {submission_id} not found")
            return
    
        problem = db.query(Problem).filter(Problem.id == submission.problem_id).first()
        if not problem:
            logger.error(f"Problem {submission.problem_id} not found")
            return

        verdict, time_used, memory_used = _judge(submission, problem)

        submission_service.update_verdict(
            db,
            submission,
            SubmissionVerdictUpdate(
                verdict=verdict,
                time_used=time_used,
                memory_used=memory_used,
            ),
        )


def _judge(
    submission: Submission, problem: Problem
) -> tuple[Verdict, float | None, int | None]:
    """Core judging logic. Returns (verdict, time_ms, memory_bytes)."""
    client = GoJudgeClient()
    language = submission.language

    # 1. Compile solution
    try:
        sol_file_ids, _ = client.compile(submission.source_code, language)
    except CompilationError:
        return Verdict.COMPILATION_ERROR, None, None

    # 2. Compile checker if special
    checker_file_ids = None
    if problem.checker_type == CheckerType.SPECIAL:
        checker_path = os.path.join(problem.storage_path, "check.cpp")
        if not os.path.isfile(checker_path):
            logger.error(f"Checker not found at {checker_path}")
            return Verdict.RUNTIME_ERROR, None, None

        with open(checker_path) as f:
            checker_source = f.read()

        try:
            checker_file_ids, _ = client.compile(
                checker_source,
                "cpp",
                extra_copy_in={"testlib.h": {"content": _get_testlib()}},
            )
        except CompilationError as e:
            logger.error(f"Checker compilation failed: {e.stderr}")
            return Verdict.RUNTIME_ERROR, None, None

    # 3. Run on each test case
    test_cases = _get_test_cases(problem)
    if not test_cases:
        logger.error(f"No test cases for problem {problem.id}")
        return Verdict.RUNTIME_ERROR, None, None

    max_time_ns = 0
    max_memory = 0

    for input_data, expected_output in test_cases:
        result = client.run(
            sol_file_ids, input_data, language,
            problem.time_limit, problem.memory_limit,
        )

        max_time_ns = max(max_time_ns, result.time_ns)
        max_memory = max(max_memory, result.memory_bytes)

        # Check for runtime errors (TLE, MLE, RTE)
        if result.verdict is not None:
            return result.verdict, max_time_ns / 1e6, max_memory // 1024

        # Check output correctness
        if problem.checker_type == CheckerType.SPECIAL:
            accepted = client.run_checker(
                checker_file_ids, input_data, result.stdout, expected_output
            )
        else:
            # exact match (also used for float — can be extended later)
            accepted = _check_exact(result.stdout, expected_output)

        if not accepted:
            return Verdict.WRONG_ANSWER, max_time_ns / 1e6, max_memory // 1024

    return Verdict.ACCEPTED, max_time_ns / 1e6, max_memory // 1024
