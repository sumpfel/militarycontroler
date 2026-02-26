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
        
        # Header: Name und Status rechtsbündig
        header = FlowPanel()
        header.add_component(Label(text=f"{icon} {v['name']}", bold=True, font_size=20, width=400, foreground="midnightblue"))
        status_label = Label(text=f"Status: {v['status']}", width=200, align="right", bold=True)
        if v['status'] == 'EINSATZBEREIT': status_label.foreground = "green"
        elif v['status'] == 'DEFEKT': status_label.foreground = "red"
        elif v['status'] == 'WARTUNG': status_label.foreground = "orange"
        header.add_component(status_label)
        card.add_component(header)
        
        # Untertitel Info
        card.add_component(Label(text=f"Klasse: {v['typ']}  |  Reg-Nr: {v['kennzeichen']}  |  Stützpunkt: {v['basis_name']}", italic=True, font_size=12))
        
        # Game Stats Panel (ausklappbar oder direkt anzeigen?)
        # Let's show them directly, it's cool
        stats = UIUtils.get_vehicle_stats(v['typ'], v['name'])
        
        stats_panel = FlowPanel(spacing_above="small")
        card.add_component(stats_panel)
        
        # Hilfsfunktion für kleine balken "████░░░░░░"
        def make_bar(val):
            filled = int(val / 10)
            return "█" * filled + "░" * (10 - filled)
            
        stats_panel.add_component(ColumnPanel(components=[
            Label(text="💨 Speed", bold=True),
            Label(text=make_bar(stats['speed']), foreground="blue")
        ], width=150))
        
        stats_panel.add_component(ColumnPanel(components=[
            Label(text="🛡️ Panzerung", bold=True),
            Label(text=make_bar(stats['armor']), foreground="grey")
        ], width=150))
        
        stats_panel.add_component(ColumnPanel(components=[
            Label(text="💥 Feuerkraft", bold=True),
            Label(text=make_bar(stats['firepower']), foreground="red")
        ], width=150))
        
        stats_panel.add_component(ColumnPanel(components=[
            Label(text="⛽ Reichweite", bold=True),
            Label(text=make_bar(stats['range']), foreground="green")
        ], width=150))
        
        return card

    def drop_down_basis_change(self, **event_args):
        self.load_vehicles()

    def drop_down_typ_change(self, **event_args):
        self.load_vehicles()
