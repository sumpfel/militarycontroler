from ._anvil_designer import Form1Template
from anvil import *
import anvil.server


class Form1(Form1Template):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        # Navigation Links erstellen
        self.link_dashboard = Link(text="🏠 Dashboard", bold=True)
        self.link_personal = Link(text="👤 Personal")
        self.link_fahrzeuge = Link(text="🚗 Fahrzeuge")
        self.link_lager = Link(text="📦 Lager & Gegenstände")
        self.link_waffen = Link(text="🔫 Waffen ↔ Munition")

        self.link_dashboard.set_event_handler('click', self.nav_dashboard)
        self.link_personal.set_event_handler('click', self.nav_personal)
        self.link_fahrzeuge.set_event_handler('click', self.nav_fahrzeuge)
        self.link_lager.set_event_handler('click', self.nav_lager)
        self.link_waffen.set_event_handler('click', self.nav_waffen)

        self.navbar_links.add_component(self.link_dashboard)
        self.navbar_links.add_component(self.link_personal)
        self.navbar_links.add_component(self.link_fahrzeuge)
        self.navbar_links.add_component(self.link_lager)
        self.navbar_links.add_component(self.link_waffen)

        # Dashboard als Startseite laden
        self.load_form("DashboardForm")

    def load_form(self, form_name):
        """Lädt ein Form in das content_panel."""
        self.content_panel.clear()
        if form_name == "DashboardForm":
            from ..DashboardForm import DashboardForm
            self.content_panel.add_component(DashboardForm())
        elif form_name == "PersonenForm":
            from ..PersonenForm import PersonenForm
            self.content_panel.add_component(PersonenForm())
        elif form_name == "FahrzeugeForm":
            from ..FahrzeugeForm import FahrzeugeForm
            self.content_panel.add_component(FahrzeugeForm())
        elif form_name == "LagerForm":
            from ..LagerForm import LagerForm
            self.content_panel.add_component(LagerForm())
        elif form_name == "WaffenMunitionForm":
            from ..WaffenMunitionForm import WaffenMunitionForm
            self.content_panel.add_component(WaffenMunitionForm())

        # Link-Styling aktualisieren
        for link in [self.link_dashboard, self.link_personal, self.link_fahrzeuge, 
                     self.link_lager, self.link_waffen]:
            link.bold = False
        if form_name == "DashboardForm": self.link_dashboard.bold = True
        elif form_name == "PersonenForm": self.link_personal.bold = True
        elif form_name == "FahrzeugeForm": self.link_fahrzeuge.bold = True
        elif form_name == "LagerForm": self.link_lager.bold = True
        elif form_name == "WaffenMunitionForm": self.link_waffen.bold = True

    def nav_dashboard(self, **event_args):
        self.load_form("DashboardForm")

    def nav_personal(self, **event_args):
        self.load_form("PersonenForm")

    def nav_fahrzeuge(self, **event_args):
        self.load_form("FahrzeugeForm")

    def nav_lager(self, **event_args):
        self.load_form("LagerForm")

    def nav_waffen(self, **event_args):
        self.load_form("WaffenMunitionForm")
