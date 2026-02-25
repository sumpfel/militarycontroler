from ._anvil_designer import FahrzeugeFormTemplate
from anvil import *
import anvil.server
from .. import UIUtils

class FahrzeugeForm(FahrzeugeFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.bases = anvil.server.call('get_bases_dropdown')
        self.types = anvil.server.call('get_vehicle_types')
        
        self.drop_down_basis.items = [("Alle Basen", None)] + [(b['name'], b['basis_id']) for b in self.bases]
        self.drop_down_typ.items = [("Alle Typen", None)] + [(t['typ'], t['typ']) for t in self.types]
        
        self.load_vehicles()

    def load_vehicles(self, **event_args):
        """Lädt Fahrzeuge mit Icons."""
        basis_id = self.drop_down_basis.selected_value
        typ = self.drop_down_typ.selected_value
        vehicles = anvil.server.call('get_vehicles', basis_id, typ)
        
        # Icon hinzufügen
        for v in vehicles:
            icon = UIUtils.get_icon(v['typ'], v['name'])
            v['display_name'] = f"{icon} {v['name']}"
            
        self.repeating_panel_fahrzeuge.items = vehicles
