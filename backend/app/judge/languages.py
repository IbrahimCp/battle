from dataclasses import dataclass

from app.submission.models import Language


@dataclass(frozen=True)
class LangConfig:
    source_file: str
    binary_file: str | None  # None = interpreted
    compile_args: list[str] | None  # None = no compilation
    run_args: list[str]
    env: list[str]


LANG_CONFIGS: dict[Language, LangConfig] = {
    Language.CPP: LangConfig(
        source_file="sol.cpp",
        binary_file="sol",
        compile_args=["/usr/bin/g++", "-O2", "-o", "sol", "sol.cpp"],
        run_args=["sol"],
        env=["PATH=/usr/bin:/bin"],
    ),
    Language.PYTHON: LangConfig(
        source_file="sol.py",
        binary_file=None,
        compile_args=None,
        run_args=["/usr/bin/python3", "sol.py"],
        env=["PATH=/usr/bin:/bin", "PYTHONIOENCODING=utf-8"],
    ),
    Language.JAVA: LangConfig(
        source_file="Sol.java",
        binary_file="Sol.class",
        compile_args=["/usr/bin/javac", "Sol.java"],
        run_args=["/usr/bin/java", "-cp", ".", "Sol"],
        env=["PATH=/usr/bin:/bin"],
    ),
}
