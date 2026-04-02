from dataclasses import dataclass

import httpx

from app.config import JUDGE_SERVER_URL
from app.submission.models import Language, Verdict
from app.judge.languages import LANG_CONFIGS


@dataclass
class RunResult:
    verdict: Verdict
    stdout: str
    stderr: str
    time_ns: int
    memory_bytes: int


# go-judge status string → our Verdict
_STATUS_MAP = {
    "Accepted": None,  # need to check output separately
    "Time Limit Exceeded": Verdict.TIME_LIMIT,
    "Memory Limit Exceeded": Verdict.MEMORY_LIMIT,
    "Output Limit Exceeded": Verdict.MEMORY_LIMIT,
    "Runtime Error (NZEC)": Verdict.RUNTIME_ERROR,
    "Runtime Error (Signal)": Verdict.RUNTIME_ERROR,
    "Internal Error": Verdict.RUNTIME_ERROR,
}


class GoJudgeClient:
    def __init__(self):
        self._url = f"{JUDGE_SERVER_URL}/run"
        self._client = httpx.Client(timeout=120)

    def compile(
        self,
        source_code: str,
        language: Language,
        extra_copy_in: dict | None = None,
    ) -> tuple[dict, str]:
        """Compile source code. Returns (copyOutCached fileIds dict, stderr).
        Raises CompilationError if compilation fails."""
        cfg = LANG_CONFIGS[language]
        if cfg.compile_args is None:
            # Interpreted language — no compilation, return source as cached file
            resp = self._post({
                "cmd": [{
                    "args": ["/bin/true"],
                    "env": cfg.env,
                    "files": [{"content": ""}, {"name": "stdout", "max": 1}, {"name": "stderr", "max": 1}],
                    "cpuLimit": 5_000_000_000,
                    "memoryLimit": 256 * 1024 * 1024,
                    "procLimit": 1,
                    "copyIn": {cfg.source_file: {"content": source_code}},
                    "copyOutCached": [cfg.source_file],
                }]
            })
            return resp[0].get("fileIds", {}), ""

        copy_in = {cfg.source_file: {"content": source_code}}
        if extra_copy_in:
            copy_in.update(extra_copy_in)

        resp = self._post({
            "cmd": [{
                "args": cfg.compile_args,
                "env": cfg.env,
                "files": [
                    {"content": ""},
                    {"name": "stdout", "max": 10240},
                    {"name": "stderr", "max": 10240},
                ],
                "cpuLimit": 10_000_000_000,
                "memoryLimit": 256 * 1024 * 1024,
                "procLimit": 50,
                "copyIn": copy_in,
                "copyOutCached": [cfg.binary_file],
            }]
        })

        result = resp[0]
        stderr = result.get("files", {}).get("stderr", "")

        if result.get("status") != "Accepted":
            raise CompilationError(stderr)

        return result.get("fileIds", {}), stderr

    def run(
        self,
        file_ids: dict,
        stdin: str,
        language: Language,
        time_limit_s: float,
        memory_limit_mb: int,
    ) -> RunResult:
        """Run a compiled binary with given stdin. Returns RunResult."""
        cfg = LANG_CONFIGS[language]

        copy_in = {}
        for name, fid in file_ids.items():
            copy_in[name] = {"fileId": fid}

        resp = self._post({
            "cmd": [{
                "args": cfg.run_args,
                "env": cfg.env,
                "files": [
                    {"content": stdin},
                    {"name": "stdout", "max": 256 * 1024 * 1024},
                    {"name": "stderr", "max": 10240},
                ],
                "cpuLimit": int(time_limit_s * 1_000_000_000),
                "memoryLimit": memory_limit_mb * 1024 * 1024,
                "procLimit": 50,
                "copyIn": copy_in,
            }]
        })

        result = resp[0]
        status = result.get("status", "")
        verdict = _STATUS_MAP.get(status, Verdict.RUNTIME_ERROR)

        return RunResult(
            verdict=verdict,
            stdout=result.get("files", {}).get("stdout", ""),
            stderr=result.get("files", {}).get("stderr", ""),
            time_ns=result.get("time", 0),
            memory_bytes=result.get("memory", 0),
        )

    def run_checker(
        self,
        checker_file_ids: dict,
        input_data: str,
        participant_output: str,
        expected_output: str,
    ) -> bool:
        """Run a testlib checker. Returns True if accepted."""
        copy_in = {}
        for name, fid in checker_file_ids.items():
            copy_in[name] = {"fileId": fid}

        copy_in["input.txt"] = {"content": input_data}
        copy_in["output.txt"] = {"content": participant_output}
        copy_in["answer.txt"] = {"content": expected_output}

        resp = self._post({
            "cmd": [{
                "args": ["checker", "input.txt", "output.txt", "answer.txt"],
                "env": ["PATH=/usr/bin:/bin"],
                "files": [
                    {"content": ""},
                    {"name": "stdout", "max": 10240},
                    {"name": "stderr", "max": 10240},
                ],
                "cpuLimit": 10_000_000_000,
                "memoryLimit": 256 * 1024 * 1024,
                "procLimit": 10,
                "copyIn": copy_in,
            }]
        })

        result = resp[0]
        return result.get("exitStatus", 1) == 0

    def _post(self, body: dict) -> list[dict]:
        resp = self._client.post(self._url, json=body)
        resp.raise_for_status()
        return resp.json()


class CompilationError(Exception):
    def __init__(self, stderr: str):
        self.stderr = stderr
        super().__init__(stderr)
