# `TinyAgent`

The source code for "An Illustrated Guide to AI Agents" where you build a `TinyAgent` from scratch by building it up with one module at a time:

![../../images/tinyagents.png](../../images/tinyagents.png)

The general idea is that each module is self-contained and added to the `TinyAgent` with minimal changes when progressing through the book. At the end, you will have learned about each module in detail and can **Build an Agent from Scratch** like so:


```python
# Modules to augment your Agent
from illustrated_agents.llm import LLM  # llm.py
from illustrated_agents.memory import Memory  # memory.py
from illustrated_agents.tools import Skills  # tools.py
from illustrated_agents.planning import NativeReAct  # planning.py
from illustrated_agents.toolbox import get_weather  # toolbox.py
from illustrated_agents.display import Display  # display.py

# The TinyAgent
from illustrated_agents.agent import TinyAgent  # agent.py

# Choose an LLM - Using Ollama through an OpenAI endpoint
llm = LLM(model="my_model", base_url="http://localhost:11434/v1")

# Add Memory (simple conversation memory)
memory = Memory()

# Create autonomous behavior using native reasoning and tool calling
planner = NativeReAct(max_steps=10)

# Add Tools through native tool calling
tools = Skills()
tools.add_tool("get_weather", get_weather, "Get weather for a location")

# Optionally add a Skill
# tools.add_skill("path/to/SKILL.md")

# Create agent
agent = TinyAgent(
    llm=llm,
    memory=memory,
    tools=tools,
    planner=planner,
    display=Display(),
)
```

Each module is separated from the `TinyAgent` so that it can be learned as a modular component step-by-step.
