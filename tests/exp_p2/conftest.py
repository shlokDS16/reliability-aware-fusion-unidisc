"""Shared fixtures for the Paper 2 tests. The dirty-tree guard (delta audit N4) asks git about the real checkout, which is legitimately dirty while code is being edited, so every
test sees a clean tree unless it exercises the guard itself (those tests call `pins.git_dirty` on a temporary repository or patch `pins.dirty_files` explicitly)."""
import pytest


@pytest.fixture(autouse=True)
def _clean_tree(monkeypatch):
    from exp_p2.gate import pins
    monkeypatch.setattr(pins, "dirty_files", lambda: [])
