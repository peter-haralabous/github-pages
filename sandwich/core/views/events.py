import asyncio
import random

from django.db import transaction
from django.http import HttpRequest
from django.http import StreamingHttpResponse


@transaction.non_atomic_requests
async def events(request: HttpRequest):
    """
    Sends server-sent events to the client.
    """

    async def event_stream():
        emojis = ["🚀", "🐎", "🌅", "🦾", "🍇"]
        for i in range(30):
            yield f"data: {random.choice(emojis)} {i}\n\n"  # noqa: S311
            await asyncio.sleep(1)

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
        # without no-transform webpack-dev-server will buffer the stream
        # https://github.com/chimurai/http-proxy-middleware/issues/371
        headers={
            "Cache-Control": "no-store, no-transform",
        },
    )
