from ._anvil_designer import PersonenFormTemplate
from anvil import *
import anvil.server
from .. import UIUtils

class PersonenForm(PersonenFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.page = 1
        self.page_size = 20
        self.all_persons = []
        
        # Dropdowns initialisieren
        self.bases = anvil.server.call('get_bases_dropdown')
        self.drop_down_basis.items = [("Alle Basen", None)] + [(b['name'], b['basis_id']) for b in self.bases]
        
        self.ranks = anvil.server.call('get_ranks_dropdown')
        self.drop_down_rang.items = [("Alle Ränge", None)] + [(r['bezeichnung'], r['rang_id']) for r in self.ranks]
        
        self.profs = anvil.server.call('get_professions_dropdown')
        self.drop_down_beruf.items = [("Alle Berufe", None)] + [(p, p) for p in self.profs]
        
        self.load_persons()

    def load_persons(self, **event_args):
        """Lädt alle Personen vom Server und zeigt die erste Seite an."""
        basis_id = self.drop_down_basis.selected_value
        rang_id = self.drop_down_rang.selected_value
        beruf = self.drop_down_beruf.selected_value
        search = self.text_box_search.text
        
        self.all_persons = anvil.server.call('get_persons', basis_id, search, rang_id, beruf)
        self.page = 1
        self.display_page()
        
        # Statistik aktualisieren falls sichtbar
        if self.panel_stats.visible:
            self.update_stats()

    def display_page(self):
        """Zeigt die aktuelle Seite der Personenliste an."""
        start = (self.page - 1) * self.page_size
        end = start + self.page_size
        page_items = self.all_persons[start:end]
        
        self.flow_panel_persons.clear()
        for p in page_items:
            card = self.create_person_card(p)
            self.flow_panel_persons.add_component(card)
            
        self.label_page.text = f"Seite {self.page}"
        self.btn_prev.enabled = self.page > 1
        self.btn_next.enabled = end < len(self.all_persons)

    def create_person_card(self, p):
        # Äußerer Card-Container
        card = ColumnPanel(role="card", spacing_above="medium")
        
        # 1. Header (Name, Rang, Icon)
        header_panel = FlowPanel()
        prof_icon = UIUtils.get_icon(p['beruf_funktion'], p['beruf_funktion'])
        header_panel.add_component(Label(text=f"{prof_icon} {p['rang']} {p['vorname']} {p['nachname']}", bold=True, font_size=22, foreground="midnightblue", width=400))
        
        # 2. HP/Status Bar (Game-Like)
        hp_val = 100 if p['status'] == 'AKTIV' else 50 if p['status'] == 'URLAUB' else 10
        hp_color = "green" if hp_val == 100 else "blue" if hp_val == 50 else "red"
        hp_bar = "█" * int(hp_val/10) + "░" * (10 - int(hp_val/10))
        
        status_panel = ColumnPanel(width=150)
        status_panel.add_component(Label(text=f"Status: {p['status']}", bold=True))
        status_panel.add_component(Label(text=hp_bar, foreground=hp_color, font_size=16, spacing_above="none", spacing_below="none"))
        header_panel.add_component(status_panel)
        
        card.add_component(header_panel)
        
        # 3. Untertitel (Klasse / Bio)
        card.add_component(Label(text=f"Klasse: {p['beruf_funktion']}  |  Zugehörigkeit: {p.get('einheit_name', 'Stab')}  |  Standort: {p['basis_name']}", italic=True))
        
        # 4. Details Container (Hidden by default)
        details_panel = ColumnPanel(visible=False, spacing_above="small")
        card.add_component(details_panel)
        
        btn_details = Button(text="⬇ Charakterbogen & Inventar anzeigen", role="secondary-color")
        
        def toggle_details(**e):
            if not details_panel.visible:
                assignments = anvil.server.call('get_person_assignments', p['person_id'])
                details_panel.clear()
                
                # Stammdaten im Game-Look
                details_panel.add_component(Label(text="📝 Spielerprofil", bold=True, foreground="indigo", font_size=16))
                details_panel.add_component(Label(text=f"Geburtstag: {p['geburtsdatum']} | Geschlecht: {p['geschlecht']} | Freigabe-Level: {p['sicherheitsfreigabe']}"))
                
                # Fahrzeuge / Mounts
                details_panel.add_component(Label(text="🚗 Zugewiesene Mounts (Fahrzeuge)", bold=True, spacing_above="medium", foreground="indigo", font_size=16))
                if assignments['vehicles']:
                    mount_grid = FlowPanel()
                    for f in assignments['vehicles']:
                        mount_slot = ColumnPanel(role="card", width=250)
                        icon = UIUtils.get_icon(f['typ'], f['name'])
                        mount_slot.add_component(Label(text=f"{icon} {f['name']}", bold=True))
                        mount_slot.add_component(Label(text=f"Reg: {f['kennzeichen']}", font_size=12, italic=True))
                        mount_grid.add_component(mount_slot)
                    details_panel.add_component(mount_grid)
                else:
                    details_panel.add_component(Label(text="Kein Mount zugewiesen.", italic=True, foreground="gray"))
                
                # Inventar / Items (als Grid)
                details_panel.add_component(Label(text="🎒 Inventar", bold=True, spacing_above="medium", foreground="indigo", font_size=16))
                if assignments['items']:
                    inv_grid = FlowPanel()
                    for i in assignments['items']:
                        # "Inventar Slot" Design
                        slot = ColumnPanel(role="card", width=150)
                        icon = UIUtils.get_icon(i['kategorie'], i['name'])
                        slot.add_component(Label(text=icon, align="center", font_size=32, spacing_above="none", spacing_below="none"))
                        slot.add_component(Label(text=i['name'], align="center", bold=True, font_size=12))
                        slot.add_component(Label(text=f"x{i.get('zugewiesene_menge', i['menge'])}", align="center", foreground="gray", font_size=12))
                        inv_grid.add_component(slot)
                    details_panel.add_component(inv_grid)
                else:
                    details_panel.add_component(Label(text="Inventar leer.", italic=True, foreground="gray"))
                
                details_panel.visible = True
                btn_details.text = "⬆ Charakterbogen schließen"
            else:
                details_panel.visible = False
                btn_details.text = "⬇ Charakterbogen & Inventar anzeigen"
                
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
        """Aktualisiert die Statistik-Labels basierend auf den aktuellen Filtern."""
        basis_id = self.drop_down_basis.selected_value
        stats = anvil.server.call('get_personnel_stats', basis_id)
        
        total = sum(r['cnt'] for r in stats['ranks'])
        self.panel_stats.add_component(Label(text=f"Gesamtpersonal: {total}", bold=True, foreground="blue"), index=0)

        self.flow_stats_ranks.clear()
        for r in stats['ranks']:
            self.flow_stats_ranks.add_component(Label(text=f"{r['bezeichnung']}: {r['cnt']}  |  ", font_size=10))
            
        self.flow_stats_profs.clear()
        for p in stats['professions']:
            icon = UIUtils.get_icon(p['beruf_funktion'], p['beruf_funktion'])
            self.flow_stats_profs.add_component(Label(text=f"{icon} {p['beruf_funktion']}: {p['cnt']}  |  ", font_size=10))

    def btn_prev_click(self, **event_args):
        if self.page > 1:
            self.page -= 1
            self.display_page()

    def btn_next_click(self, **event_args):
        if self.page * self.page_size < len(self.all_persons):
            self.page += 1
            self.display_page()

    def drop_down_basis_change(self, **event_args):
        self.load_persons()

    def drop_down_rang_change(self, **event_args):
        self.load_persons()

    def drop_down_beruf_change(self, **event_args):
        self.load_persons()

    def btn_search_click(self, **event_args):
        self.load_persons()
