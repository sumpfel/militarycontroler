from ._anvil_designer import PersonenFormTemplate
from anvil import *
import anvil.server
from .. import UIUtils

class PersonenForm(PersonenFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        # Dropdowns initialisieren
        self.bases = anvil.server.call('get_bases_dropdown')
        self.drop_down_basis.items = [("Alle Basen", None)] + [(b['name'], b['basis_id']) for b in self.bases]
        
        self.ranks = anvil.server.call('get_ranks_dropdown')
        self.drop_down_rang.items = [("Alle Ränge", None)] + [(r['bezeichnung'], r['rang_id']) for r in self.ranks]
        
        self.profs = anvil.server.call('get_professions_dropdown')
        self.drop_down_beruf.items = [("Alle Berufe", None)] + [(p, p) for p in self.profs]
        
        self.load_persons()

    def load_persons(self, **event_args):
        """Lädt Personen mit Filtern."""
        basis_id = self.drop_down_basis.selected_value
        rang_id = self.drop_down_rang.selected_value
        beruf = self.drop_down_beruf.selected_value
        search = self.text_box_search.text
        
        persons = anvil.server.call('get_persons', basis_id, search, rang_id, beruf)
        
        self.flow_panel_persons.clear()
        for p in persons:
            card = self.create_person_card(p)
            self.flow_panel_persons.add_component(card)
        
        # Statistik aktualisieren falls sichtbar
        if self.panel_stats.visible:
            self.update_stats()

    def create_person_card(self, p):
        card = ColumnPanel(role="card", spacing_above="medium")
        
        # Header Info
        header = FlowPanel()
        prof_icon = UIUtils.get_icon(p['beruf_funktion'], p['beruf_funktion'])
        name_label = Label(text=f"{prof_icon} {p['rang']} {p['vorname']} {p['nachname']}", bold=True, font_size=18, width=400)
        status_label = Label(text=p['status'], width=150)
        
        if p['status'] == 'AKTIV': status_label.foreground = "green"
        elif p['status'] == 'KRANK': status_label.foreground = "red"
        
        header.add_component(name_label)
        header.add_component(status_label)
        card.add_component(header)
        
        card.add_component(Label(text=f"{p['beruf_funktion']} | Einheit: {p.get('einheit_name', 'Keine')} | Basis: {p['basis_name']}", italic=True))
        
        details_panel = ColumnPanel(visible=False, spacing_above="small")
        card.add_component(details_panel)
        btn_details = Button(text="Details & Ausrüstung", role="secondary-color")
        
        def toggle_details(**e):
            if not details_panel.visible:
                assignments = anvil.server.call('get_person_assignments', p['person_id'])
                details_panel.clear()
                details_panel.add_component(Label(text="📄 Stammdaten", bold=True))
                details_panel.add_component(Label(text=f"Geburtsdatum: {p['geburtsdatum']} | Geschlecht: {p['geschlecht']} | Freigabe: {p['sicherheitsfreigabe']}"))
                
                details_panel.add_component(Label(text="🚗 Fahrzeuge", bold=True, spacing_above="small"))
                if assignments['vehicles']:
                    for f in assignments['vehicles']:
                        icon = UIUtils.get_icon(f['typ'], f['name'])
                        details_panel.add_component(Label(text=f"{icon} {f['name']} ({f['kennzeichen']})"))
                else:
                    details_panel.add_component(Label(text="Keine Zuweisungen.", italic=True))
                
                details_panel.add_component(Label(text="🎒 Ausrüstung", bold=True, spacing_above="small"))
                if assignments['items']:
                    for i in assignments['items']:
                        icon = UIUtils.get_icon(i['kategorie'], i['name'])
                        details_panel.add_component(Label(text=f"{icon} {i['name']} (x{i['zugewiesene_menge']})"))
                else:
                    details_panel.add_component(Label(text="Keine Zuweisungen.", italic=True))
                
                details_panel.visible = True
                btn_details.text = "Details schließen"
            else:
                details_panel.visible = False
                btn_details.text = "Details & Ausrüstung"
                
        btn_details.set_event_handler('click', toggle_details)
        card.add_component(btn_details)
        return card

    def btn_toggle_stats_click(self, **event_args):
        if not self.panel_stats.visible:
            self.update_stats()
            self.panel_stats.visible = True
            self.btn_toggle_stats.text = "Statistik ausblenden"
        else:
            self.panel_stats.visible = False
            self.btn_toggle_stats.text = "Statistik anzeigen"

    def update_stats(self):
        """Aktualisiert die Statistik-Labels."""
        basis_id = self.drop_down_basis.selected_value
        stats = anvil.server.call('get_personnel_stats', basis_id)
        
        self.flow_stats_ranks.clear()
        for r in stats['ranks']:
            self.flow_stats_ranks.add_component(Label(text=f"{r['bezeichnung']}: {r['cnt']}  |  ", font_size=12))
            
        self.flow_stats_profs.clear()
        for p in stats['professions']:
            icon = UIUtils.get_icon(p['beruf_funktion'], p['beruf_funktion'])
            self.flow_stats_profs.add_component(Label(text=f"{icon} {p['beruf_funktion']}: {p['cnt']}  |  ", font_size=12))

    def drop_down_basis_change(self, **event_args):
        self.load_persons()

    def drop_down_rang_change(self, **event_args):
        self.load_persons()

    def drop_down_beruf_change(self, **event_args):
        self.load_persons()

    def btn_search_click(self, **event_args):
        self.load_persons()
