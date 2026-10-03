# agent.py

import os
import sys
from pathlib import Path
import datetime

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

load_dotenv()

MODEL = os.getenv("MODEL", "gemini-3.1-pro-preview")

blogPlannerAgent = LlmAgent(
   name="BlogPlanner",
   model=MODEL,
   description="Creates a practical, skimmable outline in Markdown.",
   instruction="""
You are a technical content strategist. Produce a clear Markdown outline with:
- Title
- Short intro
- 4–6 main sections (each with 2–3 bullets)
- Conclusion

If `codebase_context` exists in state, weave in specific sections/snippets.
Return only the outline in Markdown.
""",
   output_key="blog_outline",
)

blogWriterAgent = LlmAgent(
   name="BlogWriter",
   model=MODEL,
   description="Writes a technical blog post from the outline.",
   instruction="""
Write a complete Markdown article from the outline in `blog_outline`.

Guidelines:
- Audience: software engineers; skip basics and focus on practical insight.
- Explain both the 'how' and 'why'.
- Include concise code snippets when helpful.
- Follow the outline's structure (H2/H3).
- Output only the final article in Markdown (no fence around the whole post).
""",
   output_key="blog_post",
)

# Expose planner/writer as tools so the root agent can call them explicitly
planner_tool = AgentTool(agent=blogPlannerAgent)
writer_tool  = AgentTool(agent=blogWriterAgent)

# Root Agent: Plan -> Write
root_agent = LlmAgent(
   name="Blogger",
   model=MODEL,
   description="Minimal multi-agent blogger that plans and writes.",
   instruction=f"""
If the user gives a topic:
1 Call the planner tool to generate the outline.
2 Call the writer tool to produce the full draft.

Date: {datetime.datetime.now().strftime("%Y-%m-%d")}
""",
   tools=[
       planner_tool, # calls blogPlannerAgent
       writer_tool,  # calls blogWriterAgent
   ],
)