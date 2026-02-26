from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
class Form1(Form1Template):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.load_form("DashboardForm")
    def load_form(self, form_name):
        self.content_panel.clear()
        self.add_nav_buttons()
        if form_name == "DashboardForm":
            from ..DashboardForm import DashboardForm
            target = DashboardForm()
        elif form_name == "PersonenForm":
            from ..PersonenForm import PersonenForm
            target = PersonenForm()
        elif form_name == "FahrzeugeForm":
            from ..FahrzeugeForm import FahrzeugeForm
            target = FahrzeugeForm()
        elif form_name == "LagerForm":
            from ..LagerForm import LagerForm
            target = LagerForm()
        elif form_name == "WaffenMunitionForm":
            from ..WaffenMunitionForm import WaffenMunitionForm
            target = WaffenMunitionForm()
        elif form_name == "BasisDetailsForm":
            from ..BasisDetailsForm import BasisDetailsForm
            target = BasisDetailsForm(basis_id=self.selected_basis_id)
        self.content_panel.add_component(target)
    def add_nav_buttons(self):
        nav_panel = FlowPanel(spacing_above="small", spacing_below="large")
        links = [
            ("🏠 Dashboard", "DashboardForm"),
            ("👤 Personal", "PersonenForm"),
            ("🚗 Fahrzeuge", "FahrzeugeForm"),
            ("📦 Lager", "LagerForm"),
            ("🔫 Waffen", "WaffenMunitionForm")
        ]
        for text, form in links:
            btn = Button(text=text, role="raised")
            btn.set_event_handler('click', lambda f=form, **e: self.load_form(f))
            nav_panel.add_component(btn)
        self.content_panel.add_component(nav_panel)
    def btn_nav_dashboard_click(self, **event_args):
        self.load_form("DashboardForm")
    def btn_nav_personal_click(self, **event_args):
        self.load_form("PersonenForm")
    def btn_nav_fahrzeuge_click(self, **event_args):
        self.load_form("FahrzeugeForm")
    def btn_nav_lager_click(self, **event_args):
        self.load_form("LagerForm")
    def btn_nav_waffen_click(self, **event_args):
        self.load_form("WaffenMunitionForm")
    def open_basis_details(self, basis_id):
        self.selected_basis_id = basis_id
        self.load_form("BasisDetailsForm")
