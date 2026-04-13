from textual.app import App
from textual.containers import ScrollableContainer, VerticalGroup, Horizontal
from textual.widgets import Header, Footer, Input, Label, RichLog, Collapsible, Button
from textual.binding import Binding
from textual.css.query import NoMatches

from langgraph.types import Command
from pathlib import Path

from stt.record import start_recording, stop_recording
from stt.transcribe import load_model, transcribe
from agent.graph import graph

MEM0_USER_ID = "test-user"

class InputBar(VerticalGroup):
    def compose(self):
        yield Label("Press 1 to Record | 2 to Upload File | 3 to Type | Ctrl+C to quit", id="hint-label")


class TurnWidget(VerticalGroup):
    def __init__(self, user_message: str, **kwargs):
        super().__init__(**kwargs)
        self.user_message = user_message

    def compose(self):
        yield Label(f"You: {self.user_message}", classes="user-message")
        with Collapsible(title="Thinking...", collapsed=True, id="trace-collapsible"):
            yield RichLog(id="trace-log", markup=True)
        yield RichLog(id="response-log", markup=True)


class HITLBar(Horizontal):
    def compose(self):
        yield Label("Agent wants to write a file. Approve?", id="hitl-label")
        yield Button("Approve", id="approve-btn", variant="success")
        yield Button("Reject", id="reject-btn", variant="error")


class DolphinAgent(App):
    CSS_PATH = "app.tcss"
    BINDINGS = [
        ("1", "record_audio", "Record"),
        ("2", "upload_file", "Upload File"),
        ("3", "toggle_textbox", "Type"),
        Binding("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self._current_turn: TurnWidget | None = None
        self._pending_hitl = False
        self._thread_id = "dolphin-session-1"

    def on_mount(self):
        load_model("base")

    def compose(self):
        yield Header(icon="🐬")
        yield Footer()
        
        self.chat_container = ScrollableContainer(id="chat-container")
        yield self.chat_container
        
        self.input_area = InputBar(id="input-area")
        yield self.input_area


    def _clear_input_area(self, skip_id: str = None):
        for widget_id in ["recording-input", "file-input", "text-input", "hitl-bar"]:
            if widget_id == skip_id:
                continue
            try:
                self.input_area.get_child_by_id(widget_id).remove()
            except NoMatches:
                pass


    def action_record_audio(self):
        self._clear_input_area()
        recording_input = Input(
            placeholder="Recording... press Enter to stop",
            id="recording-input"
        )
        self.input_area.mount(recording_input, after=0)
        self.run_worker(start_recording, name="recording", thread=True)
        self.set_focus(recording_input)


    def action_upload_file(self):
        self._clear_input_area()
        file_input = Input(
            placeholder="Enter path to audio file...",
            id="file-input"
        )
        self.input_area.mount(file_input, after=0)
        self.set_focus(file_input)


    def action_toggle_textbox(self, prompt: str = ""):
        try:
            text_input = self.input_area.get_child_by_id("text-input")
        except NoMatches:
            self._clear_input_area(skip_id="text-input")
            text_input = Input(
                value=prompt,
                placeholder="Type your prompt here...",
                id="text-input"
            )
            self.input_area.mount(text_input, after=0)

        # Focus the text box
        self.set_focus(text_input)


    async def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "recording-input":
            event.input.disabled = True
            path = stop_recording()
            prompt = transcribe(path)
            self._clear_input_area()
            safe_prompt = prompt.replace("'", "")
            await self.run_action(f"toggle_textbox('{safe_prompt}')")

        elif event.input.id == "file-input":
            path = Path(event.value.strip())
            if not path.exists():
                event.input.add_class("error")
                try:
                    self.input_area.get_child_by_id("file-error").remove()
                except NoMatches:
                    pass
                self.input_area.mount(
                    Label("[red]File not found. Try again.[/red]", id="file-error")
                )
                return
            event.input.remove_class("error")
            prompt = transcribe(str(path))
            self._clear_input_area()
            safe_prompt = prompt.replace("'", "")
            await self.run_action(f"toggle_textbox('{safe_prompt}')")

        elif event.input.id == "text-input":
            prompt = event.value.strip()
            if not prompt:
                return
            self._clear_input_area()
            await self._run_agent(prompt)


    async def _run_agent(self, prompt: str):
        turn = TurnWidget(prompt)
        await self.chat_container.mount(turn)
        self._current_turn = turn
        self.chat_container.scroll_end(animate=False)

        config = {"configurable": {"thread_id": self._thread_id}}
        initial_state = {
            "messages": [{"role": "user", "content": prompt}],
            "mem0_user_id": MEM0_USER_ID,
        }

        self.run_worker(
            lambda: self._stream_agent(initial_state, config),
            name="agent",
            thread=True
        )

    def _stream_agent(self, initial_state: dict, config: dict):
        for chunk in graph.stream(initial_state, config=config, stream_mode="updates"):
            if "__interrupt__" in chunk:
                interrupt_data = chunk["__interrupt__"][0].value
                self.call_from_thread(self._show_hitl, interrupt_data)
                return

            if "tools" in chunk:
                trace = chunk["tools"].get("trace", [])
                for entry in trace:
                    msg = f"[yellow]Tool:[/yellow] {entry['tool']} | [cyan]Args:[/cyan] {entry['args']}"
                    self.call_from_thread(self._append_trace, msg)

            if "agent" in chunk:
                messages = chunk["agent"].get("messages", [])
                for msg in messages:
                    if hasattr(msg, "content") and msg.content:
                        self.call_from_thread(self._append_response, msg.content)


    def _show_hitl(self, interrupt_data: dict):
        hitl_bar = HITLBar(id="hitl-bar")
        self.input_area.mount(hitl_bar)


    def _append_trace(self, message: str):
        if self._current_turn:
            try:
                log = self._current_turn.query_one("#trace-log", RichLog)
                log.write(message)
            except NoMatches:
                pass


    def _append_response(self, message: str):
        if self._current_turn:
            try:
                log = self._current_turn.query_one("#response-log", RichLog)
                log.write(message)
                self.chat_container.scroll_end(animate=False)
            except NoMatches:
                pass


    def on_button_pressed(self, event: Button.Pressed):
        config = {"configurable": {"thread_id": self._thread_id}}
        decision = "approve" if event.button.id == "approve-btn" else "reject"
        self._clear_input_area()

        self.run_worker(
            lambda: self._resume_agent(decision, config),
            name="agent-resume",
            thread=True
        )


    def _resume_agent(self, decision: str, config: dict):
        for chunk in graph.stream(
            Command(resume=decision),
            config=config,
            stream_mode="updates"
        ):
            if "tools" in chunk:
                trace = chunk["tools"].get("trace", [])
                for entry in trace:
                    msg = f"[yellow]Tool:[/yellow] {entry['tool']} | [cyan]Args:[/cyan] {entry['args']}"
                    self.call_from_thread(self._append_trace, msg)

            if "agent" in chunk:
                messages = chunk["agent"].get("messages", [])
                for msg in messages:
                    if hasattr(msg, "content") and msg.content:
                        self.call_from_thread(self._append_response, msg.content)


if __name__ == "__main__":
    app = DolphinAgent()
    app.run()