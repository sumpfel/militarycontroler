import anvil.server
import sqlite3
import os
import random
from datetime import date, timedelta
DB_PATH = "/tmp/military_base.db"
def get_db():
    if not os.path.exists(DB_PATH):
        init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
def query(sql, params=(), one=False):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    if one:
        return dict(rows[0]) if rows else None
    return [dict(r) for r in rows]
@anvil.server.callable
def get_all_base_locations():
    return query("SELECT basis_id, name, latitude, longitude FROM militaerbasis")
@anvil.server.callable
def get_dashboard_stats():
    conn = get_db()
    cur = conn.cursor()
    stats = {}
    for table in ["militaerbasis", "person", "fahrzeug", "gegenstand", "lager", "einheit"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cur.fetchone()[0]
    cur.execute("SELECT status, COUNT(*) as cnt FROM person GROUP BY status ORDER BY cnt DESC")
    stats["person_status"] = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT status, COUNT(*) as cnt FROM fahrzeug GROUP BY status ORDER BY cnt DESC")
    stats["fahrzeug_status"] = [dict(r) for r in cur.fetchall()]
    conn.close()
    return stats
@anvil.server.callable
def get_base_overview():
    return query("""
        SELECT mb.basis_id, mb.name, mb.standort_name, mb.sicherheitsstufe, mb.status,
               mb.kapazitaet, mb.latitude, mb.longitude,
               p_cmd.vorname || ' ' || p_cmd.nachname AS kommandant_name,
               r.bezeichnung AS kommandant_rang,
               (SELECT COUNT(*) FROM person WHERE basis_id = mb.basis_id) AS anzahl_personal,
               (SELECT COUNT(*) FROM fahrzeug WHERE basis_id = mb.basis_id) AS anzahl_fahrzeuge,
               (SELECT COUNT(*) FROM lager WHERE basis_id = mb.basis_id) AS anzahl_lager,
               (SELECT COUNT(*) FROM einheit WHERE basis_id = mb.basis_id) AS anzahl_einheiten
        FROM militaerbasis mb
        LEFT JOIN person p_cmd ON mb.kommandant_id = p_cmd.person_id
        LEFT JOIN rang r ON p_cmd.rang_id = r.rang_id
        ORDER BY mb.name
    """)
@anvil.server.callable
def get_persons(basis_id=None, search_query=None, rang_id=None, beruf=None):
    sql = """
        SELECT p.person_id, p.vorname, p.nachname, p.geburtsdatum, p.geschlecht,
               p.beruf_funktion, p.sicherheitsfreigabe, p.status,
               r.bezeichnung AS rang, r.hierarchie_stufe,
               mb.name AS basis_name,
               e.name AS einheit_name
        FROM person p
        JOIN rang r ON p.rang_id = r.rang_id
        JOIN militaerbasis mb ON p.basis_id = mb.basis_id
        LEFT JOIN einheit e ON p.einheit_id = e.einheit_id
    """
    conditions = []
    params = []
    if basis_id:
        conditions.append("p.basis_id = ?")
        params.append(basis_id)
    if rang_id:
        conditions.append("p.rang_id = ?")
        params.append(rang_id)
    if beruf:
        conditions.append("p.beruf_funktion = ?")
        params.append(beruf)
    if search_query:
        conditions.append("(p.vorname LIKE ? OR p.nachname LIKE ? OR p.beruf_funktion LIKE ?)")
        q = f"%{search_query}%"
        params.extend([q, q, q])
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY r.hierarchie_stufe DESC, p.nachname"
    return query(sql, params)
@anvil.server.callable
def get_base_details(basis_id):
    return query("""
        SELECT mb.*,
               p_cmd.vorname || ' ' || p_cmd.nachname AS kommandant_name,
               r.bezeichnung AS kommandant_rang
        FROM militaerbasis mb
        LEFT JOIN person p_cmd ON mb.kommandant_id = p_cmd.person_id
        LEFT JOIN rang r ON p_cmd.rang_id = r.rang_id
        WHERE mb.basis_id = ?
    """, (basis_id,), one=True)
@anvil.server.callable
def get_base_details_extended(basis_id):
    base = get_base_details(basis_id)
    if not base:
        return None
    vehicle_stats = query("""
        SELECT typ, COUNT(*) as cnt 
        FROM fahrzeug 
        WHERE basis_id = ? 
        GROUP BY typ
    """, (basis_id,))
    personnel_stats = query("""
        SELECT status, COUNT(*) as cnt 
        FROM person 
        WHERE basis_id = ? 
        GROUP BY status
    """, (basis_id,))
    warehouse_stats = query("""
        SELECT l.bezeichnung, 
               (SELECT SUM(menge) FROM gegenstand WHERE lager_id = l.lager_id) as belegung,
               l.kapazitaet
        FROM lager l
        WHERE l.basis_id = ?
    """, (basis_id,))
    return {
        "base": base,
        "vehicles": vehicle_stats,
        "personnel": personnel_stats,
        "warehouses": warehouse_stats
    }
@anvil.server.callable
def get_person_details(person_id):
    return query("""
        SELECT p.*, r.bezeichnung AS rang, r.hierarchie_stufe,
               mb.name AS basis_name, e.name AS einheit_name
        FROM person p
        JOIN rang r ON p.rang_id = r.rang_id
        JOIN militaerbasis mb ON p.basis_id = mb.basis_id
        LEFT JOIN einheit e ON p.einheit_id = e.einheit_id
        WHERE p.person_id = ?
    """, (person_id,), one=True)
@anvil.server.callable
def get_person_assignments(person_id):
    vehicles = query("""
        SELECT f.*, pf.zugewiesen_am 
        FROM fahrzeug f
        JOIN person_fahrzeug pf ON f.fahrzeug_id = pf.fahrzeug_id
        WHERE pf.person_id = ?
    """, (person_id,))
    items = query("""
        SELECT g.*, pg.menge as zugewiesene_menge, pg.zugewiesen_am 
        FROM gegenstand g
        JOIN person_gegenstand pg ON g.gegenstand_id = pg.gegenstand_id
        WHERE pg.person_id = ?
    """, (person_id,))
    return {"vehicles": vehicles, "items": items}
@anvil.server.callable
def get_personnel_stats(basis_id=None):
    base_filter = "WHERE basis_id = ?" if basis_id else ""
    params = (basis_id,) if basis_id else ()
    professions = query(f"""
        SELECT beruf_funktion, COUNT(*) as cnt 
        FROM person 
        {base_filter}
        GROUP BY beruf_funktion 
        ORDER BY cnt DESC
    """, params)
    ranks = query(f"""
        SELECT r.bezeichnung, COUNT(*) as cnt 
        FROM person p
        JOIN rang r ON p.rang_id = r.rang_id
        {base_filter.replace('basis_id', 'p.basis_id')}
        GROUP BY r.bezeichnung 
        ORDER BY r.hierarchie_stufe DESC
    """, params)
    return {"professions": professions, "ranks": ranks}
@anvil.server.callable
def get_professions_dropdown():
    return [r['beruf_funktion'] for r in query("SELECT DISTINCT beruf_funktion FROM person ORDER BY beruf_funktion")]
@anvil.server.callable
def get_ranks_dropdown():
    return query("SELECT rang_id, bezeichnung FROM rang ORDER BY hierarchie_stufe DESC")
@anvil.server.callable
def get_vehicles(basis_id=None, typ=None):
    sql = """
        SELECT f.fahrzeug_id, f.typ, f.name, f.kennzeichen, f.status,
               mb.name AS basis_name
        FROM fahrzeug f
        JOIN militaerbasis mb ON f.basis_id = mb.basis_id
    """
    conditions = []
    params = []
    if basis_id:
        conditions.append("f.basis_id = ?")
        params.append(basis_id)
    if typ:
        conditions.append("f.typ = ?")
        params.append(typ)
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY f.typ, f.name"
    return query(sql, params)
@anvil.server.callable
def get_vehicle_types():
    return query("SELECT DISTINCT typ FROM fahrzeug ORDER BY typ")
@anvil.server.callable
def get_warehouses(basis_id=None):
    sql = """
        SELECT l.lager_id, l.bezeichnung, l.typ, l.kapazitaet,
               mb.name AS basis_name, mb.basis_id,
               (SELECT COUNT(*) FROM gegenstand WHERE lager_id = l.lager_id) AS anzahl_items,
               (SELECT COALESCE(SUM(menge), 0) FROM gegenstand WHERE lager_id = l.lager_id) AS gesamt_menge
        FROM lager l
        JOIN militaerbasis mb ON l.basis_id = mb.basis_id
    """
    params = []
    if basis_id:
        sql += " WHERE l.basis_id = ?"
        params.append(basis_id)
    sql += " ORDER BY mb.name, l.typ, l.bezeichnung"
    return query(sql, params)
@anvil.server.callable
def get_warehouse_items(lager_id):
    return query("""
        SELECT g.gegenstand_id, g.name, g.kategorie, g.kaliber,
               g.seriennummer, g.menge, g.status
        FROM gegenstand g
        WHERE g.lager_id = ?
        ORDER BY g.kategorie, g.name
    """, (lager_id,))
@anvil.server.callable
def get_items(basis_id=None, kategorie=None):
    sql = """
        SELECT g.gegenstand_id, g.name, g.kategorie, g.kaliber,
               g.seriennummer, g.menge, g.status,
               l.bezeichnung AS lager_name, l.typ AS lager_typ,
               mb.name AS basis_name
        FROM gegenstand g
        JOIN lager l ON g.lager_id = l.lager_id
        JOIN militaerbasis mb ON l.basis_id = mb.basis_id
    """
    conditions = []
    params = []
    if basis_id:
        conditions.append("l.basis_id = ?")
        params.append(basis_id)
    if kategorie:
        conditions.append("g.kategorie = ?")
        params.append(kategorie)
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY g.kategorie, g.name"
    return query(sql, params)
@anvil.server.callable
def get_weapon_ammo_match(basis_id=None):
    sql = """
        SELECT w.name AS waffe_name, w.kaliber, w.menge AS waffe_menge,
               m.name AS munition_name, m.menge AS munition_menge, m.status AS munition_status,
               lw.bezeichnung AS waffe_lager, lm.bezeichnung AS munition_lager,
               mb_w.name AS basis_name
        FROM gegenstand w
        JOIN lager lw ON w.lager_id = lw.lager_id
        JOIN militaerbasis mb_w ON lw.basis_id = mb_w.basis_id
        JOIN gegenstand m ON w.kaliber = m.kaliber AND m.kategorie = 'MUNITION'
        JOIN lager lm ON m.lager_id = lm.lager_id
        WHERE w.kategorie = 'WAFFE' AND w.kaliber IS NOT NULL
    """
    params = []
    if basis_id:
        sql += " AND lw.basis_id = ?"
        params.append(basis_id)
    sql += " ORDER BY w.kaliber, w.name, m.name"
    return query(sql, params)
@anvil.server.callable
def get_units(basis_id=None):
    sql = """
        SELECT e.einheit_id, e.name, e.typ, 
               mb.name AS basis_name,
               (SELECT COUNT(*) FROM person WHERE einheit_id = e.einheit_id) AS personalstaerke
        FROM einheit e
        JOIN militaerbasis mb ON e.basis_id = mb.basis_id
    """
    params = []
    if basis_id:
        sql += " WHERE e.basis_id = ?"
        params.append(basis_id)
    sql += " ORDER BY mb.name, e.name"
    return query(sql, params)
@anvil.server.callable
def get_bases_dropdown():
    return query("SELECT basis_id, name FROM militaerbasis ORDER BY name")
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS rang (
        rang_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bezeichnung TEXT NOT NULL UNIQUE,
        hierarchie_stufe INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS militaerbasis (
        basis_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, standort_name TEXT NOT NULL,
        latitude REAL NOT NULL, longitude REAL NOT NULL,
        infrastruktur TEXT, flaeche REAL,
        sicherheitsstufe TEXT NOT NULL, status TEXT NOT NULL,
        wasser_vorrat REAL DEFAULT 0, treibstoff_vorrat REAL DEFAULT 0,
        energie_vorrat REAL DEFAULT 0, kapazitaet INTEGER NOT NULL,
        kommandant_id INTEGER,
        FOREIGN KEY (kommandant_id) REFERENCES person(person_id)
    );
    CREATE TABLE IF NOT EXISTS einheit (
        einheit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, typ TEXT NOT NULL,
        basis_id INTEGER NOT NULL,
        FOREIGN KEY (basis_id) REFERENCES militaerbasis(basis_id)
    );
    CREATE TABLE IF NOT EXISTS person (
        person_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vorname TEXT NOT NULL, nachname TEXT NOT NULL,
        geburtsdatum TEXT NOT NULL, geschlecht TEXT NOT NULL,
        beruf_funktion TEXT NOT NULL, sicherheitsfreigabe TEXT NOT NULL,
        status TEXT NOT NULL, basis_id INTEGER NOT NULL,
        rang_id INTEGER NOT NULL, einheit_id INTEGER,
        FOREIGN KEY (basis_id) REFERENCES militaerbasis(basis_id),
        FOREIGN KEY (rang_id) REFERENCES rang(rang_id),
        FOREIGN KEY (einheit_id) REFERENCES einheit(einheit_id)
    );
    CREATE TABLE IF NOT EXISTS lager (
        lager_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bezeichnung TEXT NOT NULL, typ TEXT NOT NULL,
        kapazitaet REAL NOT NULL, basis_id INTEGER NOT NULL,
        FOREIGN KEY (basis_id) REFERENCES militaerbasis(basis_id)
    );
    CREATE TABLE IF NOT EXISTS gegenstand (
        gegenstand_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, kategorie TEXT NOT NULL,
        kaliber TEXT, seriennummer TEXT UNIQUE,
        menge INTEGER NOT NULL DEFAULT 1, status TEXT NOT NULL,
        lager_id INTEGER NOT NULL,
        FOREIGN KEY (lager_id) REFERENCES lager(lager_id)
    );
    CREATE TABLE IF NOT EXISTS fahrzeug (
        fahrzeug_id INTEGER PRIMARY KEY AUTOINCREMENT,
        typ TEXT NOT NULL, name TEXT NOT NULL,
        kennzeichen TEXT UNIQUE, status TEXT NOT NULL,
        basis_id INTEGER NOT NULL,
        FOREIGN KEY (basis_id) REFERENCES militaerbasis(basis_id)
    );
    """)
    raenge = [
        ("Schütze",1),("Gefreiter",2),("Obergefreiter",3),("Hauptgefreiter",4),
        ("Stabsgefreiter",5),("Oberstabsgefreiter",6),("Unteroffizier",7),
        ("Stabsunteroffizier",8),("Feldwebel",9),("Oberfeldwebel",10),
        ("Hauptfeldwebel",11),("Stabsfeldwebel",12),("Oberstabsfeldwebel",13),
        ("Leutnant",14),("Oberleutnant",15),("Hauptmann",16),("Major",17),
        ("Oberstleutnant",18),("Oberst",19),("Brigadegeneral",20),
        ("Generalmajor",21),("Generalleutnant",22),("General",23),
    ]
    cur.executemany("INSERT OR IGNORE INTO rang (bezeichnung, hierarchie_stufe) VALUES (?, ?)", raenge)
    basen = [
        ("Fliegerhorst Büchel","Büchel, Rheinland-Pfalz",50.1736,7.0633,"Flugplatz, Bunker",250.0,"STRENG GEHEIM","AKTIV",50000,80000,15000,2500),
        ("Augustdorf Kaserne","Augustdorf, NRW",51.9081,8.7286,"Kasernen, Übungsplatz",180.0,"GEHEIM","AKTIV",35000,60000,12000,3000),
        ("Marinestützpunkt Wilhelmshaven","Wilhelmshaven",53.5151,8.1044,"Hafen, Docks",320.0,"GEHEIM","AKTIV",80000,120000,20000,4000),
        ("Gebirgsjägerkaserne Mittenwald","Mittenwald, Bayern",47.4425,11.2636,"Gebirgsausbildung",150.0,"VERTRAULICH","AKTIV",25000,40000,8000,1500),
        ("Flugabwehr-Kaserne Husum","Husum, SH",54.4716,9.0519,"Raketenlager, Radar",200.0,"STRENG GEHEIM","AKTIV",30000,55000,10000,1800),
    ]
    for b in basen:
        cur.execute("INSERT INTO militaerbasis (name,standort_name,latitude,longitude,infrastruktur,flaeche,sicherheitsstufe,status,wasser_vorrat,treibstoff_vorrat,energie_vorrat,kapazitaet) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", b)
    einheiten_t = [("1. Kompanie","Infanterie"),("2. Kompanie","Infanterie"),("3. Kompanie","Infanterie"),
                   ("Aufklärungszug","Aufklärung"),("Versorgungszug","Logistik"),("Sanitätszug","Sanitäter"),
                   ("Pionierkompanie","Pioniere"),("Fernmeldezug","Fernmelder"),("Stabskompanie","Stab"),
                   ("Instandsetzung","Instandsetzung"),("Sicherungszug","Sicherung"),("Panzerzug","Panzergrenadiere")]
    einheit_map = {}
    for bid in range(1, 6):
        einheit_map[bid] = []
        for n, t in random.sample(einheiten_t, random.randint(5, 8)):
            cur.execute("INSERT INTO einheit (name, typ, basis_id) VALUES (?,?,?)", (n, t, bid))
            einheit_map[bid].append(cur.lastrowid)
    vn_m = ["Alexander","Benjamin","Christian","Daniel","Erik","Felix","Georg","Hans","Jan","Klaus",
            "Lars","Markus","Niklas","Oliver","Patrick","Robert","Stefan","Thomas","Uwe","Viktor",
            "Wolfgang","Florian","Maximilian","Tobias","Sebastian","Andreas","Matthias","Jürgen",
            "Lukas","Leon","Paul","Jonas","Tim","Moritz","Philipp","David","Simon","Dominik","Marcel"]
    vn_w = ["Anna","Birgit","Christine","Diana","Eva","Franziska","Greta","Hannah","Ingrid","Julia",
            "Katharina","Laura","Maria","Nina","Petra","Sandra","Tanja","Vera","Lisa","Sophie","Lena","Emma"]
    nn = ["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Schulz","Hoffmann",
          "Schäfer","Koch","Bauer","Richter","Klein","Wolf","Schröder","Neumann","Schwarz","Zimmermann",
          "Braun","Krüger","Hofmann","Hartmann","Lange","Schmitt","Werner","Krause","Meier","Lehmann",
          "Berger","Vogel","Friedrich","Jung","Scholz","Engel","Hahn","Keller","Roth","Frank","Ludwig"]
    berufe = ["Soldat","Soldat","Soldat","Soldat","Koch","Mechaniker","Logistik","Sanitäter",
              "Fernmelder","Pilot","Fahrer","Waffenmechaniker","IT-Spezialist","Ausbilder","Aufklärer"]
    for bid in range(1, 6):
        for _ in range(random.randint(150, 250)):
            g = random.choices(["M","W"], weights=[80,20])[0]
            vn = random.choice(vn_m if g == "M" else vn_w)
            nach = random.choice(nn)
            geb = (date(1965,1,1) + timedelta(days=random.randint(0, 12775))).isoformat()
            beruf = random.choice(berufe)
            freig = random.choice(["KEINE","VERTRAULICH","GEHEIM","STRENG GEHEIM"])
            status = random.choices(["AKTIV","KRANK","URLAUB","SUSPENDIERT"], weights=[75,10,10,5])[0]
            rang = min(random.choices(range(1,24), weights=[20,18,16,14,12,10,9,8,7,6,5,4,3,3,3,2,2,1,1,1,1,1,1])[0], 23)
            eid = random.choice(einheit_map[bid]) if random.random() < 0.85 else None
            cur.execute("INSERT INTO person (vorname,nachname,geburtsdatum,geschlecht,beruf_funktion,sicherheitsfreigabe,status,basis_id,rang_id,einheit_id) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (vn, nach, geb, g, beruf, freig, status, bid, rang, eid))
    for bid in range(1, 6):
        cur.execute("SELECT p.person_id FROM person p JOIN rang r ON p.rang_id=r.rang_id WHERE p.basis_id=? AND p.status='AKTIV' ORDER BY r.hierarchie_stufe DESC LIMIT 1", (bid,))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE militaerbasis SET kommandant_id=? WHERE basis_id=?", (row[0], bid))
    lager_t = [("Waffenkammer Alpha","WAFFENLAGER",500),("Waffenkammer Bravo","WAFFENLAGER",300),
               ("Munitionsbunker 1","MUNITIONSLAGER",1000),("Munitionsbunker 2","MUNITIONSLAGER",800),
               ("Ausrüstungsdepot A","AUSRUESTUNG",800),("Ausrüstungsdepot B","AUSRUESTUNG",600),
               ("Lebensmittellager","LEBENSMITTEL",600),("Treibstofflager","TREIBSTOFF",2000),
               ("Allgemeines Depot","ALLGEMEIN",400),("Sanitätslager","AUSRUESTUNG",200)]
    lager_map = {}
    for bid in range(1, 6):
        lager_map[bid] = []
        for n, t, k in random.sample(lager_t, random.randint(6, 9)):
            cur.execute("INSERT INTO lager (bezeichnung,typ,kapazitaet,basis_id) VALUES (?,?,?,?)", (n, t, k, bid))
            lager_map[bid].append((cur.lastrowid, t))
    waffen = [("HK G36","WAFFE","5.56x45mm NATO"),("HK G36K","WAFFE","5.56x45mm NATO"),
              ("HK MP7","WAFFE","4.6x30mm HK"),("HK MG5","WAFFE","7.62x51mm NATO"),
              ("HK P8","WAFFE","9x19mm Parabellum"),("MG3","WAFFE","7.62x51mm NATO"),
              ("HK G28","WAFFE","7.62x51mm NATO"),("Panzerfaust 3","WAFFE","110mm Rakete"),
              ("Carl Gustav M3","WAFFE","84mm Rakete"),("HK GMG","WAFFE","40mm Granate"),
              ("Browning M2","WAFFE","12.7x99mm NATO"),("MP5","WAFFE","9x19mm Parabellum")]
    munition = [("5.56x45mm Patrone","MUNITION","5.56x45mm NATO"),("5.56x45mm Leuchtspur","MUNITION","5.56x45mm NATO"),
                ("7.62x51mm Patrone","MUNITION","7.62x51mm NATO"),("7.62x51mm Panzerbrechend","MUNITION","7.62x51mm NATO"),
                ("9x19mm Patrone","MUNITION","9x19mm Parabellum"),("4.6x30mm Patrone","MUNITION","4.6x30mm HK"),
                ("40mm Granate","MUNITION","40mm Granate"),("84mm Rakete HEAT","MUNITION","84mm Rakete"),
                ("110mm Rakete","MUNITION","110mm Rakete"),("12.7x99mm Patrone","MUNITION","12.7x99mm NATO")]
    ausr = [("Schutzweste SK4","AUSRUESTUNG"),("Gefechtshelm","AUSRUESTUNG"),("Nachtsichtgerät","ELEKTRONIK"),
            ("Funkgerät SEM 52","ELEKTRONIK"),("GPS-Empfänger","ELEKTRONIK"),("Erste-Hilfe-Set","MEDIZIN"),
            ("Sanitätsrucksack","MEDIZIN"),("Fernglas","AUSRUESTUNG"),("Tarnanzug Flecktarn","AUSRUESTUNG"),
            ("Kampfstiefel","AUSRUESTUNG"),("Feldration EPA","VERPFLEGUNG"),("Schlafsack","AUSRUESTUNG")]
    sn_counter = [100000]
    def next_sn():
        sn_counter[0] += 1
        return f"BW-{sn_counter[0]}"
    for bid in range(1, 6):
        wl = [l for l in lager_map[bid] if l[1] == "WAFFENLAGER"]
        ml = [l for l in lager_map[bid] if l[1] == "MUNITIONSLAGER"]
        al = [l for l in lager_map[bid] if l[1] in ("AUSRUESTUNG","ALLGEMEIN")]
        if wl:
            for n, k, kal in random.choices(waffen, k=random.randint(20, 30)):
                cur.execute("INSERT INTO gegenstand (name,kategorie,kaliber,seriennummer,menge,status,lager_id) VALUES (?,?,?,?,?,?,?)",
                            (n, k, kal, next_sn(), random.randint(1,15), random.choice(["VERFUEGBAR","AUSGEGEBEN","DEFEKT"]), random.choice(wl)[0]))
        if ml:
            for n, k, kal in random.choices(munition, k=random.randint(20, 30)):
                cur.execute("INSERT INTO gegenstand (name,kategorie,kaliber,seriennummer,menge,status,lager_id) VALUES (?,?,?,?,?,?,?)",
                            (n, k, kal, None, random.randint(50,5000), "VERFUEGBAR", random.choice(ml)[0]))
        if al:
            for n, k in random.choices(ausr, k=random.randint(20, 35)):
                cur.execute("INSERT INTO gegenstand (name,kategorie,kaliber,seriennummer,menge,status,lager_id) VALUES (?,?,?,?,?,?,?)",
                            (n, k, None, next_sn(), random.randint(1,50), random.choice(["VERFUEGBAR","AUSGEGEBEN","DEFEKT"]), random.choice(al)[0]))
    fz = [("PANZER","Leopard 2A7"),("PANZER","Puma IFV"),("PANZER","Marder 1A5"),("PANZER","Boxer GTK"),
          ("LKW","MAN KAT1"),("LKW","Mercedes Zetros"),("LKW","Unimog U5000"),
          ("JEEP","Mercedes G-Klasse"),("JEEP","Eagle V"),("JEEP","Dingo 2"),
          ("FLUGZEUG","Eurofighter Typhoon"),("FLUGZEUG","Airbus A400M"),("FLUGZEUG","Tornado IDS"),
          ("HUBSCHRAUBER","NH90"),("HUBSCHRAUBER","Tiger UHT"),("HUBSCHRAUBER","CH-53G"),
          ("BOOT","Fregatte F125"),("TRANSPORTER","Fuchs TPz"),("TRANSPORTER","GTK Boxer")]
    plates = set()
    for bid in range(1, 6):
        for t, n in random.choices(fz, k=random.randint(30, 50)):
            p = f"Y-{random.randint(100,9999)}-{random.randint(100,999)}"
            while p in plates:
                p = f"Y-{random.randint(100,9999)}-{random.randint(100,999)}"
            plates.add(p)
            cur.execute("INSERT INTO fahrzeug (typ,name,kennzeichen,status,basis_id) VALUES (?,?,?,?,?)",
                        (t, n, p, random.choices(["EINSATZBEREIT","WARTUNG","DEFEKT"], weights=[70,20,10])[0], bid))
    cur.execute("""
    CREATE TABLE IF NOT EXISTS person_gegenstand (
        person_id INTEGER NOT NULL,
        gegenstand_id INTEGER NOT NULL,
        menge INTEGER NOT NULL DEFAULT 1,
        zugewiesen_am TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (person_id, gegenstand_id),
        FOREIGN KEY (person_id) REFERENCES person(person_id),
        FOREIGN KEY (gegenstand_id) REFERENCES gegenstand(gegenstand_id)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS person_fahrzeug (
        person_id INTEGER NOT NULL,
        fahrzeug_id INTEGER NOT NULL,
        zugewiesen_am TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (person_id, fahrzeug_id),
        FOREIGN KEY (person_id) REFERENCES person(person_id),
        FOREIGN KEY (fahrzeug_id) REFERENCES fahrzeug(fahrzeug_id)
    );
    """)
    conn.commit()
    conn.close()
    print("DB initialisiert mit Testdaten.")
