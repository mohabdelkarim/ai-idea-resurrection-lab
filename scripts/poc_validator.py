"""poc_validator.py

Language-aware syntax / parse gate for generated PoCs.
No network access and no arbitrary execution beyond compiler front-ends.
"""
from __future__ import annotations

import logging
import os
import py_compile
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

LOGGER = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = frozenset({"python", "typescript", "javascript", "go", "rust"})


@dataclass(frozen=True)
class PocValidationResult:
    ok: bool
    language: str
    error: str = ""


def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 60) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as err:
        return 127, str(err)
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s"
    stderr = (completed.stderr or "").strip()
    stdout = (completed.stdout or "").strip()
    detail = stderr or stdout
    return completed.returncode, detail


def _validate_python(code: str) -> PocValidationResult:
    with tempfile.TemporaryDirectory(prefix="poc_py_") as tmp:
        path = Path(tmp) / "main.py"
        path.write_text(code, encoding="utf-8")
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as err:
            return PocValidationResult(False, "python", str(err))
    return PocValidationResult(True, "python")


def _validate_node(code: str, language: str) -> PocValidationResult:
    if shutil.which("node") is None:
        return PocValidationResult(False, language, "node binary not available")
    with tempfile.TemporaryDirectory(prefix="poc_js_") as tmp:
        ext = ".ts" if language == "typescript" else ".js"
        path = Path(tmp) / f"main{ext}"
        path.write_text(code, encoding="utf-8")
        # node --check works for JS; for TS we still use --check which parses as JS
        # unless the file uses TS-only syntax that breaks parse — acceptable gate.
        code_rc, detail = _run(["node", "--check", str(path)])
        if code_rc != 0:
            return PocValidationResult(False, language, detail or f"exit {code_rc}")
    return PocValidationResult(True, language)


def _validate_go(code: str) -> PocValidationResult:
    if shutil.which("go") is None:
        return PocValidationResult(False, "go", "go binary not available")
    with tempfile.TemporaryDirectory(prefix="poc_go_") as tmp:
        root = Path(tmp)
        (root / "go.mod").write_text("module poc\n\ngo 1.22\n", encoding="utf-8")
        (root / "main.go").write_text(code, encoding="utf-8")
        env = os.environ.copy()
        env["GO111MODULE"] = "on"
        try:
            completed = subprocess.run(
                ["go", "build", "-o", os.devnull, "."],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
                env=env,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as err:
            return PocValidationResult(False, "go", str(err))
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            return PocValidationResult(False, "go", detail or f"exit {completed.returncode}")
    return PocValidationResult(True, "go")


def _validate_rust(code: str) -> PocValidationResult:
    if shutil.which("rustc") is None:
        return PocValidationResult(False, "rust", "rustc binary not available")
    with tempfile.TemporaryDirectory(prefix="poc_rs_") as tmp:
        path = Path(tmp) / "lib.rs"
        path.write_text(code, encoding="utf-8")
        out = Path(tmp) / "lib.rlib"
        code_rc, detail = _run(
            ["rustc", "--edition", "2021", "--crate-type", "lib", str(path), "-o", str(out)],
            timeout=90,
        )
        if code_rc != 0:
            return PocValidationResult(False, "rust", detail or f"exit {code_rc}")
    return PocValidationResult(True, "rust")


def validate_poc_code(code: str, language: str) -> PocValidationResult:
    """
    Validate PoC source for the given language.
    Returns ok=False with an error message when validation fails or language is unsupported.
    """
    lang = str(language or "").strip().lower()
    source = str(code or "").strip()
    if not source:
        return PocValidationResult(False, lang or "unknown", "empty PoC code")
    if lang not in SUPPORTED_LANGUAGES:
        return PocValidationResult(
            False,
            lang or "unknown",
            f"unsupported PoC language '{lang}' — ship analysis/RFC only",
        )

    if lang == "python":
        result = _validate_python(source)
    elif lang in {"typescript", "javascript"}:
        result = _validate_node(source, lang)
    elif lang == "go":
        result = _validate_go(source)
    elif lang == "rust":
        result = _validate_rust(source)
    else:
        result = PocValidationResult(False, lang, f"no validator for {lang}")

    if result.ok:
        LOGGER.info("[PoCValidator] %s PoC passed syntax gate.", lang)
    else:
        LOGGER.warning("[PoCValidator] %s PoC failed: %s", lang, result.error[:400])
    return result
