"""
This module provides a state machine capability.

To use it, you should:

1. Declare a state machine (StateMachine)
2. Define the transitions and their callbacks (StateMachine.on)
3. Trigger events to update a model's state and triger a callback (StateMachine.trigger)

Full example:
    # 1. Declare

    model_onboarding_state_machine = StateMachine("onboarding_state")

    # 2. Define transitions

    @model_onboarding_state_machine.on("event", {"source_state": "destination_state"})
    def callback(model: Model, param: bool = False, **kwargs):
        if param:
            print(model)

    # 3. Trigger an event

    @dataclass
    class UserModel:
        onboarding_state: str

    user_model = UserModel(onboarding_state="source_state")

    model_onboarding_state_machine.trigger(
        model=user_model,
        event="event",
        param=True,
    )

    # Prints user_model *THEN* update its state.
"""

from dataclasses import dataclass
from functools import wraps
from typing import Callable, Dict, Generic, List, TypeVar

class StateMachineError(Exception):
    pass


class SkipTransition(StateMachineError):
    """Interrupt the current transition to move to the next one, if any."""
    pass


class NoTransitionFound(StateMachineError):
    """Raised when no transition was found, or when they were all skipped."""
    def __init__(self, state, event):
        super().__init__(f"No transition found from '{state}' for '{event}'")


class MustUseTrigger(StateMachineError):
    """Raised when a client try to call the callback without going through 'trigger'."""
    def __init__(self, function_name: str, event_name: str):
        super().__init__(f"Trigger must be used with '{event_name}', not {function_name}()")


Event = TypeVar("Event", bound=str)
State = TypeVar("State", bound=str)
Model = TypeVar("Model")


@dataclass(frozen=True)
class Transition(Generic[Event, State]):
    event: Event
    previous_state: State
    next_state: State
    callback: Callable


class StateMachine(Generic[Model, Event, State]):
    """An API to declare and use a state machine."""

    _attribute_name: str
    _transitions_by_state: Dict[State, List[Transition[Event, State]]]

    def __init__(self, attribute_name: str):
        self._attribute_name = attribute_name
        self._transitions_by_state = {}

    def on(
        self,
        event: Event,
        transitions: Dict[State, State],
    ):
        """Creates a decorator that, upon use, will register transitions."""

        def decorator(callback):
            @wraps(callback)
            def wrapper(*args, **kwargs):
                result = callback(*args, **kwargs)
                return result

            self._register_transitions(
                event=event,
                transitions=transitions,
                callback=wrapper,
            )

            @wraps(callback)
            def forbid_direct_calls(*args, **kwargs):
                raise MustUseTrigger(
                    function_name=callback.__name__,
                    event_name=event,
                )

            return forbid_direct_calls

        return decorator

    @property
    def transitions(self) -> List[Transition[Event, State]]:
        return list({
            transition
            for transitions in self._transitions_by_state.values()
            for transition in transitions
        })

    def trigger(self, model: Model, event: Event, **params):
        """
        Trigger the given event on the given model. It'll:
        1. trigger the callback associated to the first matching transition, then
        2. update model.<attribute_name> to the transition's next_state.
        """

        current_state = getattr(model, self._attribute_name)
        for transition in self._transitions_by_state.get(current_state, []):
            if event != transition.event:
                continue
            try:
                result = transition.callback(
                    model,
                    event=event,
                    previous_state=current_state,
                    next_state=transition.next_state,
                    **params,
                )
                setattr(model, self._attribute_name, transition.next_state)
                return result
            except SkipTransition:
                continue

        raise NoTransitionFound(state=current_state, event=event)

    def _register_transitions(
        self,
        event: Event,
        transitions: Dict[State, State],
        callback: Callable,
    ) -> None:
        for source, destination in transitions.items():
            transition = Transition(
                event=event,
                previous_state=source,
                next_state=destination,
                callback=callback,
            )

            if source not in self._transitions_by_state:
                self._transitions_by_state[source] = []

            if transition not in self._transitions_by_state[source]:
                self._transitions_by_state[source].append(transition)


def skip_transition():
    """Use this, *BEFORE ANY SIDE EFFECT*, in a callback, to skip a transition."""
    raise SkipTransition()
