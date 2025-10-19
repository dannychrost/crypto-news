"""CLI loop that runs the Atlas agent with LangChain and OpenAI."""

import json
from urllib.parse import urlparse

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from app.prompts import system_prompt
from app.tools import get_db_news, get_health, search_web


def _build_search_summary(messages) -> str | None:
    """Return a short summary based on the newest search_web tool output."""
    # Walk newest-to-oldest so we summarise the latest search.
    for message in reversed(messages):
        if not isinstance(message, ToolMessage) or getattr(message, "name", "") != "search_web":
            continue

        try:
            payload = json.loads(message.content)
        except json.JSONDecodeError:
            continue

        if not payload.get("success"):
            return payload.get("message")

        results = payload.get("results") or []
        if not results:
            return payload.get("message")

        lines = ["Here are the latest findings from the web:"]
        for result in results[:3]:
            title = (result.get("title") or "Update").strip()
            url = (result.get("url") or "").strip()
            domain = urlparse(url).netloc.replace("www.", "") if url else ""

            snippet = " ".join((result.get("snippet") or "").split())
            if len(snippet) > 220:
                snippet = snippet[:217].rstrip() + "..."

            published_date = (result.get("published_date") or "").strip()

            detail_parts = []
            if published_date:
                detail_parts.append(published_date)
            detail_parts.append(title)
            if domain:
                detail_parts.append(f"[{domain}]")
            detail = " | ".join(detail_parts)

            if snippet:
                lines.append(f"- {detail}: {snippet}")
            else:
                lines.append(f"- {detail}")

        return "\n".join(lines)

    return None


load_dotenv()

# Configure the chat model once so the agent can reuse it every turn.
model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,  # Keeps answers factual while still sounding natural.
    max_tokens=800,  # Enough room for condensed bullet lists without runaway cost.
    timeout=60,  # Gives tool-heavy turns a little breathing space.
)

# Wire up the agent with our tools and system prompt.
agent = create_agent(
    model,
    tools=[get_health, get_db_news, search_web],
    system_prompt=system_prompt,
)

messages = []

while True:
    user_input = input("User: ")
    messages.append(HumanMessage(content=user_input))
    previous_length = len(messages)

    token_logs = []
    fallback_detected = False

    for attempt in range(2):
        # Ask the agent to handle the latest message list.
        result = agent.invoke({"messages": messages})
        messages = result["messages"]
        new_messages = messages[previous_length:]

        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_tokens = 0

        # Aggregate token usage so we can log a single line per turn.
        for msg in new_messages:
            usage = getattr(msg, "response_metadata", {}).get("token_usage")
            if not usage:
                continue
            total_prompt_tokens += usage.get("prompt_tokens", 0)
            total_completion_tokens += usage.get("completion_tokens", 0)
            total_tokens += usage.get(
                "total_tokens",
                usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0),
            )

        token_logs.append(
            {
                "prompt": total_prompt_tokens,
                "completion": total_completion_tokens,
                "total": total_tokens,
            }
        )

        final_message = messages[-1]
        used_search_web = any(
            isinstance(msg, ToolMessage) and getattr(msg, "name", "") == "search_web"
            for msg in new_messages
        )
        content_lower = final_message.content.strip().lower()
        fallback_triggers = (
            "no news found for that time period.",
            "unable to access",
            "can't access",
            "cannot access",
            "no web news",
            "unable to retrieve",
        )
        fallback_response = any(trigger in content_lower for trigger in fallback_triggers)

        if fallback_response and not used_search_web and attempt == 0:
            # Nudge the agent if it tried to give up without searching.
            messages.append(
                SystemMessage(
                    content=(
                        "You must call search_web with a focused query before concluding that no news exists. "
                        "Call search_web now and then provide an updated answer to the user."
                    )
                )
            )
            previous_length = len(messages)
            continue

        fallback_detected = fallback_response
        break

    combined_prompt = sum(entry["prompt"] for entry in token_logs)
    combined_completion = sum(entry["completion"] for entry in token_logs)
    combined_total = sum(entry["total"] for entry in token_logs)

    if combined_total:
        print(
            f"[token usage] prompt={combined_prompt} completion={combined_completion} total={combined_total}"
        )

    final_message = messages[-1]

    # If the model still produced a fallback, surface the raw search results instead.
    if fallback_detected:
        summary = _build_search_summary(messages)
        if summary:
            print(summary)
            continue

    print(final_message.content)
