import pathlib
import diskcache

cache = diskcache.FanoutCache(
    directory=pathlib.Path().home() / ".cache" / "websearch-agent"
)
