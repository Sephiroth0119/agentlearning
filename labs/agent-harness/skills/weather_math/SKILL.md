---
name: weather_math
tools:
  - get_weather
  - calculate
  - finish
response_format: tool_finish
---

# Weather Math Skill

Use this skill when the user asks about weather or simple math.

Rules:
- Use `get_weather` when the user asks for weather.
- Use `calculate` when the user asks for arithmetic.
- When you have enough information, call `finish`.
- Do not answer directly in plain assistant content.
- The final user-facing answer must be passed through `finish(final_answer=...)`.
