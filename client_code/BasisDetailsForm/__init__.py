from ._anvil_designer import BasisDetailsFormTemplate
from anvil import *
import anvil.server
import plotly.graph_objects as go

class BasisDetailsForm(BasisDetailsFormTemplate):
    def __init__(self, basis_id, **properties):
        self.init_components(**properties)
        self.basis_id = basis_id
        
        self.btn_back.set_event_handler('click', self.back_click)
        self.load_details()

    def load_details(self):
        """Lädt Detail-Statistiken für die ausgewählte Basis und erstellt Graphen."""
        data = anvil.server.call('get_base_details_extended', self.basis_id)
        if not data:
            self.label_title.text = "Basis nicht gefunden."
            return
            
        base = data['base']
        self.label_title.text = f"🛡️ Basis-Auswertung: {base['name']}"
        
        # --- Basis Info ---
        self.flow_info.clear()
        
        # Info Karten im Game-Look (kleine ColumnPanels)
        self.create_info_card("📍 Standort", f"{base['standort_name']}\nKoord: {base['latitude']:.2f}, {base['longitude']:.2f}")
        self.create_info_card("🔐 Sicherheit", base['sicherheitsstufe'])
        kommandant = f"{base.get('kommandant_rang', '')} {base.get('kommandant_name', 'N/A')}"
        self.create_info_card("👨‍✈️ Kommando", kommandant)
        self.create_info_card("📏 Kapazität", f"{base['kapazitaet']} Pers.\nFläche: {base['flaeche']} km²")

        # --- Graphen ---
        # 1. Fahrzeuge (Pie Chart)
        if data['vehicles']:
            labels = [v['typ'] for v in data['vehicles']]
            values = [v['cnt'] for v in data['vehicles']]
            self.plot_vehicles.data = [go.Pie(labels=labels, values=values, hole=.4)]
            self.plot_vehicles.layout.title = "Fahrzeug-Verteilung"
            self.plot_vehicles.layout.margin = dict(l=20, r=20, t=40, b=20)
            self.plot_vehicles.layout.paper_bgcolor = "rgba(0,0,0,0)"
            
        # 2. Personal (Donut Chart)
        if data['personnel']:
            labels = [p['status'] for p in data['personnel']]
            values = [p['cnt'] for p in data['personnel']]
            colors = ['#2ca02c' if s == 'AKTIV' else '#d62728' if s == 'KRANK' else '#1f77b4' for s in labels]
            
            self.plot_personnel.data = [go.Pie(labels=labels, values=values, hole=.5, marker=dict(colors=colors))]
            self.plot_personnel.layout.title = "Personal-Status"
            self.plot_personnel.layout.margin = dict(l=20, r=20, t=40, b=20)
            self.plot_personnel.layout.paper_bgcolor = "rgba(0,0,0,0)"

        # 3. Lager (Bar Chart)
        if data['warehouses']:
            labels = [w['bezeichnung'] for w in data['warehouses']]
            belegung = [w['belegung'] or 0 for w in data['warehouses']]
            kapazitaet = [w['kapazitaet'] for w in data['warehouses']]
            
            trace1 = go.Bar(x=labels, y=belegung, name='Belegt', marker_color='rgb(55, 83, 109)')
            trace2 = go.Bar(x=labels, y=[k-b for k,b in zip(kapazitaet, belegung)], name='Frei', marker_color='rgb(26, 118, 255)')
            
            self.plot_warehouses.data = [trace1, trace2]
            self.plot_warehouses.layout.barmode = 'stack'
            self.plot_warehouses.layout.title = "Lagerkapazitäten"
            self.plot_warehouses.layout.paper_bgcolor = "rgba(0,0,0,0)"


    def create_info_card(self, title, text):
        card = ColumnPanel(role="card", width=200, spacing_above="small")
        card.add_component(Label(text=title, bold=True, foreground="indigo"))
        card.add_component(Label(text=text, font_size=12))
        self.flow_info.add_component(card)

    def back_click(self, **event_args):
        get_open_form().btn_nav_dashboard_click()
