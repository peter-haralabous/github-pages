from sandwich.core.service.agent_service.config import configure


def test_configure():
    assert configure("thread_1") == {"configurable": {"thread_id": "thread_1"}}
    assert configure("thread_2", {"configurable": {"thread_id": "thread_1"}, "tags": ["tag1", "tag2"]}) == {
        "configurable": {"thread_id": "thread_2"},
        "tags": ["tag1", "tag2"],
    }
