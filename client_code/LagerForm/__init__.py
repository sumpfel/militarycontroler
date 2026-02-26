from ._anvil_designer import LagerFormTemplate
from anvil import *
import anvil.server
from .. import UIUtils
class LagerForm(LagerFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.bases = anvil.server.call('get_bases_dropdown')
        self.drop_down_basis.items = [("Alle Basen", None)] + [(b['name'], b['basis_id']) for b in self.bases]
        self.load_warehouses()
    def load_warehouses(self, **event_args):
        basis_id = self.drop_down_basis.selected_value
        warehouses = anvil.server.call('get_warehouses', basis_id)
        self.flow_panel_lager.clear()
        for w in warehouses:
            card = self.create_lager_card(w)
            self.flow_panel_lager.add_component(card)
    def create_lager_card(self, w):
        card = ColumnPanel(role="card", spacing_above="medium")
        header = Label(text=f"{UIUtils.get_icon(w['typ'])} {w['bezeichnung']} ({w['basis_name']})", bold=True, font_size=18)
        card.add_component(header)
        card.add_component(Label(text=f"Typ: {w['typ']} | Kapazität: {w['kapazitaet']} | Items: {w['anzahl_items']}", italic=True))
        details_panel = ColumnPanel(visible=False, spacing_above="small")
        card.add_component(details_panel)
        btn = Button(text="Inhalt anzeigen", role="secondary-color")
        def toggle_items(**e):
            if not details_panel.visible:
                items = anvil.server.call('get_warehouse_items', w['lager_id'])
                details_panel.clear()
                for i in items:
                    icon = UIUtils.get_icon(i['kategorie'], i['name'])
                    details_panel.add_component(Label(text=f"{icon} {i['name']} (x{i['menge']}) - {i['status']}"))
                details_panel.visible = True
                btn.text = "Inhalt verbergen"
            else:
                details_panel.visible = False
                btn.text = "Inhalt anzeigen"
        btn.set_event_handler('click', toggle_items)
        card.add_component(btn)
        return card
