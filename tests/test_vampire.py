import subprocess
import sys
from pathlib import Path

from vampire import vampire_path

if sys.platform == "win32":
    assert Path(vampire_path).suffix == ".exe", vampire_path
    assert Path(vampire_path).with_name("cygwin1.dll").is_file()

version = subprocess.run(
    [vampire_path, "--version"],
    check=True,
    text=True,
    capture_output=True,
    timeout=30,
)
assert "Vampire 5.1.0" in version.stdout, version.stdout
assert "Linked to Z3" in version.stdout, version.stdout

problems = [
    """\
fof(fact, axiom, p(a)).
fof(goal, conjecture, p(a)).
""",
    """\
thf(goal, conjecture, ![X: $i]: (((^[Y: $i]: Y) @ X) = X)).
""",
]

for problem in problems:
    result = subprocess.run(
        [vampire_path, "--mode", "casc", "--time_limit", "5"],
        input=problem,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "SZS status Theorem" in result.stdout, result.stdout

result = subprocess.run(
    [vampire_path, "--sat_solver", "z3", "--input_syntax", "smtlib2",
     "--output_mode", "smtcomp", "--time_limit", "5"],
    input="""\
(set-logic QF_LIA)
(declare-const x Int)
(assert (> x 1))
(assert (< x 0))
(check-sat)
""",
    text=True,
    capture_output=True,
    timeout=30,
)
assert result.returncode == 0, result.stderr + result.stdout
assert "unsat" in result.stdout.splitlines(), result.stdout
