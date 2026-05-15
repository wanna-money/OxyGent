# How to Install OxyGent?

### How to Set Up the Environment?
---

We support setting up the environment via `conda` or `uv`.

+ Create the runtime environment (conda)
```bash
   conda create -n oxy_env python==3.10
   conda activate oxy_env
```
Or (uv)
```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv python install 3.10 
   uv venv .venv --python 3.10
   source .venv/bin/activate
```
+ Install the release package (conda)
```bash
   pip install oxygent
```
Or (uv)
```bash
   uv pip install oxygent
```

### Can I Use Other Python Versions?
---

We recommend using **Python 3.10** to run OxyGent for now. Future versions will be compatible with the latest Python packages.

### Are There Any Other Environment Requirements?
---

No, OxyGent's core is pure Python. However, for a better experience, we recommend installing [Node.js](https://nodejs.org) first.

### How to Install OxyGent?
---
```bash
   pip install oxygent # conda
   uv pip install oxygent # uv
```

### What If the Installation Is Too Slow?
---
You can use a mirror for installation, for example:

```bash
uv pip install oxygent -i https://pypi.tuna.tsinghua.edu.cn/simple
```

Or download the `oxygent` folder directly from GitHub and place it in the project root directory. (Using the local package requires installing requirements.txt first.)

OxyGent will prioritize the local package.


[Next: Run the Demo](./demo.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Single Agent Example](../../examples/agents/demo_single_agent.md) -- The simplest ChatAgent configuration
- [Config Setup Example](../../examples/backend/demo_config.md) -- Configuration-related examples
