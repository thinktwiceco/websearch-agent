"""IO Cache module for web search operations.

This module provides disk-based caching functionality to store and retrieve
web search results, reducing unnecessary network requests and improving
performance by caching previous search results.
"""

import pathlib

import diskcache

# Create a persistent cache in the user's home directory
cache = diskcache.FanoutCache(
    directory=pathlib.Path().home() / ".cache" / "websearch-agent"
)
