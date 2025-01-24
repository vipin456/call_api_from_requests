import time
from datetime import datetime
from pytz import timezone

class CustomLogger:
    def __init__(self, log_file, dev_mode=False):
        self.f = None
        self.dev_mode = dev_mode
        self.log_file = log_file

    def open_log(self):
        try:
            # Open the log file with 'utf-8' encoding
            return open(self.log_file, 'a', encoding='utf-8')
        except IOError as e:
            print(f"ERROR: Unable to open log file {self.log_file}: {e}")
            return None

    def _write(self, text, level="5"):
        """Write a log event with specified log level."""
        if self.f is None:
            # Lazily open log file if not already opened
            self.f = self.open_log()

        if self.f is None:
            print(text)  # Write to console if there is no log file
        else:
            ts = self.get_ts()  # Get the current timestamp
            text = f"{ts} {level} {str(text)}\n"

            try:
                self.f.write(text)
            except OSError as error:
                # Handle stale file error
                self._handle_stale_file_error()
                time.sleep(1)
                self.f.write(text)

            # Also write to console
            print(text)

    def info(self, text):
        self._write(text=text, level="6")

    def warning(self, text):
        self._write(text=text, level="4")

    def error(self, text):
        self._write(text=text, level="3")

    def close(self):
        """Close the log file."""
        try:
            if self.f is not None:
                self.f.close()
        except OSError as error:
            print(f"ERROR: error closing logger due to {error}")

        self.f = None

    def get_ts(self):
        """Get the current timestamp for the event."""
        my_tz = timezone("US/Pacific")
        now = datetime.now(my_tz)
        dt_string = now.strftime("%y.%m.%d %H:%M:%S")
        return dt_string
