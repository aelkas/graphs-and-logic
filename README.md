# graphs-and-logic

Python tools for open directed graphs, and Boolean circuits built on top of them.

Graphs come first: nodes, degrees, path lengths, topological sort, and composition
of graphs in parallel or in sequence. Boolean circuits are then a specialization of
that structure — gates are nodes, wires are edges — so circuit simplification and
evaluation become graph rewriting rather than separate machinery.

<!-- EDIT: gifImages/g_half.gif shows a half-adder evaluating step by step.
     Embed it right here. It is the best thing in this repo and nobody sees it. -->

## What it does

- **Open digraphs** — node and edge management, degrees, path lengths, topological
  sort, parallel and sequential composition.
- **Boolean circuits** — identity circuits, encoders and decoders, registers, bit
  perturbators, and random circuit generation.
- **Adders** — half adders, full adders, and carry-lookahead (CLA) adders, usable
  for addition on integers of arbitrary size.
- **Evaluation and simplification** — `evaluate` propagates constants through the
  circuit; `transform_circuit` applies rewriting rules until the circuit reaches a
  fixed point.
- **Applications** — arbitrary-size addition, checking the Hamming code property,
  and statistics on how far random circuits simplify.

## The design decision worth knowing about

The obvious way to write `evaluate` and `transform_circuit` is a long chain of
`if` statements on the circuit, checking every recognizable gate configuration.
That grows badly and becomes unreadable.

Instead `circuit_node` is an abstract class, and each gate type — constants, unary
and binary gates — is a specialization implementing its own `transform`. The
circuit iterates and delegates: each node recognizes the patterns that concern it
and reports whether it applied a rewrite, which also gives the loop its stopping
condition. Pattern matching lives with the node type it belongs to instead of in
one growing function.

Larger classes are split across files using mixins so `open_digraph` and
`bool_circ` stay readable as they grow. The UML diagram in the report shows the
full structure.

## Layout

```
modules/     node, open_digraph, bool_circ, gate transformations, adders, mixins
tests/       unit tests
worksheet.py entry point
gifImages/   UML diagram and animations of circuits evaluating
```

## Running it

```bash
git clone https://github.com/aelkas/graphs-and-logic
cd graphs-and-logic
python worksheet.py
```

## Full write-up

[**Boolean Circuits and Graph Operations — project report**](Boolean_Circuits_and_Graph_Operations_Report.md)
covers the architecture, the transformation and evaluation rules, the adder
constructions, and the Hamming code work in detail, with worked examples.

---

Built during the L2 double degree in Mathematics and Computer Science,
Université Paris-Saclay.

