"""Checks that the built book actually rendered its Python code.

Run after `jupyter-book build pygis` (the GitHub Actions workflow in
.github/workflows/book.yml does this before deploying):

    python -m pytest tests

These tests read the HTML in pygis/_build/html and fail if a page is missing,
if any {code-cell} from the source didn't make it into the HTML, if a notebook
failed to execute, or if a page that is supposed to be executed came out with
no outputs at all.
"""

import fnmatch
import re
from pathlib import Path

import pytest
import yaml
from bs4 import BeautifulSoup

BOOK = Path(__file__).resolve().parents[1] / "pygis"
HTML = BOOK / "_build" / "html"

# Up to 3 spaces of indentation is still a fence in MyST/CommonMark.
CODE_CELL = re.compile(r"^ {0,3}```+\{code-cell\}", re.MULTILINE)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def _toc_files():
    """Every page listed in _toc.yml, e.g. 'docs/e_extraction'."""
    toc = yaml.safe_load((BOOK / "_toc.yml").read_text())
    files = [toc["root"]]
    for part in toc.get("parts", []):
        for chapter in part.get("chapters", []):
            files.append(chapter["file"])
            files.extend(s["file"] for s in chapter.get("sections", []))
    return files


def _exclude_patterns():
    config = yaml.safe_load((BOOK / "_config.yml").read_text())
    return config.get("execute", {}).get("exclude_patterns", []) or []


def _is_executed(page):
    name = Path(page).name
    return not any(fnmatch.fnmatch(name, pat) for pat in _exclude_patterns())


def _source(page):
    """Page source with HTML comments (commented-out cells) removed."""
    return HTML_COMMENT.sub("", (BOOK / f"{page}.md").read_text())


def _soup(page):
    return BeautifulSoup((HTML / f"{page}.html").read_text(), "html.parser")


TOC = _toc_files()
CODE_PAGES = [
    p for p in TOC
    if (BOOK / f"{p}.md").exists() and CODE_CELL.search(_source(p))
]
EXECUTED = [p for p in CODE_PAGES if _is_executed(p)]


@pytest.fixture(scope="session", autouse=True)
def _built():
    if not (HTML / "index.html").exists():
        pytest.fail(f"No built book at {HTML}; run `jupyter-book build pygis` first")


@pytest.mark.parametrize("page", TOC)
def test_page_built(page):
    assert (HTML / f"{page}.html").exists(), f"{page}.html was not generated"


@pytest.mark.parametrize("page", CODE_PAGES)
def test_every_code_cell_rendered(page):
    """Each {code-cell} in the .md must appear as a code cell in the HTML."""
    expected = len(CODE_CELL.findall(_source(page)))
    cells = _soup(page).select("div.cell")
    assert len(cells) == expected, (
        f"{page}: source has {expected} code cells, HTML has {len(cells)}"
    )
    empty = [i for i, c in enumerate(cells) if not c.select_one("div.cell_input pre")]
    assert not empty, f"{page}: code cells {empty} rendered without their source code"


def test_no_execution_failure_reports():
    """Jupyter Book writes a report for each notebook that failed to execute."""
    reports = HTML / "reports"
    failed = sorted(str(p.relative_to(reports)) for p in reports.rglob("*") if p.is_file())
    assert not failed, f"Notebook execution failed, see _build/html/reports: {failed}"


@pytest.mark.parametrize("page", EXECUTED)
def test_executed_page_has_outputs(page):
    cells = _soup(page).select("div.cell")
    assert any(c.select_one("div.cell_output") for c in cells), (
        f"{page} should be executed but none of its code cells produced output"
    )


@pytest.mark.parametrize("page", EXECUTED)
def test_no_tracebacks_in_outputs(page):
    bad = [
        i for i, c in enumerate(_soup(page).select("div.cell"))
        if "tag_raises-exception" not in c.get("class", [])
        and c.select_one("div.cell_output .traceback, div.cell_output .highlight-ipythontb")
    ]
    assert not bad, f"{page}: code cells {bad} rendered an error traceback"
