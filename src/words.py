# Create a starter German word list CSV with categories.
import pandas as pd

# Helper to make a DataFrame from a list
def make_df(words, category):
    return pd.DataFrame({"word": words, "category": category})

# Nouns (common, mixed topics)
nouns = [
    "Haus","Auto","Baum","Tisch","Stuhl","Buch","Schule","Universität","Stadt","Dorf","Straße","Weg",
    "Garten","Blume","Hund","Katze","Vogel","Fisch","Kind","Mann","Frau","Freund","Freundin","Lehrer",
    "Schülerin","Schüler","Arzt","Krankenhaus","Apotheke","Markt","Laden","Geschäft","Supermarkt","Bäckerei",
    "Metzgerei","Bank","Geld","Euro","Zug","Bus","Bahn","Fahrrad","Flugzeug","Schiff","Computer","Handy",
    "Telefon","Uhr","Tür","Fenster","Wand","Decke","Boden","Dach","Küche","Bad","Schlafzimmer","Wohnzimmer",
    "Büro","Firma","Arbeit","Job","Chef","Kollege","Kollegin","Urlaub","Reise","Hotel","Zimmer","Bett",
    "Lampe","Licht","Strom","Wasser","Feuer","Luft","Erde","Himmel","Sonne","Mond","Stern","Wetter",
    "Regen","Schnee","Wind","Wolke","Nebel","Sturm","Donner","Blitz","Frühling","Sommer","Herbst","Winter",
    "Woche","Monat","Jahr","Tag","Stunde","Minute","Sekunde","Morgen","Abend","Nacht","Mittag","Frühstück",
    "Mittagessen","Abendessen","Essen","Getränk","Brot","Brötchen","Kuchen","Kaffee","Tee","Bier","Wein",
    "Saft","Milch","Käse","Wurst","Obst","Gemüse","Apfel","Birne","Banane","Orange","Zitrone","Traube",
    "Tomate","Gurke","Kartoffel","Karotte","Salat","Reis","Nudeln","Suppe","Salz","Pfeffer","Zucker","Öl",
    "Butter","Ei","Fleisch","Hähnchen","Rind","Schwein","Lamm","Bauch","Rücken","Kopf","Hand","Fuß","Bein",
    "Auge","Ohr","Nase","Mund","Zahn","Herz","Blut","Knochen","Haut","Gesundheit","Krankheit","Medizin",
    "Maschine","Werkzeug","Programm","Code","Software","Hardware","Internet","Server","Datenbank","Netzwerk",
    "Taste","Bildschirm","Tastatur","Maus","Drucker","Papier","Stift","Heft","Ordner","Karte","Plan",
    "Projekt","Termin","Kalender","Notiz","Brief","Paket","Post","Adresse","Stempel","Unterschrift",
    "Musik","Film","Bilder","Foto","Kamera","Radio","Fernseher","Zeitung","Buchhandlung","Bibliothek",
    "Theater","Museum","Sport","Spiel","Ball","Tor","Mannschaft","Trainer","Schiedsrichter","Zuschauer",
    "Straßenbahn","Taxi","Bahnhof","Flughafen","Hafen","Brücke","Tunnel","Platz","Park","See","Fluss",
    "Berg","Tal","Wald","Feld","Insel","Küste","Strand","Wüste","Meer","Ozean","Pfad","Kreuzung",
    "Ampel","Schild","Ticket","Fahrkarte","Pass","Visum","Grenze","Politik","Regierung","Parlament",
    "Behörde","Gericht","Polizei","Feuerwehr","Soldat","Steuer","Rechnung","Quittung","Vertrag",
    "Gesetz","Regel","Strafe","Prüfung","Note","Zeugnis","Diplom","Titel","Preis","Rabatt","Angebot",
    "Bestellung","Lieferung","Lager","Kunde","Kundin","Verkäufer","Verkäuferin","Service","Support",
    "Qualität","Menge","Gewicht","Größe","Länge","Breite","Höhe","Tiefe","Temperatur","Druck","Zeitpunkt",
    "Farbe","Form","Material","Holz","Metall","Glas","Plastik","Stein","Stoff","Papierkorb"
]

