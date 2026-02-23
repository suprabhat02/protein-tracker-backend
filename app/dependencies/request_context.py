from fastapi import Request


def get_request_metadata(request: Request) -> tuple[str | None, str | None]:
    forwarded_for = request.headers.get("x-forwarded-for")
    ip_address: str | None = None
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    elif request.client:
        ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent
