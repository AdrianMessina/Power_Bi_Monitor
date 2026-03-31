"""
Sistema de logging de uso para YPF BI Monitor
Centraliza el tracking de todas las apps
"""

import json
from pathlib import Path
from datetime import datetime
import uuid


class UsageLogger:
    """Logger centralizado para todas las apps de YPF BI Monitor"""

    def __init__(self, suite_name: str, version: str):
        self.suite_name = suite_name
        self.version = version
        self.session_id = str(uuid.uuid4())
        self.logs_dir = Path(__file__).parent.parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        # Log session start
        self.log_event('session_started', {})

    def log_event(self, event_name: str, data: dict):
        """
        Log event to JSON file

        Args:
            event_name: Name of the event
            data: Dictionary with event data
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'suite': self.suite_name,
            'version': self.version,
            'event': event_name,
            'data': data
        }

        # Append to daily log file
        log_file = self.logs_dir / f"usage_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def end_session(self):
        """Log session end"""
        self.log_event('session_ended', {})


def get_logger() -> UsageLogger:
    """
    Get or create logger instance from Streamlit session state

    Returns:
        UsageLogger instance
    """
    import streamlit as st
    if 'logger' not in st.session_state:
        st.session_state.logger = UsageLogger("YPF_BI_Monitor", "1.0")
    return st.session_state.logger
