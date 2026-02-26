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
        self.flow_panel_matches.clear()
        for m in matches:
            card = self.create_match_card(m)
            self.flow_panel_matches.add_component(card)
    def create_match_card(self, m):
        card = ColumnPanel(role="card", spacing_above="medium")
        header = Label(text=f"🔫 {m['waffe_name']} ({m['kaliber']}) - Gesamt: {m['waffe_menge']}", bold=True, font_size=16)
        card.add_component(header)
        ammo_info = Label(text=f"Passende Munition: 🔋 {m['munition_name']} (Menge: {m['munition_menge']})", foreground="indigo")
        card.add_component(ammo_info)
        lager_info = Label(text=f"Waffenlager: {m['waffe_lager']} | Munitionslager: {m['munition_lager']}", italic=True, font_size=12)
        card.add_component(lager_info)
        return card
    def drop_down_basis_change(self, **event_args):
        self.load_matches()
