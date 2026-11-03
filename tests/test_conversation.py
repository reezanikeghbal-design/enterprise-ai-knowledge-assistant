from app.services.conversation_service import ConversationService


def test_conversation_isolation(tmp_path):
    service = ConversationService(str(tmp_path / "conversations.json"))
    a = service.create()
    b = service.create()
    service.add_message(a["id"], "user", "alpha")
    assert service.get(a["id"])["messages"][0]["content"] == "alpha"
    assert service.get(b["id"])["messages"] == []
