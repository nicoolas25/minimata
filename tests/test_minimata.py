from typing import Optional
from attr import dataclass
from pytest import raises

from minimata import MustUseTrigger, NoTransitionFound, StateMachine, skip_transition
from minimata.chart import state_machine_to_svg, transition_label


@dataclass
class _TestModel:
    state: str = "state_1"
    knowledge_1: Optional[str] = None
    knowledge_2: Optional[str] = None
    knowledge_3: Optional[str] = None


_test_state_machine: StateMachine[_TestModel, str, str] = StateMachine("state")


@_test_state_machine.on("event_1", {"state_1": "state_2"})
def _event_1(test_model, info: bool = True, **kwargs):
    test_model.knowledge_1 = "Foo" if info else "Bar"


@_test_state_machine.on("event_2", {"state_2": "state_3"})
def _event_2(test_model, **kwargs):
    """
    Sample documentation starts...

    Condition: must have knowledge_1
    Condition: must have luck

    ... ongoing documentation.
    """
    if not test_model.knowledge_1:
        skip_transition()
    test_model.knowledge_2 = "Bar"


def test_simple_transition():
    model = _TestModel()
    _test_state_machine.trigger(model, "event_1")
    assert model.state == "state_2"


def test_direct_function_call_are_forbidden():
    model = _TestModel()
    with raises(MustUseTrigger):
        _event_1(model)


def test_enter_state_callback():
    model = _TestModel()
    _test_state_machine.trigger(model, "event_1")
    assert model.knowledge_1 == "Foo"


def test_after_state_change():
    model = _TestModel()
    _test_state_machine.trigger(model, "event_1", info=False)
    assert model.knowledge_1 == "Bar"


def test_transition_skipping():
    model = _TestModel(state="state_2", knowledge_1=None)
    with raises(NoTransitionFound):
        _test_state_machine.trigger(model, "event_2")


def test_transition_with_satisfied_condition():
    model = _TestModel(state="state_2", knowledge_1="Foo")
    _test_state_machine.trigger(model, "event_2")
    assert model.knowledge_2 == "Bar"


def test_missing_transition():
    model = _TestModel()
    with raises(NoTransitionFound):
        _test_state_machine.trigger(model, "event_3")


def test_charting():
    svg = state_machine_to_svg(
        state_machine=_test_state_machine,
        title="Offer state machine",
    )
    assert str(svg).startswith("b'<?xml")


def test_transition_label_extracts_relevant_docstring():
    transition = next(
        transition
        for transition in _test_state_machine.transitions
        if transition.callback.__doc__
    )
    assert transition_label(transition) == "must have knowledge_1, must have luck"
