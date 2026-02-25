---

title: Composition Over Convenience

---

# {{ page.title }}

You began with a simple problem.
How do I turn a Python function into a Blender add-on?
Along the way, you built something larger.
You learned:

- How to declare tools instead of writing operators by hand.
- How to separate UI from logic.
- How to separate storage ownership from tool behavior.
- How to route shared data through a contract.
- How to compose multiple plugins into a host.
- How to isolate instances with scopes.
- How to execute long-running tasks without freezing Blender.
- How to enforce architectural discipline at build time.

QuickAddon is not a macro generator.
It is not a shortcut.
It is a structure.
The structure enforces:

- Explicit ownership
- Declarative inputs
- Predictable routing
- Controlled execution
- Safe composition

You may never need multi-instance scoped hosts.
You may never embed a host inside another host.
You may never declare a long task.
That is fine.
The architecture scales down as cleanly as it scales up.
The point is not complexity.
The point is boundaries.
When boundaries are clear:

- Systems remain stable.
- Growth remains controlled.
- Refactoring becomes possible.
- Composition becomes natural.

You now understand the full loop:

Script  
→ Tool  
→ Plugin  
→ Host  
→ System  

Everything beyond this point is composition.
Build what you need.
Refactor when structure demands it.
Generate when discipline permits it.

Own your boundaries.