# Build a ~3000-row German word list CSV with richer categories + some helpful columns.
import pandas as pd
from itertools import product

# ---------- Helpers ----------
def article_from_gender(g):
    return {"m":"der","f":"die","n":"das"}.get(g, "")

def df_from_records(records):
    return pd.DataFrame.from_records(records, columns=[
        "wort","kategorie","genus","artikel","plural","englisch","basisform","praeteritum","partizip_ii","hinweis"
    ])

def make_noun(word, gender=None, plural=None, english=None, hint=None):
    return [word, "Substantiv", gender or "", article_from_gender(gender) if gender else "", plural or "", english or "", "", "", "", hint or ""]

def make_name(word, gender):
    cat = "Männername" if gender=="m" else "Frauenname"
    return [word, cat, "", "", "", "", "", "", "", ""]

def make_color(word, english=None):
    return [word, "Farbe", "", "", "", english or "", "", "", "", ""]

def make_adj(word, english=None):
    return [word, "Adjektiv", "", "", "", english or "", "", "", "", ""]

def make_verb(infinitive, english=None, hint=None):
    # naive forms for regular verbs (not perfect; marked in hint)
    stem = infinitive
    praet = ""
    part2 = ""
    ok = False
    # VERY rough detection of regular verbs (ending -en/-eln/-ern) -> simple forms
    if infinitive.endswith("ieren"):
        ok = True
        stem = infinitive[:-5]
        praet = stem + "ierte"
        part2 = stem + "iert"
    elif infinitive.endswith("eln"):
        ok = True
        stem = infinitive[:-3]
        praet = stem + "elte"
        part2 = stem + "elt"
    elif infinitive.endswith("ern"):
        ok = True
        stem = infinitive[:-3]
        praet = stem + "erte"
        part2 = stem + "ert"
    elif infinitive.endswith("en"):
        ok = True
        stem = infinitive[:-2]
        praet = stem + "te"
        part2 = "ge" + stem + "t"
    elif infinitive.endswith("n"):
        ok = True
        stem = infinitive[:-1]
        praet = stem + "te"
        part2 = "ge" + stem + "t"
    note = (hint or "")
    if ok:
        if note:
            note += " | "
        note += "Formen automatisch (vereinfacht) generiert; unregelmäßige Verben evtl. falsch/leer."
    return [infinitive, "Verb", "", "", "", english or "", infinitive, praet, part2, note]

# ---------- Base lists (curated and compact) ----------

