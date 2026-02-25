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
        """Lädt Fahrzeuge als Karten."""
        basis_id = self.drop_down_basis.selected_value
        typ = self.drop_down_typ.selected_value
        vehicles = anvil.server.call('get_vehicles', basis_id, typ)
        
        self.flow_panel_vehicles.clear()
        for v in vehicles:
            card = self.create_vehicle_card(v)
            self.flow_panel_vehicles.add_component(card)

    def create_vehicle_card(self, v):
        card = ColumnPanel(role="card", spacing_above="medium")
        icon = UIUtils.get_icon(v['typ'], v['name'])
        header = Label(text=f"{icon} {v['name']}", bold=True, font_size=18)
        card.add_component(header)
        
        info = Label(text=f"Typ: {v['typ']} | Kennzeichen: {v['kennzeichen']} | Basis: {v['basis_name']}", italic=True)
        card.add_component(info)
        
        status_label = Label(text=f"Status: {v['status']}")
        if v['status'] == 'EINSATZBEREIT': status_label.foreground = "green"
        elif v['status'] == 'DEFEKT': status_label.foreground = "red"
        card.add_component(status_label)
        
        return card

    def drop_down_basis_change(self, **event_args):
        self.load_vehicles()

    def drop_down_typ_change(self, **event_args):
        self.load_vehicles()
