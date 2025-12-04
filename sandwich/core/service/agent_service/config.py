from langchain_core.runnables import RunnableConfig


def configure(thread_id: str, config: RunnableConfig | None = None) -> RunnableConfig:
    """
    Add the thread ID to a RunnableConfig (or create it) and return it

    See:
    - https://reference.langchain.com/python/langchain_core/runnables/?h=runnableconfig#langchain_core.runnables.RunnableConfig
    """
    config = config or {}
    config.setdefault("configurable", {})
    config["configurable"]["thread_id"] = thread_id
    return config