# Some common simple nouns with gender & plural (subset; compounds generated below will add many more)
base_nouns = [
    ("Haus","n","Häuser","house"),
    ("Auto","n","Autos","car"),
    ("Stadt","f","Städte","city"),
    ("Dorf","n","Dörfer","village"),
    ("Schule","f","Schulen","school"),
    ("Universität","f","Universitäten","university"),
    ("Garten","m","Gärten","garden"),
    ("Hund","m","Hunde","dog"),
    ("Katze","f","Katzen","cat"),
    ("Vogel","m","Vögel","bird"),
    ("Fisch","m","Fische","fish"),
    ("Kind","n","Kinder","child"),
    ("Mann","m","Männer","man"),
    ("Frau","f","Frauen","woman"),
    ("Lehrer","m","Lehrer","teacher"),
    ("Lehrerin","f","Lehrerinnen","teacher (f)"),
    ("Arzt","m","Ärzte","doctor"),
    ("Ärztin","f","Ärztinnen","doctor (f)"),
    ("Krankenhaus","n","Krankenhäuser","hospital"),
    ("Apotheke","f","Apotheken","pharmacy"),
    ("Laden","m","Läden","shop"),
    ("Supermarkt","m","Supermärkte","supermarket"),
    ("Bäckerei","f","Bäckereien","bakery"),
    ("Bank","f","Banken","bank"),
    ("Geld","n","","money"),
    ("Euro","m","Euro","euro"),
    ("Zug","m","Züge","train"),
    ("Bus","m","Busse","bus"),
    ("Bahn","f","Bahnen","railway"),
    ("Fahrrad","n","Fahrräder","bicycle"),
    ("Flugzeug","n","Flugzeuge","airplane"),
    ("Schiff","n","Schiffe","ship"),
    ("Computer","m","Computer","computer"),
    ("Telefon","n","Telefone","telephone"),
    ("Handy","n","Handys","mobile phone"),
    ("Uhr","f","Uhren","clock"),
    ("Fenster","n","Fenster","window"),
    ("Tür","f","Türen","door"),
    ("Wand","f","Wände","wall"),
    ("Decke","f","Decken","ceiling/blanket"),
    ("Boden","m","Böden","floor/ground"),
    ("Dach","n","Dächer","roof"),
    ("Küche","f","Küchen","kitchen"),
    ("Bad","n","Bäder","bathroom"),
    ("Schlafzimmer","n","Schlafzimmer","bedroom"),
    ("Wohnzimmer","n","Wohnzimmer","living room"),
    ("Büro","n","Büros","office"),
    ("Firma","f","Firmen","company"),
    ("Arbeit","f","Arbeiten","work"),
    ("Chef","m","Chefs","boss"),
    ("Kollege","m","Kollegen","colleague"),
    ("Kollegin","f","Kolleginnen","colleague (f)"),
    ("Urlaub","m","Urlaube","vacation"),
    ("Reise","f","Reisen","trip"),
    ("Hotel","n","Hotels","hotel"),
    ("Zimmer","n","Zimmer","room"),
    ("Bett","n","Betten","bed"),
    ("Lampe","f","Lampen","lamp"),
    ("Licht","n","Lichter","light"),
    ("Strom","m","","electricity"),
    ("Wasser","n","","water"),
    ("Feuer","n","","fire"),
    ("Luft","f","","air"),
    ("Erde","f","","earth/soil"),
    ("Himmel","m","","sky/heaven"),
    ("Sonne","f","Sonnen","sun"),
    ("Mond","m","Monde","moon"),
    ("Stern","m","Sterne","star"),
    ("Wetter","n","","weather"),
    ("Regen","m","","rain"),
    ("Schnee","m","","snow"),
    ("Wind","m","","wind"),
    ("Wolke","f","Wolken","cloud"),
    ("Nebel","m","","fog"),
    ("Sturm","m","Stürme","storm"),
    ("Donner","m","","thunder"),
    ("Blitz","m","Blitze","lightning"),
    ("Frühling","m","Frühlinge","spring"),
    ("Sommer","m","Sommer","summer"),
    ("Herbst","m","Herbste","autumn"),
    ("Winter","m","Winter","winter"),
    ("Woche","f","Wochen","week"),
    ("Monat","m","Monate","month"),
    ("Jahr","n","Jahre","year"),
    ("Tag","m","Tage","day"),
    ("Stunde","f","Stunden","hour"),
    ("Minute","f","Minuten","minute"),
    ("Sekunde","f","Sekunden","second"),
    ("Frühstück","n","Frühstücke","breakfast"),
    ("Mittagessen","n","","lunch"),
    ("Abendessen","n","","dinner"),
    ("Brot","n","Brote","bread"),
    ("Brötchen","n","Brötchen","roll"),
    ("Kuchen","m","Kuchen","cake"),
    ("Kaffee","m","","coffee"),
    ("Tee","m","","tea"),
    ("Bier","n","","beer"),
    ("Wein","m","Weine","wine"),
    ("Saft","m","Säfte","juice"),
    ("Milch","f","","milk"),
    ("Käse","m","","cheese"),
    ("Wurst","f","Würste","sausage"),
    ("Obst","n","","fruit"),
    ("Gemüse","n","","vegetables"),
    ("Apfel","m","Äpfel","apple"),
    ("Birne","f","Birnen","pear"),
    ("Banane","f","Bananen","banana"),
    ("Orange","f","Orangen","orange"),
    ("Zitrone","f","Zitronen","lemon"),
    ("Traube","f","Trauben","grape"),
    ("Tomate","f","Tomaten","tomato"),
    ("Gurke","f","Gurken","cucumber"),
    ("Kartoffel","f","Kartoffeln","potato"),
    ("Karotte","f","Karotten","carrot"),
    ("Salat","m","Salate","salad"),
    ("Reis","m","","rice"),
    ("Nudeln","pl","Nudeln","pasta"),
    ("Suppe","f","Suppen","soup"),
    ("Salz","n","","salt"),
    ("Pfeffer","m","","pepper"),
    ("Zucker","m","","sugar"),
    ("Öl","n","Öle","oil"),
    ("Butter","f","","butter"),
    ("Ei","n","Eier","egg"),
    ("Fleisch","n","","meat"),
]

