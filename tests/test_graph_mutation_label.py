"""The graph detail panel must say outright that a mutation's text is the
false or distorted version (charter 5; EV-02 printed a false accusation about
two election workers under a bare "Mutated" label, 2026-11-12)."""
import re
from pathlib import Path

BUILD_JS = Path(__file__).resolve().parent.parent / "gallery" / "build.js"
LABEL = "Distorted version (false or misleading as it spread)"


def _mutation_branch():
    src = BUILD_JS.read_text(encoding="utf-8")
    m = re.search(r"node_type === 'mutation'\) \{(.*?)\n\s*\} else if", src, re.S)
    assert m, "mutation branch not found in build.js"
    return m.group(1)


def test_mutated_text_is_labelled_false_or_distorted():
    assert f"detailField('{LABEL}', d.mutated)" in _mutation_branch()


def test_bare_mutated_label_is_gone():
    assert "detailField('Mutated'" not in _mutation_branch()
