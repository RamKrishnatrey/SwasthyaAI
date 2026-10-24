from backend.swasthyaai.agent.state import ConversationState


def test_conversation_stops_after_two_follow_up_questions():
    state = ConversationState(follow_up_count=2)

    assert state.can_ask_follow_up is False
    assert state.record_follow_up() == state


def test_conversation_allows_one_question_at_a_time_until_limit():
    state = ConversationState()

    next_state = state.record_follow_up()

    assert state.follow_up_count == 0
    assert next_state.follow_up_count == 1
    assert next_state.can_ask_follow_up is True
