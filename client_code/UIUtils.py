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
