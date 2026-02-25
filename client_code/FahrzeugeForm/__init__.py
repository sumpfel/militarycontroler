from ._anvil_designer import FahrzeugeFormTemplate
from anvil import *
import anvil.server


class FahrzeugeForm(FahrzeugeFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        self.add_component(Label(text="Fahrzeuge", role="headline", spacing_above="small"))
        
        # Filter
        filter_panel = FlowPanel(spacing_above="small", spacing_below="small")
        
        self.basis_dropdown = DropDown(placeholder="Alle Basen", include_placeholder=True, width=250)
        bases = anvil.server.call('get_bases_dropdown')
        self.basis_dropdown.items = [(b['name'], b['basis_id']) for b in bases]
        self.basis_dropdown.set_event_handler('change', self.filter_changed)
        filter_panel.add_component(Label(text="Basis: ", bold=True))
        filter_panel.add_component(self.basis_dropdown)
        
        self.typ_dropdown = DropDown(placeholder="Alle Typen", include_placeholder=True, width=200)
        types = anvil.server.call('get_vehicle_types')
        self.typ_dropdown.items = [(t['typ'], t['typ']) for t in types]
        self.typ_dropdown.set_event_handler('change', self.filter_changed)
        filter_panel.add_component(Label(text="  Typ: ", bold=True))
        filter_panel.add_component(self.typ_dropdown)
        
        self.add_component(filter_panel)
        
        self.result_label = Label(text="", italic=True, spacing_below="small")
        self.add_component(self.result_label)
        
        # DataGrid
        self.grid = DataGrid(auto_header=True, show_page_controls=True, rows_per_page=25)
        self.grid.columns = [
            {"id": "typ", "title": "Typ", "data_key": "typ"},
            {"id": "name", "title": "Modell", "data_key": "name"},
            {"id": "kennzeichen", "title": "Kennzeichen", "data_key": "kennzeichen"},
            {"id": "status", "title": "Status", "data_key": "status"},
            {"id": "basis", "title": "Basis", "data_key": "basis_name"},
        ]
        self.add_component(self.grid)
        self.load_data()
    
    def filter_changed(self, **event_args):
        self.load_data()
    
    def load_data(self):
        basis_id = self.basis_dropdown.selected_value
        typ = self.typ_dropdown.selected_value
        vehicles = anvil.server.call('get_vehicles', basis_id=basis_id, typ=typ)
        
        self.grid.clear()
        for v in vehicles:
            row = DataRowPanel(item=v)
            self.grid.add_component(row)
        
        self.result_label.text = f"{len(vehicles)} Fahrzeuge gefunden"