# Verb list (~300+, a blend; forms will be naive for regulars)
verbs = [
    "sein","haben","werden","können","müssen","sollen","wollen","dürfen","mögen",
    "machen","tun","gehen","kommen","fahren","fliegen","laufen","schwimmen","schlafen",
    "essen","trinken","sprechen","reden","sagen","fragen","antworten","hören","sehen",
    "schauen","lesen","schreiben","lernen","studieren","arbeiten","spielen","kaufen",
    "verkaufen","öffnen","schließen","beginnen","enden","starten","stoppen","sitzen",
    "stehen","liegen","bleiben","bringen","nehmen","geben","bekommen","finden","suchen",
    "treffen","helfen","denken","glauben","wissen","kennen","verstehen","erklären","zeigen",
    "benutzen","brauchen","fühlen","leben","wohnen","reisen","besuchen","bauen","kochen",
    "backen","springen","tanzen","singen","malen","zeichnen","warten","hoffen","lieben",
    "hassen","lachen","weinen","gewinnen","verlieren","bezahlen","sparen","zahlen","schicken",
    "holen","tragen","ziehen","drücken","schneiden","reinigen","putzen","waschen","wiederholen",
    "vorbereiten","entscheiden","vergleichen","entwickeln","programmieren","debuggen","drucken",
    "speichern","laden","installieren","aktualisieren","konfigurieren","kompilieren","testen",
    "deployen","loggen","analysieren","optimieren","verschlüsseln","entschlüsseln","drucken",
    "telefonieren","mailen","fotografieren","filmen","spielen","surfen","wandern","klettern",
    "reiten","joggen","angeln","grillen","backen","braten","kochen","schälen","würzen",
    "mischen","gießen","rühren","probieren","servieren","bestellen","liefern","packen",
    "auspacken","öffnen","schließen","abschicken","empfangen","bestätigen","ablehnen",
    "akzeptieren","verweigern","diskutieren","argumentieren","beweisen","widerlegen",
    "vermuten","schätzen","berechnen","messen","wiegen","zeichnen","konstruieren",
    "entwerfen","planen","organisieren","strukturieren","protokollieren","dokumentieren",
    "formulieren","korrigieren","übersetzen","interpretieren","simulieren","modellieren",
    "kalibrieren","justieren","schrauben","löten","sägen","bohren","hämmern","kleben",
    "trocknen","heizen","kühlen","frieren","schmelzen","verdampfen","destillieren",
    "filtern","sortieren","sammeln","lagern","entsorgen","reparieren","warten",
    "betreiben","überwachen","steuern","regeln","melden","warnen","sichern","retten",
    "pflegen","heilen","diagnostizieren","therapieren","untersuchen","operieren",
    "zeichnen","bemalen","dekorieren","gestalten","designen","codieren","refaktorieren",
    "debuggen","profilen","benchmarken","konfigurieren","deployen","versionieren",
    "committen","pushen","pullen","mergen","releasen","rollouten","skalieren",
    "containerisieren","virtualisieren","scripten","automatisieren","parametrisieren",
    "validieren","verifizieren","authentifizieren","autorisieren","testen","monitoren",
    "observieren","loggen","visualisieren","berichten","präsentieren","moderieren",
    "leiten","führen","managen","coachen","beraten","verhandeln","motivieren","rekrutieren",
    "einstellen","kündigen","bewerten","belohnen","bestrafen","trainieren","üben","lehren",
    "unterrichten","erzählen","beschreiben","erfinden","entdecken","erforschen","publizieren",
    "drucken","verlegen","versenden","empfehlen","reservieren","buchen","zahlen","abrechnen",
    "finanzieren","investieren","versichern","verwalten","vermieten","kaufen","verkaufen",
    "mieten","vermieten","bauen","sanieren","renovieren","modernisieren","isolieren",
    "lackieren","polieren","fräsen","drehen","schleifen","gießen","schweißen","härten",
    "prüfen","abnehmen","abholen","zurückgeben","austauschen","ersetzen","verbinden",
    "trennen","synchronisieren","backupen","wiederherstellen","entpacken","komprimieren",
    "archivieren","verschieben","kopieren","einfügen","löschen","umbenennen","suchen",
    "finden","sortieren","filtern","gruppieren","aggregieren","exportieren","importieren"
]

