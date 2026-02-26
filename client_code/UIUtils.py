def get_icon(entity_type, name=None):
    """Gibt ein passendes Emoji-Icon für Fahrzeuge und Gegenstände zurück."""
    mapping = {
        # Fahrzeuge
        "PANZER": "🚜",
        "LKW": "🚚",
        "JEEP": "🚙",
        "FLUGZEUG": "✈️",
        "HUBSCHRAUBER": "🚁",
        "BOOT": "🚢",
        "TRANSPORTER": "🚐",
        "STAB": "🏢",
        "INFANTERIE": "🎖️",
        "LOGISTIK": "📦",

        # Berufe / Funktionen
        "Soldat": "🪖",
        "Koch": "👨‍🍳",
        "Mechaniker": "🔧",
        "Sanitäter": "🩺",
        "Fernmelder": "☎️",
        "Pilot": "👨‍✈️",
        "Fahrer": "🚛",
        "Waffenmechaniker": "🛠️",
        "IT-Spezialist": "💻",
        "Ausbilder": "👨‍🏫",
        "Aufklärer": "🔭",
        
        # Gegenstände (Kategorien)
        "WAFFE": "🔫",
        "MUNITION": "🔋",
        "AUSRUESTUNG": "🎒",
        "ELEKTRONIK": "💻",
        "MEDIZIN": "💊",
        "VERPFLEGUNG": "🍞",
        
        # Lager Typen
        "WAFFENLAGER": "🔫",
        "MUNITIONSLAGER": "🔋",
        "LEBENSMITTEL": "🍎",
        "TREIBSTOFF": "⛽",
    }
    
    # Spezifische Namens-Mappings (optional)
    if name:
        name_lower = name.lower()
        if "leopard" in name_lower: return "🚜"
        if "eurofighter" in name_lower: return "✈️"
        if "tiger" in name_lower: return "🚁"
        if "fregatte" in name_lower: return "🚢"
        if "g36" in name_lower: return "🔫"
        if "patrone" in name_lower or "munition" in name_lower: return "🔋"

    return mapping.get(entity_type, "📦")

def get_vehicle_stats(typ, name):
    """Generiert RPG-artige Statistiken basierend auf dem Fahrzeugtyp."""
    stats = {
        "PANZER": {"speed": 60, "armor": 100, "firepower": 90, "range": 50},
        "LKW": {"speed": 80, "armor": 30, "firepower": 10, "range": 80},
        "JEEP": {"speed": 120, "armor": 40, "firepower": 20, "range": 70},
        "FLUGZEUG": {"speed": 100, "armor": 50, "firepower": 85, "range": 100},
        "HUBSCHRAUBER": {"speed": 95, "armor": 40, "firepower": 70, "range": 60},
        "BOOT": {"speed": 50, "armor": 70, "firepower": 80, "range": 90},
        "TRANSPORTER": {"speed": 85, "armor": 60, "firepower": 30, "range": 75}
    }
    
    # Standard-Werte für bekannte Typen, sonst generisch
    base_stats = stats.get(typ, {"speed": 50, "armor": 50, "firepower": 50, "range": 50})
    
    # Leicht variieren für "Realismus"
    import random
    random.seed(name) # Pseudo-random basierend auf Name
    
    return {
        "speed": min(100, max(0, base_stats["speed"] + random.randint(-5, 5))),
        "armor": min(100, max(0, base_stats["armor"] + random.randint(-5, 5))),
        "firepower": min(100, max(0, base_stats["firepower"] + random.randint(-5, 5))),
        "range": min(100, max(0, base_stats["range"] + random.randint(-5, 5))),
    }
