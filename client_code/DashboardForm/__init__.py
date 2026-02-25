from ._anvil_designer import DashboardFormTemplate
from anvil import *
import anvil.server


class DashboardForm(DashboardFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.load_dashboard()

    def load_dashboard(self):
        """Lädt Dashboard-Statistiken und Karten-Daten vom Server."""
        stats = anvil.server.call('get_dashboard_stats')
        bases = anvil.server.call('get_base_overview')
        locations = anvil.server.call('get_all_base_locations')

        # Google Map hinzufügen
        self.add_component(Label(text="📍 Standortübersicht", role="headline", spacing_above="small"))
        map_comp = GoogleMap(height=400, center={"lat": 51.1657, "lng": 10.4515}, zoom=6)
        for loc in locations:
            marker = GoogleMap.Marker(position={"lat": loc['latitude'], "lng": loc['longitude']}, title=loc['name'])
            marker.set_event_handler('click', lambda l=loc, **e: self.open_details(l['basis_id']))
            map_comp.add_component(marker)
        self.add_component(map_comp)

        # Statistik-Karten
        stats_panel = FlowPanel(spacing_above="large", spacing_below="large")
        
        stat_items = [
            ("🏰 Basen", stats['militaerbasis']),
            ("👤 Personal", stats['person']),
            ("🚗 Fahrzeuge", stats['fahrzeug']),
            ("📦 Gegenstände", stats['gegenstand']),
            ("🏭 Lager", stats['lager']),
            ("⚔️ Einheiten", stats['einheit']),
        ]
        for label, count in stat_items:
            card = ColumnPanel(role="card", spacing_above="small", spacing_below="small")
            card.add_component(Label(text=label, font_size=14, bold=True))
            card.add_component(Label(text=str(count), font_size=32, bold=True, align="center"))
            stats_panel.add_component(card)
        
        self.add_component(Label(text="Dashboard", role="headline", spacing_above="small"))
        self.add_component(stats_panel)

        # Personal-Status
        self.add_component(Label(text="Personal nach Status", role="headline", font_size=20, spacing_above="large"))
        status_panel = FlowPanel(spacing_above="small", spacing_below="large")
        status_colors = {"AKTIV": "green", "KRANK": "orange", "URLAUB": "blue", "SUSPENDIERT": "red"}
        for s in stats.get('person_status', []):
            card = ColumnPanel(role="card")
            card.add_component(Label(text=s['status'], bold=True, foreground=status_colors.get(s['status'], 'black')))
            card.add_component(Label(text=str(s['cnt']), font_size=24, bold=True, align="center"))
            status_panel.add_component(card)
        self.add_component(status_panel)

        # Basen-Übersicht
        self.add_component(Label(text="Basen-Übersicht", role="headline", font_size=20, spacing_above="large"))
        
        grid = DataGrid(auto_header=True)
        grid.columns = [
            {"id": "name", "title": "Basis", "data_key": "name"},
            {"id": "kommandant", "title": "Kommandant", "data_key": "kommandant"},
            {"id": "sicherheit", "title": "Sicherheit", "data_key": "sicherheitsstufe"},
            {"id": "personal", "title": "Personal", "data_key": "anzahl_personal"},
            {"id": "fahrzeuge", "title": "Fahrzeuge", "data_key": "anzahl_fahrzeuge"},
            {"id": "einheiten", "title": "Einheiten", "data_key": "anzahl_einheiten"},
            {"id": "lager", "title": "Lager", "data_key": "anzahl_lager"},
        ]
        for base in bases:
            # Name als Link für Details
            name_link = Link(text=base['name'], bold=True)
            name_link.set_event_handler('click', lambda b=base, **e: self.open_details(b['basis_id']))
            
            row = DataRowPanel(item={
                "name": name_link,
                "kommandant": f"{base.get('kommandant_rang', '')} {base.get('kommandant_name', 'N/A')}",
                "sicherheitsstufe": base['sicherheitsstufe'],
                "anzahl_personal": base['anzahl_personal'],
                "anzahl_fahrzeuge": base['anzahl_fahrzeuge'],
                "anzahl_einheiten": base['anzahl_einheiten'],
                "anzahl_lager": base['anzahl_lager'],
            })
            grid.add_component(row)
        self.add_component(grid)

    def open_details(self, basis_id):
        # Wir rufen eine Methode in Form1 auf
        get_open_form().open_basis_details(basis_id)