# Adjectives (base set; we'll expand with "un-" where appropriate later)
adjectives_base = [
    "groß","klein","neu","alt","gut","schlecht","schnell","langsam","früh","spät",
    "hell","dunkel","stark","schwach","klug","dumm","laut","leise","warm","kalt",
    "heiß","kühl","trocken","nass","sauber","schmutzig","teuer","billig","reich","arm",
    "schön","hässlich","freundlich","unfreundlich","nett","gemein","ruhig","nervös","müde","fit",
    "gesund","krank","sicher","gefährlich","einfach","schwierig","leicht","schwer","kurz","lang",
    "breit","schmal","hoch","tief","nah","fern","frei","besetzt","offen","geschlossen",
    "richtig","falsch","wichtig","unwichtig","modern","altmodisch","praktisch","unpraktisch",
    "nützlich","nutzlos","möglich","unmöglich","typisch","untypisch","klar","unklar",
    "saftig","trocken","weich","hart","scharf","mild","bitter","süß","salzig","sauer",
    "freundlich","geduldig","ungeduldig","höflich","unhöflich","spitz","stumpf","glatt","rau",
    "stabil","instabil","flexibel","inflexibel","kreativ","unkreativ","aktiv","passiv",
    "ruhig","hektisch","seriös","locker","fröhlich","traurig","optimistisch","pessimistisch",
    "realistisch","idealistisch","neutral","parteiisch","objektiv","subjektiv","zentral","peripher",
    "häufig","selten","gewöhnlich","ungewöhnlich","einzigartig","vielfältig","einfach","komplex",
    "transparent","opak","stumpf","glänzend","edel","billig","robust","fragil","schmal","massiv",
    "bunt","farblos","lebendig","starr","heikel","locker","streng","locker","sicher","unsicher"
]

# Colors: base + modifiers to expand
base_colors = ["rot","blau","grün","gelb","orange","violett","lila","rosa","pink","schwarz","weiß","grau","braun","beige","türkis","cyan","magenta","gold","silber","bronze"]
color_mods = ["hell","dunkel","pastell","neon","blass","tief"]

# Male & female names (extend beyond the starter)
male_names = [
    "Alexander","Maximilian","Felix","Lukas","Leon","Paul","Jonas","Tim","Noah","Elias","David","Daniel","Jan",
    "Philipp","Niklas","Sebastian","Benjamin","Martin","Thomas","Michael","Andreas","Christian","Peter","Johannes",
    "Oliver","Robert","Stefan","Florian","Patrick","Marcel","Kevin","Dominik","Simon","Julian","Tobias","Marco",
    "Sven","Kai","Finn","Luca","Tom","Matteo","Moritz","Anton","Fabian","Joshua","Kilian","Pascal","René",
    "Ralf","Uwe","Jürgen","Dieter","Karl","Heinz","Frank","Holger","Bernd","Dirk","Volker","Rainer","Georg","Markus",
    "Matthias","Carsten","Björn","Heiko","Gerd","Ludwig","Theo","Timo","Nils","Arne","Malte","Hannes","Henrik",
    "Cornelius","Konstantin","Christoph","Manuel","Otto","Rudolf","Klaus","Hans","Fritz","Albert","Walter","Leo",
    "Oskar","Emil","Ferdinand","Johann","Nikolaus","Aaron","Adrian","Benedikt","Caspar","Damian","Erik","Falk",
    "Gideon","Henry","Ilias","Jakob","Kasper","Linus","Marius","Nathan","Olivier","Quentin","Raphael","Samuel",
    "Thilo","Ulrich","Vincent","Wolfgang","Yannick","Zacharias","Bruno","Hugo","Peer","Peer","Till","Levin",
    "Justus","Magnus","Valentin","Quirin","Severin","Fabio","Leandro","Mika","Jasper","Pepe","Lennard","Keno",
    "Henning","Bastian","Tobias","Gregor","Roman","Nico","Rico","Mirko","Jörn","Torben","Torge","Birk","Gunnar",
    "Sönke","Helge","Enno","Theo","Hendrik","Frederik","Arvid","Jannis","Kjell","Tjark","Ole","Bent","Kalle",
    "Hauke","Klaas","Franz","Konrad","Friedrich","Götz","Gunther","Berthold"
]

female_names = [
    "Anna","Maria","Emilia","Mia","Lea","Lena","Julia","Laura","Sarah","Sophie","Johanna","Clara","Emma","Marie",
    "Lisa","Lina","Hannah","Jana","Nicole","Katharina","Carolin","Caroline","Carina","Christina","Christine",
    "Susanne","Sandra","Anja","Heike","Monika","Petra","Sabine","Nina","Nadine","Daniela","Franziska","Theresa",
    "Marlene","Paula","Luisa","Helena","Maja","Martha","Greta","Isabell","Isabelle","Charlotte","Amelie","Eva",
    "Tina","Ute","Silke","Gabriele","Birgit","Kerstin","Ingrid","Angelika","Renate","Brigitte","Saskia","Tanja",
    "Yvonne","Anita","Sina","Sabrina","Melanie","Martina","Claudia","Katrin","Ilona","Kira","Miriam","Rebecca",
    "Stefanie","Ulrike","Hildegard","Annika","Antonia","Carla","Elisa","Elisabeth","Nora","Ronja","Selina","Verena",
    "Agnes","Lotte","Ida","Frieda","Marlies","Grete","Helene","Adele","Lilly","Ella","Alina","Pia","Mila","Lia",
    "Zoe","Nele","Merle","Mareike","Svea","Fenja","Tabea","Mareen","Britta","Wiebke","Neele","Elena","Mira",
    "Miriam","Mona","Selma","Yara","Ayla","Leyla","Sila","Dilara","Derya","Aylin","Aisha","Sofia","Giulia","Chiara"
]

