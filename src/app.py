import time
import datetime

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Footer, Header, Button, Static, Input, Pretty, Label

from typing import Any, Final
import db

# Constants for selectors etc
hash_: Final = "#"
out: Final = "out"
hash_out: Final = hash_ + out
activityname: Final = "activityname"
hash_activityname: Final = hash_ + activityname
start: Final = "start"
stop: Final = "stop"
delete: Final = "delete"
timer_class: Final = "Timer"


def disable_timers() -> None:
    """Utility function to disable timers"""

    timers = app.query(timer_class)
    if timers:
        for timer in timers:
            timer.disabled = True


def enable_timers() -> None:
    """Utility function to enable timers"""

    timers = app.query(timer_class)
    if timers:
        for timer in timers:
            timer.disabled = False


def pretty_output(text: Any) -> None:
    """Utility function to update output"""

    out = app.query_one(hash_out)
    out.update(text)
    out.visible = True


def add_timer(label: str, elapsed: float = 0.0):
    """Utility function to add timer. If we are loading, anticipate elapsed > 0"""

    # First check that we don't already have one with the same name
    # if we do, use update_out
    for timer in app.query(timer_class):
        if timer.label == label:
            pretty_output(f"Timer with {label} already exists")
            return

    new_timer = Timer(label=label, elapsed=elapsed)
    app.query_one("#timers").mount(new_timer)
    new_timer.scroll_visible()


class MyInput(Input):
    """Widget to get input from the user"""

    def on_input_submitted(self, event: Input.Submitted) -> None:
        pretty_output(f"{event} recieved")
        self.disabled = True
        enable_timers()
        add_timer(self.value)
        app.sub_title = f"timer {self.value} added, hit 'r' to remove it"
        self.styles.visibility = "hidden"
        self.value = ""


class TimeDisplay(Static):
    """Widget to display elapsed time"""

    start_time = reactive(time.monotonic())
    time = reactive(0.0)
    # total will keep the time over the period(s) for which the time is active
    total = reactive(0.0)

    def __init__(self, elapsed: float = 0.0) -> None:
        """Instantiation"""

        # Need our own init to handle elapsed
        # init for Static
        super().__init__()
        self.elapsed = elapsed
        # We add the elapsed time from the first the first time further down
        # this is a bit of a hack
        self.freshly_loaded = True

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app"""

        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update the time to the current time"""

        self.time = self.total + (time.monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes"""

        # divmod returns a tuple of (quotient, remainder)
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        display = f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"
        self.update(display)

    def start(self) -> None:
        """Method to start or resume timer updating"""

        if self.freshly_loaded:
            self.start_time = time.monotonic() - self.elapsed
            self.freshly_loaded = False
        else:
            self.start_time = time.monotonic()

        self.update_timer.resume()
        app.sub_title = "timer started"

    def stop_no_update(self) -> None:
        """Method to stop timer updating w/o time update"""

        self.update_timer.pause()
        app.sub_title = "timer stopped"

    def stop(self) -> None:
        """Method to stop timer updating"""

        self.update_timer.pause()
        self.total += time.monotonic() - self.start_time
        self.time = self.total
        app.sub_title = "timer stopped"


class Timer(Static):
    """Timing block associated with each activity"""

    def __init__(self, label: str, elapsed: float) -> None:
        # Need our own init to handle
        super().__init__()
        self.label = label
        self.elapsed = elapsed
        # Quasi-log to log state changes
        self.timer_log = []

    def log_it(self, state: str) -> None:
        """Log it with tz-aware UTC timestamp"""

        ts = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

        log_entry = {"label": self.label, "state": state, "ts": ts, "date": ts.date()}
        if state == "stop":
            previous_entry = self.timer_log[-1]
            self.elapsed += (log_entry["ts"] - previous_entry["ts"]).total_seconds()

        self.timer_log.append(log_entry)
        pretty_output(log_entry)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when button is pressed"""

        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)

        if button_id == start:
            time_display.start()
            self.add_class("started")
        elif button_id == stop:
            time_display.stop()
            self.remove_class("started")
        elif button_id == delete:
            self.remove()
            app.sub_title = "timer deleted"

        self.log_it(button_id)

    def compose(self) -> ComposeResult:
        yield Button(start, id=start, variant="success")
        yield Button(stop, id=stop, variant="warning")
        yield Button(delete, id=delete, variant="error")
        yield Label(self.label)
        yield TimeDisplay(elapsed=self.elapsed)


