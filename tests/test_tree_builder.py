"""Tests for ecrstudio.tree_builder module."""

from ecrstudio.tree_builder import build_tree, TreeNode


class TestBuildTree:
    """Tests for build_tree function."""

    def test_single_ver(self):
        lines = ["VER   0200000"]
        roots = build_tree(lines)
        assert len(roots) == 1
        assert roots[0].record_type == "VER"

    def test_hierarchy_ver_dos_exo(self):
        lines = [
            "VER   0200000000000000000000          Test                      0",
            "DOS   TEST    Dossier test",
            "EXO   010120253112202500           EUR",
        ]
        roots = build_tree(lines)
        assert len(roots) == 1
        ver = roots[0]
        assert ver.record_type == "VER"
        assert len(ver.children) == 1
        dos = ver.children[0]
        assert dos.record_type == "DOS"
        assert len(dos.children) == 1
        exo = dos.children[0]
        assert exo.record_type == "EXO"

    def test_full_hierarchy(self, minimal_lines):
        roots = build_tree(minimal_lines)
        assert len(roots) == 1
        ver = roots[0]
        # VER > DOS > EXO > ECR > 2 MVT
        dos = ver.children[0]
        exo = dos.children[0]
        assert len(exo.children) == 1  # 1 ECR
        ecr = exo.children[0]
        assert ecr.record_type == "ECR"
        assert len(ecr.children) == 2  # 2 MVT
        for mvt in ecr.children:
            assert mvt.record_type == "MVT"

    def test_parent_reference(self, minimal_lines):
        roots = build_tree(minimal_lines)
        dos = roots[0].children[0]
        assert dos.parent == roots[0]
        exo = dos.children[0]
        assert exo.parent == dos

    def test_line_index_tracking(self, minimal_lines):
        roots = build_tree(minimal_lines)
        assert roots[0].line_index == 0
        dos = roots[0].children[0]
        assert dos.line_index == 1

    def test_empty_lines(self):
        roots = build_tree([])
        assert roots == []

    def test_label_contains_type(self, minimal_lines):
        roots = build_tree(minimal_lines)
        assert "VER" in roots[0].label


class TestTreeNode:
    """Tests for TreeNode class."""

    def test_add_child(self):
        parent = TreeNode(0, "VER", "VER node")
        child = TreeNode(1, "DOS", "DOS node")
        parent.add_child(child)
        assert child in parent.children
        assert child.parent == parent

    def test_initial_state(self):
        node = TreeNode(5, "ECR", "ECR label")
        assert node.line_index == 5
        assert node.record_type == "ECR"
        assert node.label == "ECR label"
        assert node.children == []
        assert node.parent is None