# Animals (selection; ~200)
animals = [
    "Hund","Katze","Kaninchen","Hamster","Meerschweinchen","Pferd","Kuh","Schaf","Ziege","Schwein",
    "Huhn","Hahn","Gans","Ente","Truthahn","Taube","Spatz","Amsel","Drossel","Rotkehlchen","Fink","Storch","Kranich",
    "Schwan","Möwe","Rabe","Krähe","Adler","Falke","Eule","Uhu","Fledermaus","Fuchs","Wolf","Bär","Dachs","Igel",
    "Marder","Otter","Biber","Hirsch","Reh","Elch","Wildschwein","Hase","Maulwurf","Eichhörnchen","Waschbär",
    "Luchs","Leopard","Gepard","Tiger","Löwe","Panther","Gorilla","Schimpanse","Orang-Utan","Pavian","Panda",
    "Koala","Känguru","Opossum","Wal","Delfin","Tümmler","Hai","Rochen","Qualle","Krake","Tintenfisch","Hering",
    "Dorsch","Kabeljau","Lachs","Forelle","Karpfen","Zander","Hecht","Aal","Barsch","Thunfisch","Makrele","Sardine",
    "Seepferdchen","Seehund","Seelöwe","Walross","Pinguin","Eisbär","Robbe","Kamel","Dromedar","Lama","Alpaka",
    "Pferd","Esel","Maultier","Zebra","Giraffe","Nashorn","Flusspferd","Elefant","Antilope","Gazelle","Büffel",
    "Yak","Bisam","Murmel","Lemming","Wiesel","Hermelin","Iltis","Hyäne","Schakal","Fennek","Dingo","Strauß",
    "Emu","Kiwivogel","Kakadu","Papagei","Ara","Kolibri","Specht","Kuckuck","Kormoran","Pelikan","Seeadler",
    "Geier","Habicht","Milan","Mauersegler","Schwalbe","Schneehuhn","Auerhahn","Birkhuhn","Rebhuhn","Fasan",
    "Perlhuhn","Pfau","Truthahn","Gans","Ente","Huhn","Kobra","Python","Boa","Viper","Eidechse","Gecko","Leguan",
    "Krokodil","Alligator","Schildkröte","Landschildkröte","Meeresschildkröte","Frosch","Kröte","Molch","Salamander",
    "Biene","Wespe","Hornisse","Hummel","Ameise","Termite","Käfer","Marienkäfer","Schmetterling","Mottenfalter",
    "Libelle","Mücke","Stechmücke","Fliege","Bremsen","Heuschrecke","Grille","Zikade","Assel","Spinne","Webspinne",
    "Tarantel","Skorpion","Zecke","Floh","Läuse","Wanze","Krebs","Hummer","Garnele","Krabbe","Seestern","Seeigel"
]

