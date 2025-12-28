import os
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.tabs import MDTabs
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard

# ─────────────────────────────────────────────────────────────────────────────
# Global font override
# ─────────────────────────────────────────────────────────────────────────────
FONT_PATHS = [
    r"C:\\EdenOS_Origin\\all_daemons\\Aethercore\\fonts\\LSANS.TTF",
    r"fonts\\LSANS.TTF",
]
for fp in FONT_PATHS:
    if os.path.exists(fp):
        LabelBase.register(
            name="Roboto",
            fn_regular=fp,
            fn_bold=fp,
            fn_italic=fp,
            fn_bolditalic=fp,
        )
        break

class AetherCore:
    def __init__(self):
        self.memory = []
    def log(self, msg: str):
        self.memory.append(msg)
        return msg

# ─────────────────────────────────────────────────────────────────────────────
# StillPoint Suites: Advocate, Eden Wing, SOS
# ─────────────────────────────────────────────────────────────────────────────
class AdvocateScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.clear_widgets()
        card = MDCard(orientation="vertical", padding=dp(16), spacing=dp(12), style="elevated")
        card.add_widget(MDLabel(text="Advocate: The StillPoint Clinic", halign="center", font_style="H5"))
        card.add_widget(MDLabel(text="Clinical precision meets Eden care.", halign="center"))
        card.add_widget(MDRaisedButton(
            text="Go to Eden Wing",
            on_release=lambda *_: setattr(self.manager, "current", "edenwing"),
        ))
        card.add_widget(MDRaisedButton(
            text="Go to SOS",
            on_release=lambda *_: setattr(self.manager, "current", "sos"),
        ))
        self.add_widget(card)

class EdenWingScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.clear_widgets()
        card = MDCard(orientation="vertical", padding=dp(16), spacing=dp(12))
        card.add_widget(MDLabel(text="Eden Wing: Rehab", halign="center", font_style="H5"))
        card.add_widget(MDLabel(text="Restoration in progress…", halign="center"))
        card.add_widget(MDRaisedButton(
            text="Back to Advocate",
            on_release=lambda *_: setattr(self.manager, "current", "advocate"),
        ))
        self.add_widget(card)

class SOSScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.clear_widgets()
        card = MDCard(orientation="vertical", padding=dp(16), spacing=dp(12))
        card.add_widget(MDLabel(text="SOS: Standalone App", halign="center", font_style="H5"))
        card.add_widget(MDLabel(text="Emergency whispers and urgent care.", halign="center"))
        card.add_widget(MDRaisedButton(
            text="Back to Advocate",
            on_release=lambda *_: setattr(self.manager, "current", "advocate"),
        ))
        self.add_widget(card)

# ─────────────────────────────────────────────────────────────────────────────
# Consent screen stays as entry point
# ─────────────────────────────────────────────────────────────────────────────
class ConsentScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.clear_widgets()
        card = MDCard(orientation="vertical", padding=dp(16), spacing=dp(12), style="elevated")
        card.add_widget(MDLabel(text="Consent", halign="center", font_style="H5"))
        card.add_widget(MDLabel(text="By continuing, you enter StillPoint Suites.", halign="center"))
        card.add_widget(MDRaisedButton(
            text="Continue",
            on_release=lambda *_: setattr(self.manager, "current", "main"),
        ))
        self.add_widget(card)


class MainScreen(MDScreen):
    def __init__(self, aether: AetherCore, **kwargs):
        super().__init__(**kwargs)
        self.aether = aether

    def on_pre_enter(self, *args):
        self.clear_widgets()
        layout = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        layout.add_widget(MDLabel(text="Aethercore — StillPoint Suites", halign="center", font_style="H5"))
        layout.add_widget(MDLabel(
            text="Choose a path: direct clinic flows or the tabbed hub.",
            halign="center",
        ))
        layout.add_widget(MDRaisedButton(
            text="Open Advocate (Clinic)",
            on_release=lambda *_: setattr(self.manager, "current", "advocate"),
        ))
        layout.add_widget(MDRaisedButton(
            text="Open Eden Wing (Rehab)",
            on_release=lambda *_: setattr(self.manager, "current", "edenwing"),
        ))
        layout.add_widget(MDRaisedButton(
            text="Open SOS (Standalone)",
            on_release=lambda *_: setattr(self.manager, "current", "sos"),
        ))
        layout.add_widget(MDRaisedButton(
            text="Tab Hub: StillPoint Suites",
            on_release=lambda *_: setattr(self.manager, "current", "stillpoint"),
        ))
        layout.add_widget(MDRaisedButton(
            text="SOS App (Flirt)",
            on_release=lambda *_: setattr(self.manager, "current", "sos_app"),
        ))
        self.add_widget(layout)

# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Stillpoint Suites (Hub) → Advocate, Eden Wing, SOS
# ─────────────────────────────────────────────────────────────────────────────
class AdvocateTab(MDBoxLayout, MDTabsBase):
    title = "Advocate"
    def __init__(self, aether: AetherCore, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(12), padding=dp(16), **kwargs)
        self.aether = aether
        self.add_widget(MDLabel(text="Advocate — The StillPoint Clinic", halign="center", font_style="H6"))
        self.add_widget(MDCard(
            orientation="vertical",
            padding=dp(16),
            radius=[18,18,18,18],
            style="outlined",
            md_bg_color=(0.10,0.10,0.14,1),
            children=[
                MDLabel(text="Client intake. Anti-gaslighting tools. Evidence packs.", halign="center"),
                MDTextField(hint_text="Describe the issue...", helper_text="facts > feelings (we’ll hold both)", helper_text_mode="on_focus"),
                MDRaisedButton(text="Generate Advocate Plan", on_release=lambda *_: self.aether.log("advocate_plan")),
            ]
        ))
        self.add_widget(MDRaisedButton(text="Jump to Eden Wing", on_release=lambda *_: self.parent.switch_tab("Eden Wing")))

class EdenWingTab(MDBoxLayout, MDTabsBase):
    title = "Eden Wing"
    def __init__(self, aether: AetherCore, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(12), padding=dp(16), **kwargs)
        self.aether = aether
        self.add_widget(MDLabel(text="Eden Wing — Rehab / Recovery", halign="center", font_style="H6"))
        self.add_widget(MDCard(
            orientation="vertical",
            padding=dp(16),
            radius=[18,18,18,18],
            style="outlined",
            md_bg_color=(0.10,0.12,0.16,1),
            children=[
                MDLabel(text="Ritual resets, soft locks, and quiet rooms.", halign="center"),
                MDTextField(hint_text="Name a ritual or boundary..."),
                MDRaisedButton(text="Apply Rehab Protocol", on_release=lambda *_: self.aether.log("eden_wing_protocol")),
            ]
        ))
        self.add_widget(MDRaisedButton(text="Jump to Advocate", on_release=lambda *_: self.parent.switch_tab("Advocate")))

class SOSTab(MDBoxLayout, MDTabsBase):
    title = "SOS"
    def __init__(self, aether: AetherCore, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(12), padding=dp(16), **kwargs)
        self.aether = aether
        self.add_widget(MDLabel(text="SOS — Standalone App (Flirt)", halign="center", font_style="H6"))
        self.add_widget(MDCard(
            orientation="vertical",
            padding=dp(16),
            radius=[18,18,18,18],
            style="outlined",
            md_bg_color=(0.12,0.10,0.14,1),
            children=[
                MDLabel(text="Signal → soothe → stabilize.", halign="center"),
                MDTextField(hint_text="Whisper a distress signal…"),
                MDRaisedButton(text="Send SOS", on_release=lambda *_: self.aether.log("sos_signal")),
            ]
        ))
        self.add_widget(MDRaisedButton(text="Open SOS as App", on_release=lambda *_: setattr(self.parent.parent, "current", "sos_app")))

class StillpointHubScreen(MDScreen):
    def __init__(self, aether: AetherCore, **kwargs):
        super().__init__(**kwargs)
        self.aether = aether
        root = MDBoxLayout(orientation="vertical")
        toolbar = MDTopAppBar(title="Stillpoint Suites", elevation=2, md_bg_color=(0.22,0.18,0.34,1))
        root.add_widget(toolbar)

        self.tabs = MDTabs(expand=True)
        self.tabs.add_widget(AdvocateTab(self.aether))
        self.tabs.add_widget(EdenWingTab(self.aether))
        self.tabs.add_widget(SOSTab(self.aether))
        root.add_widget(self.tabs)

        root.add_widget(MDBoxLayout(size_hint_y=None, height=dp(60), padding=dp(8), spacing=dp(8), children=[
            MDRaisedButton(text="Back to Main", on_release=lambda *_: setattr(self.manager, "current", "main")),
        ]))
        self.add_widget(root)

# Optional standalone SOS screen (Flirt app)
class FlirtScreen(MDScreen):
    def __init__(self, aether: AetherCore, **kwargs):
        super().__init__(**kwargs)
        self.aether = aether

    def on_pre_enter(self, *args):
        self.clear_widgets()
        layout = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        layout.add_widget(MDLabel(text="SOS — Flirt App", halign="center", font_style="H5"))
        layout.add_widget(MDTextField(hint_text="Message…"))
        layout.add_widget(MDRaisedButton(text="Dispatch", on_release=lambda *_: self.aether.log("flirt_dispatch")))
        layout.add_widget(MDRaisedButton(text="Back", on_release=lambda *_: setattr(self.manager, "current", "stillpoint")))
        self.add_widget(layout)

# App
class AetherCoreApp(MDApp):
    def build(self):
        self.aether = AetherCore()
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Dark"

        sm = ScreenManager()
        sm.add_widget(ConsentScreen(name="consent"))
        sm.add_widget(MainScreen(self.aether, name="main"))
        sm.add_widget(AdvocateScreen(name="advocate"))
        sm.add_widget(EdenWingScreen(name="edenwing"))
        sm.add_widget(SOSScreen(name="sos"))
        sm.add_widget(StillpointHubScreen(self.aether, name="stillpoint"))
        sm.add_widget(FlirtScreen(self.aether, name="sos_app"))
        return sm

if __name__ == "__main__":
    AetherCoreApp().run()