class Punchcard(App[int]):
    """A simple app to track time, using textual"""

    CSS_PATH = "style.css"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("n", "add_timer", "New activity"),
        ("r", "remove_timer", "Remove activity"),
        ("w", "write_to_db", "Write to db"),
        ("r", "read_from_db", "Read from db"),
        ("v", "view_timer_log", "View log+state"),
        ("c", "clear_output", "Clear output"),
    ]
    SUB_TITLE = "let's get timing"

    return_value = 0

    def action_clear_output(self) -> None:
        pretty_output("")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ScrollableContainer(id="timers")
        yield MyInput(
            placeholder="Enter a name for the activity",
            id=activityname,
            disabled=True,
        )
        yield Pretty([], id=out)

    def prompt_for_activity_name(self) -> None:
        """Prompt for an activity name"""

        # Hide/disable all the timers
        disable_timers()

        # Need to make the input visible to get the associated activity name
        # then when this is done, hide the input again
        # and mount the new timer
        pretty_output("Please enter a name for the activity in the box and hit enter")
        activity = self.query_one(hash_activityname)
        activity.disabled = False
        activity.visible = True
        activity.scroll_visible()
        activity.focus()

    def action_add_timer(self) -> None:
        """An action to add a timer"""

        self.prompt_for_activity_name()

    def action_remove_timer(self) -> None:
        """An action to remove a timer"""
        timers = self.query(timer_class)
        if timers:
            timers.last().remove()
            self.sub_title = "timer removed, hit 'n' to add another"

    def get_timer_state(self, timer: Timer) -> dict[str, Any]:
        """State dict from Timer object"""

        state = "start" if timer.has_class("started") else "stop"
        return dict(state=state, elapsed=timer.elapsed, label=timer.label)

    def action_view_timer_log(self) -> None:
        """Method to show timer log/state"""

        timers = self.query(timer_class)
        pretty_output(([timer.timer_log for timer in timers], [self.get_timer_state(timer) for timer in timers]))

    def action_write_to_db(self) -> None:
        """Write log and state to db"""

        n_actions = 0
        n_states = 0
        timers = self.query(timer_class)

        # If no timers, nothing to do
        if len(timers) == 0:
            pretty_output("No timers present")
            return
        # implied else

        # Loop through and write the timer logs
        for timer in timers:
            # stop the timer for good order
            timer.query_one(TimeDisplay).stop_no_update()
            timer.remove_class("started")

            # log
            log = timer.timer_log
            # If log is not empty
            if log:
                # Loop through until empty
                while log:
                    # Write each entry to db and pop it off the list at the same time
                    to_write = log.pop(0)
                    db.write_timer_log(to_write)
                    n_actions += 1

        # Loop through and write the states
        db.clear_state()
        ts = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

        for timer in timers:
            timer_state = self.get_timer_state(timer)
            timer_state["ts"] = ts
            db.write_state(timer_state)
            n_states += 1

        pretty_output(f"{n_actions} actions, {n_states} states written to db")

    def action_read_from_db(self) -> None:
        """Method to read from db"""

        inputs = db.read_state()
        if len(inputs) == 0:
            pretty_output("No timers in db")
            return

        for each in inputs:
            add_timer(label=each.label, elapsed=each.elapsed)

        pretty_output(inputs)


# app must be global unfortunately
app: Punchcard | None = None


def runapp() -> int:
    global app

    app = Punchcard()
    return app.run()


if __name__ == "__main__":
    runapp()