# Professions (~120)
professions = [
    "Arzt","Ärztin","Pfleger","Pflegekraft","Hebamme","Physiotherapeut","Ergotherapeut","Zahnarzt","Zahnärztin",
    "Apotheker","Apothekerin","Ingenieur","Ingenieurin","Architekt","Architektin","Bauarbeiter","Elektriker",
    "Installateur","Schreiner","Tischler","Maler","Lackierer","Mechaniker","Mechatroniker","Kfz-Mechatroniker",
    "Programmierer","Entwickler","Softwarearchitekt","Administrator","Datenbankadministrator","IT-Consultant",
    "Projektmanager","Produktmanager","Designer","Grafiker","Fotograf","Redakteur","Journalist","Autor","Lektor",
    "Lehrer","Lehrerin","Professor","Professorin","Dozent","Dozentin","Forscher","Forscherin","Biologe","Chemiker",
    "Physiker","Mathematiker","Statistiker","Analyst","Berater","Coach","Trainer","Verkäufer","Verkäuferin",
    "Kaufmann","Kauffrau","Bürokaufmann","Bürokauffrau","Steuerberater","Rechtsanwalt","Richter","Notar",
    "Polizist","Polizistin","Feuerwehrmann","Feuerwehrfrau","Soldat","Sanitäter","Pilot","Pilotin","Lokführer",
    "Kapitän","Seemann","Fischer","Bäcker","Konditor","Koch","Köchin","Kellner","Kellnerin","Metzger","Gärtner",
    "Landwirt","Winzer","Florist","Friseur","Friseurin","Kosmetikerin","Einzelhandelskaufmann",
    "Einzelhandelskauffrau","Immobilienmakler","Hausmeister","Reiniger","Hauswirtschaftler","Logistiker",
    "Lagerist","Spediteur","Fahrer","Kurrier","Zugbegleiter","Lokführer","Schaffner","Therapeut","Psychologe",
    "Psychologin","Kriminologe","Sozialarbeiter","Erzieher","Erzieherin"
]

# Foods (~150)
foods = [
    "Apfel","Birne","Banane","Orange","Zitrone","Limette","Grapefruit","Traube","Kirsche","Pfirsich","Nektarine",
    "Aprikose","Pflaume","Zwetschge","Mango","Papaya","Ananas","Kiwi","Melone","Wassermelone","Honigmelone",
    "Erdbeere","Himbeere","Brombeere","Johannisbeere","Heidelbeere","Preiselbeere","Cranberry","Granatapfel",
    "Tomate","Gurke","Paprika","Chili","Aubergine","Zucchini","Kartoffel","Süßkartoffel","Karotte","Sellerie",
    "Pastinake","Petersilie","Schnittlauch","Lauch","Brokkoli","Blumenkohl","Rosenkohl","Kohl","Chinakohl",
    "Grünkohl","Spinat","Salat","Rucola","Feldsalat","Kopfsalat","Mais","Erbse","Bohne","Linsen","Kichererbse",
    "Reis","Nudel","Spätzle","Gnocchi","Brot","Brötchen","Baguette","Croissant","Kuchen","Torte","Keks","Cracker",
    "Schokolade","Praline","Bonbon","Karamell","Honig","Marmelade","Nutella","Butter","Margarine","Öl","Olivenöl",
    "Sonnenblumenöl","Rapsöl","Essig","Balsamico","Sojasauce","Fischsauce","Austernsauce","Worcestersauce",
    "Senf","Mayonnaise","Ketchup","Pesto","Salsa","Guacamole","Hummus","Tahini","Joghurt","Quark","Sahne",
    "Milch","Käse","Mozzarella","Parmesan","Gouda","Emmentaler","Feta","Camembert","Brie","Bergkäse","Räucherlachs",
    "Schinken","Salami","Speck","Wurst","Tofu","Tempeh","Seitan","Ei","Hähnchen","Pute","Rind","Schwein","Lamm",
    "Kalb","Wild","Hackfleisch","Frikadelle","Schnitzel","Bratwurst","Weißwurst","Currywurst","Leberkäse",
    "Sauerkraut","Kartoffelsalat","Nudelsalat","Gulasch","Eintopf","Suppe","Borschtsch","Pho","Ramen","Udon",
    "Soba","Curry","Pizza","Pasta","Lasagne","Spaghetti","Tortellini","Risotto","Paella","Burrito","Taco","Quesadilla",
    "Sushi","Sashimi","Tempura","Dim Sum","Döner","Falafel","Shawarma","Kebab","Burger","Pommes","Sandwich"
]

