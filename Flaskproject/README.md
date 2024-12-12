# RallyUp

**RallyUp** is de ultieme app voor padelliefhebbers die op zoek zijn naar nieuwe speelpartners en spannende wedstrijden. 
Of je nu zelf een zoekertje wilt plaatsen of er eentje accepteert, met RallyUp leg je moeiteloos connecties. 
Daarnaast biedt onze app slimme functies om transacties eenvoudig af te handelen, wedstrijden direct aan je agenda toe te voegen, 
en ervaringen te delen via een handig reviewsysteem.

---

## Functionaliteiten
1. **Plaatsen van zoekertjes**: Creëer een zoekertje om andere padelspelers te vinden met details zoals tijd, locatie en niveau.
2. **Accepteren van zoekertjes**: Vind zoekertjes die bij je passen en start een transactie. Voeg het spel daarna toe aan je agenda.
3. **Reviews schrijven en beheren**: Geef feedback na het spel en pas eerdere reviews eenvoudig aan.
4. **Gebruikers zoeken**: Zoek andere spelers op gebruikersnaam en bekijk hun profiel en beoordelingen.
5. **Voor jou-pagina**: Krijg gepersonaliseerde suggesties gebaseerd op je locatie en favoriete speeldagen.

---

## Speciaal algoritme
**RallyUp** gebruikt een slim algoritme om je padelervaring te personaliseren en te optimaliseren:

1. **Agenda-integratie**  
   Je geplande spellen worden automatisch gesynchroniseerd met je persoonlijke agenda (zoals Google Calendar of Apple Calendar).
   Bij het plannen of accepteren van een spel genereert de app een ICS-bestand dat je aan je agenda kunt toevoegen voor herinneringen en notificaties.

3. **Analyse van speelgewoonten en persoonlijke suggesties**  
   Het algoritme analyseert je favoriete speeldag via databasegegevens en geeft suggesties voor spellen en locaties in jouw omgeving.

---

## Installatie
Volg deze stappen om **RallyUp** lokaal te installeren en ervoor te zorgen dat het correct werkt met Flask:

### Vereisten
- Python 3.9+
- Pip (Python Package Installer)
- Virtualenv (optioneel, voor een virtuele omgeving)

### Instructies
1. **Clone de repository**  
   Clone de repository vanuit GitHub naar je lokale machine:
   ```bash
   git clone https://github.com/Marketplace-development/uneven-marketplace-da2024-group13.git
   ```

2. **Ga naar de projectmap**  
   ```bash
   cd uneven-marketplace-da2024-group13
   ```

3. **Maak een virtuele omgeving aan (optioneel)**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # Voor Mac/Linux
   venv\Scripts\activate     # Voor Windows
   ```

4. **Installeer de vereisten**  
   Installeer de benodigde Python-pakketten:
   ```bash
   pip install flask flask-sqlalchemy flask-migrate flask-wtf sqlalchemy python-ics
   ```

5. **Start de applicatie**  
   ```bash
   flask run
   ```

6. **Indien foutmelding ("Port in use")**  
   Start de applicatie op een andere poort:
   ```bash
   flask run --port=5001
   ```
---
## Links
- **[Figma](https://www.figma.com/design/PvbKYVUdIIh78QEKgkvtCD/Rally_up?node-id=0-1&t=RirFmI7af5mYUdv2-1)**  
  Bekijk hier onze Figma om ons conceptuele design te zien. 

- **[Miro Board](https://miro.com/welcomeonboard/TWhTWDVaRE5LWDR6T1ZIVVZJb0k1RVU1RTV6ZU1XMEZwS1F4Ui9xOXpYWTNYKzlOWWw2dVI4TDVVN0hEbFFoR3RGOWhNbHZ1dFJWc1VIdlR3WmIrSlhIdGVCRFRKc2VVR1JvTzdWUlAwT0Q5bnVyYUdLNDJINC9SZzcxeFVaYm0hZQ==?share_link_id=803440164873)**  
  Bekijk ons Miro-board voor meer details over het project en samenwerkingen.
---

## Projectstructuur

- **`run.py`**: Het startbestand van de applicatie. Hiermee zet je de app aan.
- **`config.py`**: Bevat de configuratie-instellingen voor de applicatie, zoals de database of beveiligingssleutels.
- **`app/`**: De hoofdmap van de applicatie:
  - **`__init__.py`**: Initialiseert de Flask-app en verbindt met de database.
  - **`models.py`**: Definieert de database-modellen: locatie, padelspeler, zoekertje, transaction en review.
  - **`routes.py`**: Bevat de routes en logica van de applicatie. Dit bestand bepaalt wat er gebeurt als je op knoppen klikt of een pagina bezoekt.
  - **`templates/`**: Bevat de HTML-sjablonen voor de applicatie.
  - **`static/`**: Bevat statische bestanden zoals PNG-bestanden (logo's en icoontjes).
- **`migrations/`**: Houdt veranderingen in de database bij.

---

## Toekomstige functionaliteiten

We zouden nog willen werken aan nieuwe functies om de app persoonlijker, interactiever en gebruiksvriendelijker te maken, met focus op betere matches, 
community-interactie en extra beloningen voor actieve spelers.

### 1. Meer geoptimaliseerd matchmaking-algoritme
In de toekomst willen we een geavanceerd matchmaking-algoritme bovenop het huidige ‘voor jou’-algoritme implementeren dat gebaseerd is op gebruikersreviews. 
Dit algoritme zal zoekertjes voorstellen die het beste aansluiten bij de voorkeuren en speelstijl van de gebruiker.

### 2. Statistieken, prestaties bijhouden en puntensysteem
Dit omvat een interactief puntensysteem dat wordt gesponsord door toekomstige partners. 
Gebruikers die actief deelnemen op de app – zoals het aanmaken van zoekertjes en reageren op zoekertjes van anderen – verdienen punten. 
Bij het behalen van een bepaald aantal punten kunnen spelers beloningen ontvangen van onze sponsors, zoals kortingsbonnen, 
merchandise of andere exclusieve voordelen. Dit systeem motiveert spelers om actief deel te nemen en versterkt de community rond de app.

### 3. Geavanceerd notificatiesysteem
Dit systeem zal gebruikers op de hoogte stellen wanneer hun zoekertje door andere padelspelers wordt geboekt. 
Gebruikers ontvangen direct een melding zodra ze inloggen, zodat ze op de hoogte blijven van de status van hun zoekertjes. 
Daarnaast zullen meldingen worden verstuurd wanneer nieuwe reviews over hen worden. Dit zorgt voor een efficiëntere en gebruiksvriendelijke ervaring, 
waarbij gebruikers geen belangrijke updates missen.

### 4. Conversatiesysteem
Dit systeem maakt het mogelijk om eenvoudig vragen te stellen, afspraken te maken en details te bespreken over geplaatste zoekertjes. 
Het conversatiesysteem biedt een veilige en gebruiksvriendelijke omgeving binnen de app, zodat spelers snel en effectief met elkaar in contact kunnen komen 
zonder externe platformen te gebruiken.

### 5. Volledig transactiesysteem met opties overschrijven, cash, PayPal
We willen het huidige simulatiesysteem voor transacties in de app uitbreiden naar een volledig werkend betalingssysteem. 
Dit zou gebruikers de mogelijkheid bieden om echte betalingen te doen via opties zoals overschrijving, contante betaling, of PayPal. 
Het doel is om transacties soepel en betrouwbaar te maken, zodat spelers eenvoudig hun reserveringen of andere betalingen kunnen afhandelen.
