# Minimata: minimalist state-machine in Python

Miniata is a very small library to manage state-machines in Python.

Because it doesn't bundle a lot of features, it's pretty flexible.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `minimata`.

```bash
pip install minimata
```

## Why

I needed a really simple implementations and didn't wanted to reach to heavier
alternatives like [transitions](https://github.com/pytransitions/transitions).

## Usage

Here is an example:

```python
from minimata import StateMachine, skip_transition

model_onboarding_state_machine = StateMachine("onboarding_state")

@model_onboarding_state_machine.on("event", {"source_state": "destination_state"})
def callback(model: Model, param: bool = False, **kwargs):
    if param:
        print(model)

@dataclass
class UserModel:
    onboarding_state: str

user_model = UserModel(onboarding_state="source_state")

model_onboarding_state_machine.trigger(
    model=user_model,
    event="event",
    param=True,
) # Executes callback (prints user_model) *THEN* update its state.
```

## Contributing

With a hundred line of code, it's possible to get there and customize this. It'll
probably make sense for you to copy-paste that code rather than to add it as a
dependency.

That being said, pull-requests are welcome. It would be nice to polish the library,
please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Credits

Inspiration was heavily taken from the following projects.

* [micro-machine](https://github.com/soveran/micromachine)
* [transitions](https://github.com/pytransitions/transitions)

Many thanks to their authors, maintainers, and contributors.

## License

[MIT](https://choosealicense.com/licenses/mit/)
