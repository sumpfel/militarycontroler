from ._anvil_designer import PersonenFormTemplate
from anvil import *
import anvil.server
from .. import UIUtils

class PersonenForm(PersonenFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.bases = anvil.server.call('get_bases_dropdown')
        self.drop_down_basis.items = [("Alle Basen", None)] + [(b['name'], b['basis_id']) for b in self.bases]
        self.load_persons()

    def load_persons(self, **event_args):
        """Lädt Personen in das FlowPanel als Karten."""
        basis_id = self.drop_down_basis.selected_value
        search = self.text_box_search.text
        persons = anvil.server.call('get_persons', basis_id, search)
        
        self.flow_panel_persons.clear()
        for p in persons:
            card = self.create_person_card(p)
            self.flow_panel_persons.add_component(card)

    def create_person_card(self, p):
        card = ColumnPanel(role="card", spacing_above="medium")
        
        # Header Info
        header = FlowPanel()
        name_label = Label(text=f"{p['rang']} {p['vorname']} {p['nachname']}", bold=True, font_size=18, width=400)
        status_label = Label(text=p['status'], width=150)
        
        # Status Farben
        if p['status'] == 'AKTIV': status_label.foreground = "green"
        elif p['status'] == 'KRANK': status_label.foreground = "red"
        
        header.add_component(name_label)
        header.add_component(status_label)
        card.add_component(header)
        
        # Sub-Info
        card.add_component(Label(text=f"{p.get('beruf_funktion', 'Soldat')} | Einheit: {p.get('einheit_name', 'Keine')} | Basis: {p['basis_name']}", italic=True))
        
        # Details Panel (versteckt)
        details_panel = ColumnPanel(visible=False, spacing_above="small")
        card.add_component(details_panel)
        
        btn_details = Button(text="Details & Ausrüstung", role="secondary-color")
        
        def toggle_details(**e):
            if not details_panel.visible:
                # Daten nachladen
                assignments = anvil.server.call('get_person_assignments', p['person_id'])
                details_panel.clear()
                
                # Stammdaten
                details_panel.add_component(Label(text="📄 Stammdaten", bold=True))
                details_panel.add_component(Label(text=f"Geburtsdatum: {p['geburtsdatum']} | Geschlecht: {p['geschlecht']} | Freigabe: {p['sicherheitsfreigabe']}"))
                
                # Fahrzeuge
                details_panel.add_component(Label(text="🚗 Zugewiesene Fahrzeuge", bold=True, spacing_above="small"))
                if assignments['vehicles']:
                    for f in assignments['vehicles']:
                        icon = UIUtils.get_icon(f['typ'], f['name'])
                        details_panel.add_component(Label(text=f"{icon} {f['name']} ({f['kennzeichen']}) - {f['status']}"))
                else:
                    details_panel.add_component(Label(text="Keine Fahrzeuge zugewiesen.", italic=True))
                
                # Gegenstände
                details_panel.add_component(Label(text="🎒 Ausrüstung / Gegenstände", bold=True, spacing_above="small"))
                if assignments['items']:
                    for i in assignments['items']:
                        icon = UIUtils.get_icon(i['kategorie'], i['name'])
                        details_panel.add_component(Label(text=f"{icon} {i['name']} (x{i.get('zugewiesene_menge', i['menge'])}) - {i['status']}"))
                else:
                    details_panel.add_component(Label(text="Keine Gegenstände zugewiesen.", italic=True))
                
                details_panel.visible = True
                btn_details.text = "Details schließen"
            else:
                details_panel.visible = False
                btn_details.text = "Details & Ausrüstung"
                
        btn_details.set_event_handler('click', toggle_details)
        card.add_component(btn_details)
        
        return card

    def drop_down_basis_change(self, **event_args):
        self.load_persons()

    def btn_search_click(self, **event_args):
        self.load_persons()

    def filter_changed(self, **event_args):
        self.load_persons()