# Cities (Germany + world; ~220)
cities = [
    # Germany (selection)
    "Berlin","Hamburg","München","Köln","Frankfurt","Stuttgart","Düsseldorf","Dortmund","Essen","Bremen","Dresden",
    "Leipzig","Hannover","Nürnberg","Duisburg","Bochum","Wuppertal","Bielefeld","Bonn","Münster","Karlsruhe",
    "Mannheim","Augsburg","Wiesbaden","Mönchengladbach","Gelsenkirchen","Braunschweig","Kiel","Aachen","Chemnitz",
    "Halle","Magdeburg","Freiburg","Krefeld","Lübeck","Oberhausen","Erfurt","Mainz","Rostock","Kassel","Hagen",
    "Saarbrücken","Hamm","Potsdam","Ludwigshafen","Oldenburg","Leverkusen","Osnabrück","Solingen","Heidelberg",
    "Herne","Neuss","Darmstadt","Paderborn","Regensburg","Ingolstadt","Würzburg","Fürth","Ulm","Heilbronn",
    "Pforzheim","Wolfsburg","Göttingen","Bottrop","Reutlingen","Koblenz","Bremerhaven","Recklinghausen",
    "Bergisch Gladbach","Remscheid","Jena","Trier","Moers","Salzgitter","Siegen","Hildesheim","Cottbus","Gera",
    "Kaiserslautern","Zwickau","Flensburg","Konstanz","Villingen-Schwenningen","Witten","Dessau-Roßlau","Bamberg",
    "Bayreuth","Lüneburg","Tübingen","Landshut","Aschaffenburg","Düren","Ratingen",
    # Europe/world
    "Wien","Zürich","Genf","Basel","Paris","Lyon","Marseille","Toulouse","Bordeaux","Lille","Nantes","Nizza",
    "Rom","Mailand","Neapel","Turin","Bologna","Florenz","Venedig","Madrid","Barcelona","Valencia","Sevilla",
    "Bilbao","Lissabon","Porto","London","Manchester","Birmingham","Liverpool","Edinburgh","Glasgow","Dublin","Cork",
    "Brüssel","Antwerpen","Gent","Rotterdam","Amsterdam","Den Haag","Utrecht","Kopenhagen","Stockholm","Oslo",
    "Helsinki","Reykjavik","Prag","Brno","Bratislava","Budapest","Warschau","Krakau","Danzig","Posen","Breslau",
    "New York","Los Angeles","Chicago","Houston","Phoenix","Philadelphia","San Antonio","San Diego","Dallas","San Jose",
    "Toronto","Vancouver","Montreal","Ottawa","Mexiko-Stadt","Monterrey","Guadalajara","São Paulo","Rio de Janeiro",
    "Brasília","Buenos Aires","Santiago","Lima","Bogotá","Quito","Caracas","Johannesburg","Kapstadt","Nairobi","Kairo",
    "Alexandria","Addis Abeba","Lagos","Accra","Casablanca","Rabat","Tunis","Algier","Istanbul","Ankara","Izmir",
    "Dubai","Abu Dhabi","Doha","Riad","Dschidda","Teheran","Bagdad","Amman","Beirut","Jerusalem","Tel Aviv","Karatschi",
    "Lahore","Islamabad","Delhi","Mumbai","Bengaluru","Chennai","Kalkutta","Dhaka","Bangkok","Kuala Lumpur","Singapur",
    "Jakarta","Manila","Ho-Chi-Minh-Stadt","Hanoi","Hongkong","Shanghai","Peking","Shenzhen","Guangzhou","Taipeh",
    "Tokio","Osaka","Kyoto","Seoul","Busan","Sydney","Melbourne","Auckland","Wellington","Perth","Brisbane"
]

# Prefix compounds: prefixes + suffixes with genders/plurals to generate many plausible nouns
prefixes = [
    "Haus","Auto","Stadt","Schul","Arbeits","Kinder","Wasser","Luft","Feuer","Holz","Metall","Stein",
    "Glas","Papier","Computer","Netz","Daten","Zeit","Tages","Nacht","Abend","Morgen","Reise","Bahn",
    "Zug","Bus","Flug","Fahr","Rad","Handy","Küchen","Wohn","Büro","Garten","Straßen","See","Fluss",
    "Berg","Wald","Insel","Strand","Meer","Wetter","Gesundheits","Kranken","Sport","Kultur","Musik",
    "Film","Foto","Theater","Museum","Polizei","Feuerwehr","Steuer","Zoll","Bank","Versicherungs",
    "Verkehrs","Umwelt","Energie","Klima","Technik","Software","Hardware","Server","Netzwerk","Datenbank"
]

