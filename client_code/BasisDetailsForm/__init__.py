from ._anvil_designer import BasisDetailsFormTemplate
from anvil import *
import anvil.server


class BasisDetailsForm(BasisDetailsFormTemplate):
    def __init__(self, basis_id, **properties):
        self.init_components(**properties)
        self.basis_id = basis_id
        self.load_details()

    def load_details(self):
        """Lädt Detail-Statistiken für die ausgewählte Basis."""
        data = anvil.server.call('get_base_details_extended', self.basis_id)
        if not data:
            self.add_component(Label(text="Basis nicht gefunden.", role="headline"))
            return
            
        base = data['base']
        
        # Titel & Header
        self.add_component(Button(text="⬅ Zurück zum Dashboard", role="secondary-color", click=self.back_click))
        self.add_component(Label(text=f"Basis-Details: {base['name']}", role="headline", spacing_above="medium"))
        
        # Details-Grid (Zwei Spalten)
        details_panel = ColumnPanel(role="card", spacing_above="medium")
        
        info_flow = FlowPanel()
        info_flow.add_component(Label(text=f"📍 Standort: {base['standort_name']} ({base['latitude']}, {base['longitude']})", width=400))
        info_flow.add_component(Label(text=f"🛡️ Sicherheitsstufe: {base['sicherheitsstufe']}", width=300))
        info_flow.add_component(Label(text=f"👨‍✈️ Kommandant: {base.get('kommandant_rang', '')} {base.get('kommandant_name', 'N/A')}", width=350))
        info_flow.add_component(Label(text=f"📏 Fläche: {base['flaeche']} km²", width=200))
        details_panel.add_component(info_flow)
        
        self.add_component(details_panel)

        # Statistiken (Fahrzeuge, Personal, Lager)
        stats_row = FlowPanel(spacing_above="large")
        
        # 1. Fahrzeuge nach Typ
        v_panel = ColumnPanel(role="card", width=350)
        v_panel.add_component(Label(text="Fahrzeugbestand", bold=True, font_size=18))
        for v in data['vehicles']:
            v_panel.add_component(Label(text=f"{v['typ']}: {v['cnt']}"))
        if not data['vehicles']:
            v_panel.add_component(Label(text="Keine Fahrzeuge stationiert.", italic=True))
        stats_row.add_component(v_panel)
        
        # 2. Personal nach Status
        p_panel = ColumnPanel(role="card", width=350)
        p_panel.add_component(Label(text="Personalstatus", bold=True, font_size=18))
        for p in data['personnel']:
            p_panel.add_component(Label(text=f"{p['status']}: {p['cnt']}"))
        stats_row.add_component(p_panel)
        
        # 3. Lagerfüllstand (Top 5)
        w_panel = ColumnPanel(role="card", width=400)
        w_panel.add_component(Label(text="Lagerkapazitäten", bold=True, font_size=18))
        for w in data['warehouses']:
            belegung = w['belegung'] or 0
            prozent = (belegung / w['kapazitaet'] * 100) if w['kapazitaet'] > 0 else 0
            w_panel.add_component(Label(text=f"📦 {w['bezeichnung']}: {belegung}/{w['kapazitaet']} ({prozent:.1f}%)"))
        stats_row.add_component(w_panel)
        
        self.add_component(stats_row)

    def back_click(self, **event_args):
        get_open_form().nav_dashboard()
