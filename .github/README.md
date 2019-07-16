# ucfai's `bot`


## Code structure
```
ucfai                   # source-code root
├── meta                # object-oriented containers for use by `tooling` funcs
│   ├── coordinator.py
│   ├── group.py
│   ├── groups.py       # sets up specific attributes for each Group
│   └── meeting.py
├── templates           # all the different models, self-contained
├── tooling             # shared components between observers and general utilities (think logging, plotting, etc.)
│   ├── apis            # class to coallesce Coordinators for use by tooling
│   ├── config          # configurations, e.g. website-specific data, etc.
│   └── ops.py          # all library functions should be placed here with a docstring
└── run.py              # entrypoint
```
