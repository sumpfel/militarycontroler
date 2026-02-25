from ._anvil_designer import WaffenMunitionFormTemplate
from anvil import *
import anvil.server
from .. import UIUtils

class WaffenMunitionForm(WaffenMunitionFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.bases = anvil.server.call('get_bases_dropdown')
        self.drop_down_basis.items = [("Alle Basen", None)] + [(b['name'], b['basis_id']) for b in self.bases]
        self.load_matches()

    def load_matches(self, **event_args):
        basis_id = self.drop_down_basis.selected_value
        matches = anvil.server.call('get_weapon_ammo_match', basis_id)
        
        # Icons hinzufügen
        for m in matches:
            m['waffe_display'] = f"🔫 {m['waffe_name']}"
            m['muni_display'] = f"🔋 {m['munition_name']}"
            
        self.repeating_panel_matches.items = matches

    def filter_changed(self, **event_args):
        self.load_matches()