# Verbs (infinitives)
verbs = [
    "sein","haben","werden","können","müssen","sollen","wollen","dürfen","mögen","machen","tun","gehen","kommen",
    "fahren","fliegen","laufen","schlafen","essen","trinken","sprechen","sagen","fragen","antworten","hören",
    "sehen","lesen","schreiben","lernen","studieren","arbeiten","spielen","kaufen","verkaufen","öffnen",
    "schließen","beginnen","enden","starten","stoppen","sitzen","stehen","liegen","bleiben","bringen","nehmen",
    "geben","bekommen","finden","suchen","treffen","helfen","denken","glauben","wissen","kennen","verstehen",
    "erklären","zeigen","benutzen","brauchen","fühlen","leben","wohnen","reisen","besuchen","bauen","kochen",
    "backen","schwimmen","springen","tanzen","singen","malen","zeichnen","warten","hoffen","lieben","hassen",
    "lachen","weinen","gewinnen","verlieren","bezahlen","sparen","zahlen","schicken","holen","tragen","ziehen",
    "drücken","schneiden","reinigen","putzen","waschen","wiederholen","vorbereiten","entscheiden","vergleichen",
    "entwickeln","programmieren","debuggen","drucken","speichern","laden","installieren","aktualisieren",
    "konfigurieren","kompilieren","testen","deployen","loggen","analysieren","optimieren","verschlüsseln","entschlüsseln"
]

# Male names
male_names = [
    "Alexander","Maximilian","Felix","Lukas","Leon","Paul","Jonas","Tim","Noah","Elias","David","Daniel","Jan",
    "Philipp","Niklas","Sebastian","Benjamin","Martin","Thomas","Michael","Andreas","Christian","Peter","Johannes",
    "Oliver","Robert","Stefan","Florian","Patrick","Marcel","Kevin","Dominik","Simon","Julian","Tobias","Marco",
    "Sven","Kai","Jannik","Finn","Luca","Tom","Matteo","Moritz","Anton","Fabian","Joshua","Kilian","Pascal","René",
    "Ralf","Uwe","Jürgen","Dieter","Karl","Heinz","Frank","Holger","Bernd","Dirk","Volker","Rainer","Georg","Markus",
    "Matthias","Carsten","Björn","Heiko","Gerd","Ludwig","Theo","Till","Timo","Nils","Arne","Malte","Hannes","Henrik",
    "Cornelius","Konstantin","Christoph","Manuel","Gerrit","Hendrik","Günter","Wolf","Otto","Rudolf","Klaus","Hans",
    "Fritz","Albert","Walter","Leo","Oskar","Emil","Ferdinand","Johann","Nikolaus"
]

# Female names
female_names = [
    "Anna","Maria","Emilia","Mia","Lea","Lena","Julia","Laura","Sarah","Sophie","Johanna","Clara","Emma","Marie",
    "Lisa","Lina","Hannah","Jana","Nicole","Katharina","Carolin","Caroline","Carina","Christina","Christine",
    "Susanne","Sandra","Anja","Heike","Monika","Petra","Sabine","Nina","Nadine","Daniela","Franziska","Theresa",
    "Marlene","Paula","Luisa","Helena","Maja","Martha","Greta","Isabell","Isabelle","Charlotte","Amelie","Eva",
    "Tina","Ute","Silke","Gabriele","Birgit","Kerstin","Ingrid","Angelika","Renate","Brigitte","Saskia","Tanja",
    "Yvonne","Anita","Sina","Sabrina","Melanie","Martina","Claudia","Katrin","Ilona","Kira","Miriam","Rebecca",
    "Stefanie","Theresia","Helga","Gudrun","Ulrike","Hildegard","Annika","Antonia","Carla","Elisa","Elisabeth",
    "Margarita","Nora","Ronja","Selina","Verena","Anneliese","Agnes","Lotte","Ida","Frieda","Marlies","Grete"
]

# Colors
colors = [
    "rot","blau","grün","gelb","orange","violett","lila","pink","schwarz","weiß","grau","braun","beige","türkis",
    "cyan","magenta","gold","silber","bronze","marineblau","himmelblau","dunkelblau","hellblau","dunkelgrün",
    "hellgrün","bordeaux","weinrot","creme","petrol","oliv","mint","koralle","pfirsich","senf","lavendel",
    "indigo","elfenbein"
]

# Build DataFrame
df = pd.concat([
    make_df(nouns, "Substantiv"),
    make_df(verbs, "Verb"),
    make_df(male_names, "Männername"),
    make_df(female_names, "Frauenname"),
    make_df(colors, "Farbe"),
], ignore_index=True)

# Deduplicate just in case
df = df.drop_duplicates(subset=["word","category"]).reset_index(drop=True)

# Save CSV
path = "/mnt/data/de_woerterbuch_start.csv"
df.to_csv(path, index=False)

import caas_jupyter_tools
caas_jupyter_tools.display_dataframe_to_user("Startmenge Deutsches Wörterbuch (CSV)", df.head(50))

# Basic counts per category to show summary
counts = df["category"].value_counts().to_dict()
path, counts, len(df)
