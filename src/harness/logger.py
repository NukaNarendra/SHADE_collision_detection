import json
from datetime import datetime


class ConversationLogger:
    def __init__(self, config):
        self.config = config
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.config.logs_dir / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.transcript = []

    def log_turn(self, turn_number, agent_name, raw_content, reasoning, duration):
        char_count = len(raw_content) if raw_content else 0
        try:
            parsed_content = json.loads(raw_content)
            keys_present = list(parsed_content.keys())
            is_valid_json = True
        except:
            parsed_content = raw_content
            keys_present = []
            is_valid_json = False

        log_entry = {
            "turn_number": turn_number,
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "metadata": {
                "char_count": char_count,
                "is_valid_json": is_valid_json,
                "json_keys": keys_present
            },
            "reasoning": reasoning,
            "content": parsed_content
        }

        self.transcript.append(log_entry)
        self._write_log()

    def log_evaluation(self, eval_type, data):
        decision_entry = {
            "type": eval_type,
            "timestamp": datetime.now().isoformat(),
            "reasoning": data["reasoning"],
            "decision": data["parsed"]
        }
        self.transcript.append(decision_entry)
        self._write_log()
        return self.session_dir

    def _write_log(self):
        log_file = self.session_dir / "full_transcript.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(self.transcript, f, indent=4)