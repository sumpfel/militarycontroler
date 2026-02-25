from ._anvil_designer import WaffenMunitionFormTemplate
from anvil import *
import anvil.server


class WaffenMunitionForm(WaffenMunitionFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        self.add_component(Label(text="Waffen ↔ Munition", role="headline", spacing_above="small"))
        self.add_component(Label(
            text="Verknüpfung von Waffen und passender Munition über das Kaliber",
            italic=True, foreground="gray", spacing_below="small"
        ))
        
        # Basis-Filter
        filter_panel = FlowPanel(spacing_above="small", spacing_below="small")
        self.basis_dropdown = DropDown(placeholder="Alle Basen", include_placeholder=True, width=250)
        bases = anvil.server.call('get_bases_dropdown')
        self.basis_dropdown.items = [(b['name'], b['basis_id']) for b in bases]
        self.basis_dropdown.set_event_handler('change', self.filter_changed)
        filter_panel.add_component(Label(text="Basis: ", bold=True))
        filter_panel.add_component(self.basis_dropdown)
        self.add_component(filter_panel)
        
        # DataGrid
        self.grid = DataGrid(auto_header=True, show_page_controls=True, rows_per_page=30)
        self.grid.columns = [
            {"id": "waffe", "title": "Waffe", "data_key": "waffe_name"},
            {"id": "kaliber", "title": "Kaliber", "data_key": "kaliber"},
            {"id": "w_menge", "title": "Waffen Stk.", "data_key": "waffe_menge"},
            {"id": "munition", "title": "Passende Munition", "data_key": "munition_name"},
            {"id": "m_menge", "title": "Muni Menge", "data_key": "munition_menge"},
            {"id": "m_status", "title": "Muni Status", "data_key": "munition_status"},
            {"id": "basis", "title": "Basis", "data_key": "basis_name"},
        ]
        self.add_component(self.grid)
        
        self.result_label = Label(text="", italic=True, spacing_above="small")
        self.add_component(self.result_label)
        
        self.load_data()
    
    def filter_changed(self, **event_args):
        self.load_data()
    
    def load_data(self):
        basis_id = self.basis_dropdown.selected_value
        matches = anvil.server.call('get_weapon_ammo_match', basis_id=basis_id)
        
        self.grid.clear()
        for m in matches:
            row = DataRowPanel(item=m)
            self.grid.add_component(row)
        
        self.result_label.text = f"{len(matches)} Waffen-Munition-Verknüpfungen gefunden"
