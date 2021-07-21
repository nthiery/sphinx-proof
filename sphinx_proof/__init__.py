# -*- coding: utf-8 -*-
"""
    sphinx_proof
    ~~~~~~~~~~~~

    A Sphinx extension for producing proofs, theorems, lemmas, etc.
"""
from pathlib import Path
from typing import Any, Dict, Set, Union
from sphinx.config import Config
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from .nodes import enumerable_node, visit_enumerable_node, depart_enumerable_node
from .nodes import unenumerable_node, visit_unenumerable_node, depart_unenumerable_node
from .nodes import proof_node, visit_proof_node, depart_proof_node
from .domain import ProofDomain
from sphinx.util import logging
from sphinx.util.fileutil import copy_asset


logger = logging.getLogger(__name__)


def purge_proofs(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    if not hasattr(env, "proof_list"):
        return

    # Override env.proof_list
    env.proof_list = {
        proof: env.proof_list[proof]
        for proof in env.proof_list.keys()
        if env.proof_list[proof]["docname"] != docname
    }


def merge_proofs(
    app: Sphinx, env: BuildEnvironment, docnames: Set[str], other: BuildEnvironment
) -> None:
    if not hasattr(env, "proof_list"):
        env.proof_list = {}

    # Merge env stored data
    if hasattr(other, "proof_list"):
        env.proof_list = {**env.proof_list, **other.proof_list}


def init_numfig(app: Sphinx, config: Config) -> None:
    """Initialize proof numfig format."""
    config["numfig"] = True
    numfig_format = {
        "proof": "Proof %s",
    }
    numfig_format.update(config.numfig_format)
    config.numfig_format = numfig_format


def copy_asset_files(app: Sphinx, exc: Union[bool, Exception]):
    static_path = Path(__file__).parent.joinpath("_static", "proof.css").absolute()
    asset_files = [str(static_path)]

    if exc is None:
        for path in asset_files:
            copy_asset(path, str(Path(app.outdir).joinpath("_static").absolute()))


def setup(app: Sphinx) -> Dict[str, Any]:

    app.add_css_file("proof.css")
    app.connect("build-finished", copy_asset_files)
    app.connect("config-inited", init_numfig)
    app.connect("env-purge-doc", purge_proofs)
    app.connect("env-merge-info", merge_proofs)

    app.add_domain(ProofDomain)
    app.add_node(
        proof_node,
        singlehtml=(visit_proof_node, depart_proof_node),
        html=(visit_proof_node, depart_proof_node),
        latex=(visit_proof_node, depart_proof_node)
    )
    app.add_node(
        unenumerable_node,
        singlehtml=(visit_unenumerable_node, depart_unenumerable_node),
        html=(visit_unenumerable_node, depart_unenumerable_node),
        latex=(visit_unenumerable_node, depart_unenumerable_node)
    )
    app.add_enumerable_node(
        enumerable_node,
        "proof",
        None,
        singlehtml=(visit_enumerable_node, depart_enumerable_node),
        html=(visit_enumerable_node, depart_enumerable_node),
        latex=(visit_enumerable_node, depart_enumerable_node)
    )

    return {
        "version": "builtin",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
