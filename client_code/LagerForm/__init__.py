from ._anvil_designer import LagerFormTemplate
from anvil import *
import anvil.server


class LagerForm(LagerFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        self.add_component(Label(text="Lager & Gegenstände", role="headline", spacing_above="small"))
        
        # Basis-Filter
        filter_panel = FlowPanel(spacing_above="small", spacing_below="small")
        self.basis_dropdown = DropDown(placeholder="Alle Basen", include_placeholder=True, width=250)
        bases = anvil.server.call('get_bases_dropdown')
        self.basis_dropdown.items = [(b['name'], b['basis_id']) for b in bases]
        self.basis_dropdown.set_event_handler('change', self.filter_changed)
        filter_panel.add_component(Label(text="Basis: ", bold=True))
        filter_panel.add_component(self.basis_dropdown)
        self.add_component(filter_panel)
        
        # Container für Lager-Karten
        self.lager_container = ColumnPanel()
        self.add_component(self.lager_container)
        
        self.load_data()
    
    def filter_changed(self, **event_args):
        self.load_data()
    
    def load_data(self):
        basis_id = self.basis_dropdown.selected_value
        warehouses = anvil.server.call('get_warehouses', basis_id=basis_id)
        
        self.lager_container.clear()
        
        for wh in warehouses:
            card = ColumnPanel(role="card", spacing_above="small", spacing_below="small")
            
            # Lager-Header
            header = FlowPanel()
            header.add_component(Label(
                text=f"📦 {wh['bezeichnung']}",
                bold=True, font_size=16
            ))
            header.add_component(Label(
                text=f"  [{wh['typ']}]  |  {wh['basis_name']}  |  {wh['anzahl_items']} Positionen  |  Menge: {wh['gesamt_menge']}",
                italic=True, foreground="gray"
            ))
            card.add_component(header)
            
            # Expand-Button
            items_panel = ColumnPanel(visible=False)
            
            btn = Button(text="📋 Inhalt anzeigen", role="outlined")
            def toggle_items(panel=items_panel, button=btn, lager_id=wh['lager_id']):
                def handler(**event_args):
                    if not panel.visible:
                        panel.visible = True
                        button.text = "📋 Inhalt ausblenden"
                        if len(panel.get_components()) == 0:
                            items = anvil.server.call('get_warehouse_items', lager_id)
                            if items:
                                grid = DataGrid(auto_header=True)
                                grid.columns = [
                                    {"id": "name", "title": "Gegenstand", "data_key": "name"},
                                    {"id": "kategorie", "title": "Kategorie", "data_key": "kategorie"},
                                    {"id": "kaliber", "title": "Kaliber", "data_key": "kaliber"},
                                    {"id": "menge", "title": "Menge", "data_key": "menge"},
                                    {"id": "status", "title": "Status", "data_key": "status"},
                                ]
                                for item in items:
                                    item['kaliber'] = item.get('kaliber') or '-'
                                    row = DataRowPanel(item=item)
                                    grid.add_component(row)
                                panel.add_component(grid)
                            else:
                                panel.add_component(Label(text="Lager ist leer.", italic=True))
                    else:
                        panel.visible = False
                        button.text = "📋 Inhalt anzeigen"
                return handler
            
            btn.set_event_handler('click', toggle_items())
            card.add_component(btn)
            card.add_component(items_panel)
            
            self.lager_container.add_component(card)
