from ._anvil_designer import PersonenFormTemplate
from anvil import *
import anvil.server


class PersonenForm(PersonenFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        # Header
        self.add_component(Label(text="Personal", role="headline", spacing_above="small"))
        
        # Filter-Zeile
        filter_panel = FlowPanel(spacing_above="small", spacing_below="small")
        
        # Basis-Dropdown
        self.basis_dropdown = DropDown(placeholder="Alle Basen", include_placeholder=True, width=250)
        bases = anvil.server.call('get_bases_dropdown')
        self.basis_dropdown.items = [(b['name'], b['basis_id']) for b in bases]
        self.basis_dropdown.set_event_handler('change', self.filter_changed)
        filter_panel.add_component(Label(text="Basis: ", bold=True))
        filter_panel.add_component(self.basis_dropdown)
        
        # Suchfeld
        self.search_box = TextBox(placeholder="Name oder Funktion suchen...", width=250)
        self.search_box.set_event_handler('pressed_enter', self.filter_changed)
        filter_panel.add_component(Label(text="  Suche: ", bold=True))
        filter_panel.add_component(self.search_box)
        
        # Suchen-Button
        btn = Button(text="🔍 Suchen", role="primary-color")
        btn.set_event_handler('click', self.filter_changed)
        filter_panel.add_component(btn)
        
        self.add_component(filter_panel)
        
        # Ergebnis-Zähler
        self.result_label = Label(text="", italic=True, spacing_below="small")
        self.add_component(self.result_label)
        
        # DataGrid
        self.grid = DataGrid(auto_header=True, show_page_controls=True, rows_per_page=25)
        self.grid.columns = [
            {"id": "rang", "title": "Rang", "data_key": "rang"},
            {"id": "name", "title": "Name", "data_key": "name"},
            {"id": "funktion", "title": "Funktion", "data_key": "beruf_funktion"},
            {"id": "status", "title": "Status", "data_key": "status"},
            {"id": "freigabe", "title": "Freigabe", "data_key": "sicherheitsfreigabe"},
            {"id": "basis", "title": "Basis", "data_key": "basis_name"},
            {"id": "einheit", "title": "Einheit", "data_key": "einheit_name"},
        ]
        self.add_component(self.grid)
        
        # Daten laden
        self.load_data()
    
    def filter_changed(self, **event_args):
        self.load_data()
    
    def load_data(self):
        basis_id = self.basis_dropdown.selected_value
        search = self.search_box.text if self.search_box.text else None
        persons = anvil.server.call('get_persons', basis_id=basis_id, search_query=search)
        
        self.grid.clear()
        for p in persons:
            row = DataRowPanel(item={
                "rang": p['rang'],
                "name": f"{p['vorname']} {p['nachname']}",
                "beruf_funktion": p['beruf_funktion'],
                "status": p['status'],
                "sicherheitsfreigabe": p['sicherheitsfreigabe'],
                "basis_name": p['basis_name'],
                "einheit_name": p.get('einheit_name') or '-',
            })
            self.grid.add_component(row)
        
        self.result_label.text = f"{len(persons)} Personen gefunden"