suffixes = [
    {"base":"Tür","gender":"f","plural":"Türen"},
    {"base":"Dach","gender":"n","plural":"Dächer"},
    {"base":"Wand","gender":"f","plural":"Wände"},
    {"base":"Fenster","gender":"n","plural":"Fenster"},
    {"base":"Boden","gender":"m","plural":"Böden"},
    {"base":"Plan","gender":"m","plural":"Pläne"},
    {"base":"Liste","gender":"f","plural":"Listen"},
    {"base":"Buch","gender":"n","plural":"Bücher"},
    {"base":"Seite","gender":"f","plural":"Seiten"},
    {"base":"Nummer","gender":"f","plural":"Nummern"},
    {"base":"Fehler","gender":"m","plural":"Fehler"},
    {"base":"Server","gender":"m","plural":"Server"},
    {"base":"Client","gender":"m","plural":"Clients"},
    {"base":"Vertrag","gender":"m","plural":"Verträge"},
    {"base":"Gesetz","gender":"n","plural":"Gesetze"},
    {"base":"Prüfung","gender":"f","plural":"Prüfungen"},
    {"base":"Reise","gender":"f","plural":"Reisen"},
    {"base":"Hafen","gender":"m","plural":"Häfen"},
    {"base":"Bahnhof","gender":"m","plural":"Bahnhöfe"},
    {"base":"Flughafen","gender":"m","plural":"Flughäfen"},
    {"base":"Karte","gender":"f","plural":"Karten"},
    {"base":"Preis","gender":"m","plural":"Preise"},
    {"base":"Park","gender":"m","plural":"Parks"},
    {"base":"Platz","gender":"m","plural":"Plätze"},
    {"base":"Straße","gender":"f","plural":"Straßen"},
    {"base":"Brücke","gender":"f","plural":"Brücken"},
    {"base":"Tunnel","gender":"m","plural":"Tunnel"},
    {"base":"Zentrum","gender":"n","plural":"Zentren"},
    {"base":"Haus","gender":"n","plural":"Häuser"},
    {"base":"Werk","gender":"n","plural":"Werke"},
    {"base":"Ticket","gender":"n","plural":"Tickets"},
    {"base":"Station","gender":"f","plural":"Stationen"},
    {"base":"Leitung","gender":"f","plural":"Leitungen"},
    {"base":"Leiter","gender":"m","plural":"Leiter"},
    {"base":"Leuchte","gender":"f","plural":"Leuchten"},
    {"base":"Schalter","gender":"m","plural":"Schalter"},
    {"base":"Sensor","gender":"m","plural":"Sensoren"},
    {"base":"Aktuator","gender":"m","plural":"Aktuatoren"},
]

# ---------- Build dataset ----------
records = []

# Simple nouns
for w,g,pl,en in base_nouns:
    records.append(make_noun(w, g, pl, en))

# Compound nouns (limit to ~1600 to keep total around 3000)
compound_count = 0
for pre in prefixes:
    for suf in suffixes:
        word = pre + suf["base"]
        plural = pre + suf["plural"] if suf["plural"] else ""
        gender = suf["gender"]
        hint = "Zusammensetzung aus '{}' + '{}'".format(pre, suf["base"])
        records.append([word, "Substantiv", gender, article_from_gender(gender), plural, "", "", "", "", hint])
        compound_count += 1
        if compound_count >= 1600:
            break
    if compound_count >= 1600:
        break

# Verbs
for v in verbs:
    records.append(make_verb(v))

# Colors (base + modifiers)
color_set = set()
for c in base_colors:
    color_set.add(c)
for mod in color_mods:
    for c in base_colors:
        color_set.add(mod + c)
for c in sorted(color_set):
    records.append(make_color(c))

# Adjectives: base + 'un-' prefixed (avoid duplicates)
adj_set = set(adjectives_base)
for a in adjectives_base:
    if not a.startswith("un") and len(a) > 3:
        adj_set.add("un" + a)
for a in sorted(adj_set):
    records.append(make_adj(a))

# Names
for n in male_names:
    records.append(make_name(n, "m"))
for n in female_names:
    records.append(make_name(n, "f"))

# Animals (as nouns; add gender guess empty)
for a in animals:
    records.append(make_noun(a))

# Professions (as nouns)
for p in professions:
    # gender heuristic if endswith -in -> feminine
    g = "f" if p.endswith("in") and not p.endswith("erin") else ""
    records.append(make_noun(p, g))

# Foods (as nouns)
for f in foods:
    records.append(make_noun(f))

# Cities (proper nouns; category Stadt)
for c in cities:
    records.append([c, "Stadt", "", "", "", "", "", "", "", ""])

# Assemble DataFrame
df = df_from_records(records)

# Deduplicate by (wort,kategorie)
df = df.drop_duplicates(subset=["wort","kategorie"]).reset_index(drop=True)

# Provide a quick category count
counts = df["kategorie"].value_counts().sort_index()

# Save CSV
path = "/mnt/data/de_woerterbuch_rund3000.csv"
df.to_csv(path, index=False, encoding="utf-8")

import caas_jupyter_tools
caas_jupyter_tools.display_dataframe_to_user("Deutsches Wörterbuch (~3000 Einträge)", df.head(50))

len_df = len(df)
len_df, counts.to_dict(), path
