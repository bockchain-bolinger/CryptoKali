"""
history.py - Chat history management.
"""

class ChatHistory:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatHistory, cls).__new__(cls)
            cls._instance.sessions = {}
        return cls._instance

    def get_history(self, session_id: str, last_n: int = 20) -> list:
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id][-last_n:]

    def add_message(self, session_id: str, role: str, content: str) -> None:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": role, "content": content})

    def clear_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            self.sessions[session_id] = []
