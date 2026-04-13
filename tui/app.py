from textual.app import App
from textual.containers import ScrollableContainer, VerticalGroup
from textual.widgets import (
    Header, 
    Footer, 
    Input,
    Placeholder,
    Label,
    RichLog,
    Log,
    Link
)
from textual.binding import Binding
from textual.css.query import NoMatches

from stt.record import start_recording, stop_recording
from stt.transcribe import load_model, transcribe

class InputBar(VerticalGroup):
    def compose(self):
        yield Label(
            "Press 1 to Record Audio, 2 to Upload File, 3 to Type", id="hint-label"
        )
        # yield Placeholder("Textbox")
        # yield Placeholder("File Uploader")

class DolphinAgent(App):
    CSS_PATH = "app.tcss"
    BINDINGS = [
        ("1", "record_audio", "Record audio"),
        ("2", "upload_file", "Upload File"),
        ("3", "toggle_textbox", "Give prompt via text"),
        Binding("ctrl+c", "quit", "Quit the app")
    ]
    
    def on_mount(self):
        load_model("base")
    
    
    def compose(self):
        yield Header(name="Dolphin Agent")
        yield Footer()
        
        self.chat_container = ScrollableContainer(id="chat-container")
        yield self.chat_container
        
        self.input_area = InputBar(id="input-area")
        yield self.input_area
        
    def _clear_input_area(self, exclude_id=""):
        for widget_id in ["recording-input", "file-input", "text-input"]:
            try:
                if widget_id != exclude_id:
                    self.input_area.get_child_by_id(widget_id).remove()
            except NoMatches:
                pass   
    
    
    def action_record_audio(self):
        self._clear_input_area(exclude_id="recording-input")

        recording_label = Input(
            placeholder="Recording.... Press Enter to stop",
            # disabled=True,
            id="recording-input"
        )

        self.run_worker(start_recording, name="start_recording", group="stt", thread=True)
        self.input_area.mount(recording_label, after=0)
        self.set_focus(recording_label)


    def action_upload_file(self):
        self._clear_input_area(exclude_id="file-input")
        pass
    
    
    def action_toggle_textbox(self, prompt = ""):        
        try:
            text_input = self.input_area.get_child_by_id("text-input")
        except NoMatches:
            self._clear_input_area(exclude_id="text-input")
            text_input = Input(value=prompt, placeholder="Please enter your prompt here", id="text-input")
            self.input_area.mount(text_input, after=0)
            self.set_focus(text_input)

        # Focus the text box
        self.set_focus(text_input)
        

    async def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "recording-input":
            event.control.disabled = True
            path = stop_recording()
            prompt = transcribe(path)

            self.input_area.remove_children("#recording-input") 
            await self.run_action(f"toggle_textbox(\"{prompt}\")")

        if event.input.id == "file-input":
            raise NotImplementedError

        if event.input.id == "text-input":
            prompt = event.value

        

if __name__ == "__main__":
    app = DolphinAgent()
    app.run()