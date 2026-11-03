"""Voice: turns text into spoken audio using Microsoft's free neural voices (edge-tts)."""
import asyncio
import re
import config


def clean(text):
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[*_`#>~|]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def synth(text):
    import edge_tts

    async def run():
        out = bytearray()
        async for chunk in edge_tts.Communicate(text, config.VOICE).stream():
            if chunk["type"] == "audio":
                out += chunk["data"]
        return bytes(out)

    return asyncio.run(run())
