"""Handles the create → send → stream → extract cycle for a single user question."""

import anthropic


def ask_question(client: anthropic.Anthropic, agent_id: str, env_id: str, question: str) -> str:
    """
    Creates a new session, sends the question, streams events until idle,
    and returns the agent's text response.
    """
    session = client.beta.sessions.create(
        agent=agent_id,
        environment_id=env_id,
        title=question[:80],
    )

    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [{"type": "text", "text": question}],
            }
        ],
    )

    response_parts = []
    session_error = None

    with client.beta.sessions.events.stream(session.id) as stream:
        for event in stream:
            event_type = getattr(event, "type", None)

            if event_type == "agent.message":
                content = getattr(event, "content", [])
                for block in content:
                    block_type = getattr(block, "type", None)
                    if block_type == "text":
                        response_parts.append(block.text)

            elif event_type == "session.error":
                error = getattr(event, "error", None)
                error_type = getattr(error, "type", "unknown_error")
                error_msg = getattr(error, "message", str(error))
                session_error = f"{error_type}: {error_msg}"

            elif event_type == "session.status_idle":
                break

            elif event_type == "session.status_terminated":
                raise RuntimeError(
                    f"Session terminated unexpectedly (session_id={session.id})"
                )

    if session_error:
        raise RuntimeError(f"Session error — {session_error}")

    answer = "".join(response_parts).strip()

    if not answer:
        raise ValueError(f"Empty response from agent (session_id={session.id})")

    return answer
