from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationState:
    follow_up_count: int = 0
    max_follow_ups: int = 2

    @property
    def can_ask_follow_up(self) -> bool:
        return self.follow_up_count < self.max_follow_ups

    def record_follow_up(self) -> "ConversationState":
        if not self.can_ask_follow_up:
            return self
        return ConversationState(self.follow_up_count + 1, self.max_follow_ups)
