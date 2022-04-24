import re
from typing import Optional

from graphviz import Digraph

from minimata import StateMachine, Transition


def state_machine_to_svg(
    state_machine: StateMachine,
    title: Optional[str] = None,
    current_state: Optional[str] = None,
):
    digraph = Digraph(
        title,
        node_attr={"shape": "box", "style": "rounded,filled"},
    )
    digraph.graph_attr["rankdir"] = "TB"

    transitions = state_machine.transitions

    # Draw transitions
    for tr in transitions:
        digraph.edge(
            tr.previous_state,
            tr.next_state,
            label=transition_label(tr),
        )

    srcs = {tr.previous_state for tr in transitions}
    dests = {tr.next_state for tr in transitions}
    states = srcs.union(dests)

    # Color entry states
    for state in states:
        if state not in dests:
            digraph.node(state, fillcolor="deepskyblue")

    # Color terminal states
    for state in states:
        if state not in srcs:
            digraph.node(state, fillcolor="limegreen")

    # Color current state
    if current_state:
        digraph.node(current_state, fillcolor="yellow")

    return digraph.pipe(format="svg")


def transition_label(transition: Transition) -> Optional[str]:
    if doc := transition.callback.__doc__:
        if lines := re.findall(r"^\s*Condition: .+$", doc, flags=re.MULTILINE):
            return ", ".join(
                line.split(": ", maxsplit=1)[1]
                for line in lines
            )
    return None
