from flask import render_template, request, redirect, url_for, flash, session, Response
from .models import db, Padelspeler, Zoekertje, Review, Locatie, Transaction
from datetime import datetime, timedelta, date
from decimal import Decimal
from ics import Calendar, Event
from sqlalchemy import func
import re


def update_verlopen_zoekertjes():
    """Zet de status van verlopen zoekertjes op False."""
    vandaag = datetime.now().date()
    huidige_tijd = datetime.now().time()

    verlopen_zoekertjes = Zoekertje.query.filter(
        (Zoekertje.datum < vandaag) |  # Zoekertjes van vorige datums
        ((Zoekertje.datum == vandaag) & (Zoekertje.start_time <= huidige_tijd)),  # Zoekertjes van vandaag waarvan de tijd is verlopen
        Zoekertje.status == True
    ).all()

    for zoekertje in verlopen_zoekertjes:
        zoekertje.status = False

    db.session.commit()

def register_routes(app):
    def get_form_data(request, fields):
        """Helperfunctie om formuliergegevens op te halen."""
        return {field: request.form.get(field) for field in fields}

    @app.route('/')
    def pre_home():
        return render_template('pre_home.html')

    @app.route('/home')
    def home():
        return render_template("home.html")

    @app.route('/registratie', methods=['GET', 'POST'])
    def registratie():
    # Vooraf unieke steden ophalen voor zowel GET als POST
        steden = Locatie.query.with_entities(Locatie.stad).distinct().order_by(Locatie.stad.asc()).all()
        steden = [stad[0] for stad in steden]  # Lijst van stadnamen

    # Lege data-initialisatie voor GET-verzoek
        data = {}

        if request.method == 'POST':
            fields = ['gebruikersnaam', 'email', 'telephone_number', 'woonplaats', 'niveau']
            data = get_form_data(request, fields)

            # Validatie voor telefoonnummer (9 tot 13 cijfers cijfers)
            phone_pattern = r'^(\+32)?\d{9,13}$'
            if not re.match(phone_pattern, data['telephone_number']):
                flash('Ongeldig telefoonnummer. Gebruik 9 tot 13 cijfers.', 'error')
                return render_template('register.html', data=data, steden=steden)
            
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                flash('Ongeldig e-mailadres.', 'error')
                return render_template('register.html', data=data, steden=steden)

            # Controleer of de gebruikersnaam uniek is
            existing_user = Padelspeler.query.filter_by(padelspeler_name=data['gebruikersnaam']).first()
            if existing_user:
                flash('Gebruikersnaam is al in gebruik.', 'error')
                return render_template('register.html', data=data, steden=steden)

            # Controleer of de e-mail al geregistreerd is
            existing_email = Padelspeler.query.filter_by(email=data['email']).first()
            if existing_email:
                flash('Dit e-mailadres is al geregistreerd.', 'error')
                return render_template('register.html', data=data, steden=steden)        

            # Nieuwe gebruiker maken
            new_padelspeler = Padelspeler(
                padelspeler_name=data['gebruikersnaam'],
                email=data['email'],
                telephone_number=data['telephone_number'],
                woonplaats=data['woonplaats'],
                niveau=data['niveau'],
            )
            db.session.add(new_padelspeler)
            db.session.commit()

            # Sla userID op in de sessie
            session['userID'] = new_padelspeler.padelspeler_id
            return redirect(url_for('zoekertjes'))
    

        return render_template('register.html', data=data, steden=steden)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            mail = request.form['email']

            # Controleer of het e-mailadres in de database bestaat
            existing_user = Padelspeler.query.filter_by(email=mail).first()
            if existing_user:
                session['userID'] = existing_user.padelspeler_id
                return redirect(url_for('zoekertjes'))
            else:
                flash('E-mailadres niet geregistreerd.', 'error')
                return render_template('login.html')

        return render_template('login.html')
    
    @app.route('/zoekertjes', methods=['GET'])
    def zoekertjes():
        """View and search zoekertjes."""
        userID = session.get('userID')
        update_verlopen_zoekertjes()

        # Haal locaties op en organiseer ze per stad
        locaties = Locatie.query.order_by(Locatie.stad.asc(), Locatie.sportclub_naam.asc()).all()
        locaties_per_stad = {}
        for locatie in locaties:
            if locatie.stad not in locaties_per_stad:
                locaties_per_stad[locatie.stad] = []
            locaties_per_stad[locatie.stad].append(locatie)

        # Haal filters op uit request.args
        data = {
            'datum': request.args.get('datum', ''),
            'locatie': request.args.get('locatie', ''),
            'stad': request.args.get('stad', ''),
            'niveau': request.args.get('niveau', ''),
            'prijs': request.args.get('prijs', ''),
            'aantal_personen': request.args.get('aantal_personen', '')
        }

        # Validatie: controleer of locatie bij stad hoort
        if data['locatie'] and data['stad']:
            flash("Je kan slechts één filter invullen: sportclub of stad, niet beide.", "error")
            return render_template(
                'zoekertjes.html',
                zoekertjes=[],
                locaties_per_stad=locaties_per_stad,
                data=data
            )

        # Base query voor zoekertjes
        zoekertjes = Zoekertje.query.filter(
            Zoekertje.padelspeler_id != userID,
            Zoekertje.status == True
        ).outerjoin(Transaction, (Transaction.listing_id == Zoekertje.listing_id) & (Transaction.betaler_id == userID)) \
            .filter(Transaction.transaction_id == None) \
            .order_by(Zoekertje.datum.asc())

        # Filter zoekertjes op basis van opgegeven waarden
        if data['stad']:
            zoekertjes = zoekertjes.join(Locatie).filter(Locatie.stad == data['stad'])

        if data['locatie']:
            zoekertjes = zoekertjes.join(Locatie).filter(Locatie.sportclub_naam == data['locatie'])

        if data['datum']:
            zoekertjes = zoekertjes.filter(Zoekertje.datum == datetime.strptime(data['datum'], '%Y-%m-%d'))

        if data['niveau']:
            zoekertjes = zoekertjes.filter(Zoekertje.niveau == data['niveau'])

        if data['prijs']:
            try:
                if '-' in data['prijs']:
                    min_price, max_price = map(int, data['prijs'].split('-'))
                    zoekertjes = zoekertjes.filter(Zoekertje.prijs >= min_price, Zoekertje.prijs <= max_price)
                else:
                    zoekertjes = zoekertjes.filter(Zoekertje.prijs == int(data['prijs']))
            except ValueError:
                app.logger.warning(f"Ongeldig prijsformaat: {data['prijs']}")

        if data['aantal_personen']:
            zoekertjes = zoekertjes.filter(Zoekertje.aantal_personen == int(data['aantal_personen']))

        zoekertjes1 = zoekertjes.all()

        return render_template(
            'zoekertjes.html',
            zoekertjes=zoekertjes1,
            locaties_per_stad=locaties_per_stad,
            data=data
        )
        
    @app.route('/zoekertjes/nieuw', methods=['GET', 'POST'])
    def nieuw_zoekertje():
        userID = session.get('userID')
    
        # Initialiseer de data-variabele
        data = {}

        locaties = Locatie.query.order_by(Locatie.stad.asc()).all()
        locaties_per_stad = {}
        for locatie in locaties:
            if locatie.stad not in locaties_per_stad:
                locaties_per_stad[locatie.stad] = []
            locaties_per_stad[locatie.stad].append(locatie)

        if request.method == 'POST':
            padelspeler_id = userID
            padelspeler = Padelspeler.query.get_or_404(padelspeler_id)
            data = request.form.to_dict()        
           
           
            name = data['name']
            datum = datetime.strptime(data['datum'], '%Y-%m-%d')
            start_time = datetime.strptime(data['start_time'], '%H:%M')
            end_time = datetime.strptime(data['end_time'], '%H:%M')
            prijs = float(data['prijs'].replace(",", "."))
            sportclub = data['locatie']
            aantal_personen = int(data['aantal_personen'])
            type_spel = data['type_spel']
            description = data['description']
            plein_nr = int(data['plein_nr'])
            niveau = data['niveau']

            nieuw = Zoekertje(
                padelspeler_id=userID,
                sportclub=sportclub,
                niveau=niveau,
                aantal_personen=aantal_personen,
                type_spel=type_spel,
                name=name,
                description=description,
                status=True,
                prijs=prijs,
                plein_nr=plein_nr,
                datum=datum,
                start_time=start_time,
                end_time=end_time
            )
            db.session.add(nieuw)
            db.session.commit()
            Padelspeler.update_frequent_play_days()

            return redirect(url_for('zoekertjes'))

        return render_template('nieuw_zoekertje.html', locaties_per_stad=locaties_per_stad, data=data)

    @app.route('/zoekertjes/edit/<int:listing_id>', methods=['GET', 'POST'])
    def edit_zoekertje(listing_id):
        zoekertje = Zoekertje.query.get_or_404(listing_id)

        locaties = Locatie.query.order_by(Locatie.stad.asc()).all()
        locaties_per_stad = {}
        for locatie in locaties:
            if locatie.stad not in locaties_per_stad:
                locaties_per_stad[locatie.stad] = []
            locaties_per_stad[locatie.stad].append(locatie)

        if request.method == 'POST':
            zoekertje.name = request.form['name'] or zoekertje.name
            zoekertje.description = request.form['description'] or zoekertje.description
            zoekertje.prijs = float(request.form['prijs']) if request.form['prijs'] else zoekertje.prijs
            zoekertje.datum = request.form['datum'] or zoekertje.datum
            zoekertje.start_time = request.form['start_time'] or zoekertje.start_time
            zoekertje.end_time = request.form['end_time'] or zoekertje.end_time
            zoekertje.plein_nr = int(request.form['plein_nr']) if request.form['plein_nr'] else zoekertje.plein_nr
            zoekertje.aantal_personen = int(request.form['aantal_personen']) if request.form['aantal_personen'] else zoekertje.aantal_personen
            zoekertje.type_spel = request.form['type_spel'] or zoekertje.type_spel
            zoekertje.niveau = request.form['niveau'] if request.form['niveau'] else zoekertje.niveau

            locatie_id = request.form.get('locatie')
            if locatie_id:
                zoekertje.sportclub = int(locatie_id)

            db.session.commit()
            return redirect(url_for('zoekertje_edited'))

        # Render de template met het zoekertje en de locaties
        return render_template('edit_zoekertje.html', zoekertje=zoekertje, locaties_per_stad=locaties_per_stad)
    
    @app.route('/zoekertje/edited')
    def zoekertje_edited():
        return render_template('zoekertje_edited.html')

    @app.route('/zoekertjes/delete/<int:listing_id>', methods=['POST'])
    def delete_zoekertje(listing_id):
        zoekertje = Zoekertje.query.get_or_404(listing_id)

    # Verwijder het zoekertje
        zoekertje.status = False
        db.session.commit()
        return redirect(url_for('zoekertje_deleted'))
    
    @app.route('/zoekertjes/deleted/')
    def zoekertje_deleted():
        return render_template('zoekertje_deleted.html')

    
    @app.route('/specifiekzoekertje/<int:listing_id>')
    def specifiekzoekertje(listing_id):
        # Haal het zoekertje op met de bijbehorende padelspeler (eigenaar)
        zoekertje = Zoekertje.query.get_or_404(listing_id)
        eigenaar = Padelspeler.query.get_or_404(zoekertje.padelspeler_id)  # De eigenaar van het zoekertje
        reviews = Review.query.filter_by(user_id_medespeler=eigenaar.padelspeler_id).all()

        return render_template('specifiekzoekertje.html', zoekertje=zoekertje, eigenaar=eigenaar, reviews=reviews)  

    @app.route('/profile')
    def profile():
        userID = session.get('userID')
        update_verlopen_zoekertjes()

        user = Padelspeler.query.get_or_404(userID)
        reviews = Review.query.filter_by(user_id_medespeler=userID).all()
        for review in reviews:
            plaatser = Padelspeler.query.get(review.plaatser_id)
            review.plaatser_name = plaatser.padelspeler_name if plaatser else "Onbekend"

        zoekertjes = db.session.query(
            Zoekertje,
            func.count(Transaction.transaction_id).label('transaction_count'),
            func.string_agg(Padelspeler.padelspeler_name, ', ').label('betaler_namen')
        ).outerjoin(
            Transaction, Transaction.listing_id == Zoekertje.listing_id
        ).outerjoin(
            Padelspeler, Padelspeler.padelspeler_id == Transaction.betaler_id
        ).filter(
            Zoekertje.padelspeler_id == userID,
            Zoekertje.status == True
        ).group_by(Zoekertje.listing_id).all()


        zoekertjes_data = [
            {
                "zoekertje": row[0],
                "transaction_count": row[1],
                "betaler_namen": row[2].split(',') if row[2] else [],
                "formatted_date": row[0].datum.strftime('%d-%m-%Y') if row[0].datum else None
            }
            for row in zoekertjes
        ]

        vandaag = datetime.now().date()
        huidige_tijd = datetime.now().time()
        komende_sessies = Zoekertje.query.join(Transaction).filter(
            (Transaction.betaler_id == userID) | (Transaction.ontvanger_id == userID),
            (Zoekertje.datum > vandaag) |
            ((Zoekertje.datum == vandaag) & (Zoekertje.end_time > huidige_tijd))
        ).order_by(Zoekertje.datum.asc(), Zoekertje.start_time.asc()).all()

        return render_template(
            'eigenprofiel.html',
            user=user,
            reviews=reviews,
            zoekertjes=zoekertjes_data,
            komende_sessies=komende_sessies
        )

        
    @app.route('/edit_profile', methods=['GET', 'POST'])
    def edit_profile():
        userID = session.get('userID')
      
        user = Padelspeler.query.get_or_404(userID)

        # Voeg deze regel toe om steden op te halen
        steden = Locatie.query.with_entities(Locatie.stad).distinct().order_by(Locatie.stad.asc()).all()
        steden = [stad[0] for stad in steden]  # Zet tuples om in een lijst van strings

        if request.method == 'POST':
            # Verkrijg de nieuwe gegevens van de gebruiker
            user.padelspeler_name = request.form['padelspeler_name'] or user.padelspeler_name
            user.telephone_number = request.form['telephone_number'] or user.telephone_number
            user.email = request.form['email'] or user.email
            user.woonplaats = request.form['woonplaats'] or user.woonplaats
            user.niveau = request.form['niveau'] or user.niveau

            db.session.commit()
            return redirect(url_for('profile_edited'))

        return render_template('edit_profile.html', user=user, steden=steden)
    
    @app.route('/profile/edited')
    def profile_edited():
        return render_template('profile_edited.html')

    @app.route('/calendar', methods=['GET'])
    def calendar():
        """Kalenderpagina."""
        return render_template('calendar.html')
    
    @app.route('/anderprofiel/<string:eigenaar>', methods=['GET'])
    def anderprofiel(eigenaar):
        eigenaar = Padelspeler.query.filter_by(padelspeler_name=eigenaar).first_or_404()
        reviews = Review.query.filter_by(user_id_medespeler=eigenaar.padelspeler_id).all()
        zoekertje = Zoekertje.query.filter_by(padelspeler_id=eigenaar.padelspeler_id, status=True).first()
        for review in reviews:
            plaatser = Padelspeler.query.get(review.plaatser_id)  # Zoek de plaatser op basis van plaatser_id
            review.plaatser_name = plaatser.padelspeler_name if plaatser else "Onbekend"
        return render_template('anderprofiel.html', reviews=reviews, eigenaar=eigenaar, zoekertje = zoekertje)
    
    @app.route('/anderprofiel_/<string:eigenaar>', methods=['GET'])
    def anderprofiel_(eigenaar):
        eigenaar = Padelspeler.query.filter_by(padelspeler_name=eigenaar).first_or_404()
        reviews = Review.query.filter_by(user_id_medespeler=eigenaar.padelspeler_id).all()
        for review in reviews:
            plaatser = Padelspeler.query.get(review.plaatser_id)  # Zoek de plaatser op basis van plaatser_id
            review.plaatser_name = plaatser.padelspeler_name if plaatser else "Onbekend"
        return render_template('anderprofiel_.html', reviews=reviews, eigenaar=eigenaar)

    
    @app.route('/transactie/<int:listing_id>', methods=['GET', 'POST'])
    def transactie(listing_id):
        userID = session.get('userID')

        zoekertje = Zoekertje.query.filter_by(listing_id=listing_id).first_or_404()

        # Controleer of de gebruiker al een transactie voor dit zoekertje heeft

        if request.method == 'POST':
            # Simuleer betalingsverwerking
      
                # Placeholder voor echte betaalverwerking
                    # Bereken de commissie (bijv. 10% van de prijs)
            commissie = zoekertje.prijs * Decimal('0.10')
            commissie = round(commissie, 2)

                    # Maak een nieuwe transactie aan
            transactie = Transaction(
                ontvanger_id=zoekertje.padelspeler_id,  # Stel dat dit de ontvanger is
                betaler_id=userID,  # Huidige gebruiker is de betaler
                listing_id=listing_id,
                prijs=zoekertje.prijs,
                commision_fee=commissie,
                )

            db.session.add(transactie)
            transacties_count = Transaction.query.filter_by(listing_id=listing_id).count()
                    
            if transacties_count >= zoekertje.aantal_personen:
                zoekertje.status = False
            
            db.session.commit()
            Padelspeler.update_frequent_play_days()
            return redirect(url_for('succes', listing_id=zoekertje.listing_id))

        return render_template('transactie.html', zoekertje=zoekertje)

    
    @app.route('/succes/<int:listing_id>', methods=['GET'])
    def succes(listing_id):
        zoekertje = Zoekertje.query.filter_by(listing_id=listing_id).first_or_404()
        """Route voor succesvolle betaling."""
        return render_template('succes.html', zoekertje=zoekertje)
    
    @app.route('/review/nieuw', methods=['GET', 'POST'])
    def nieuwe_review():
        plaatser_id = session['userID']
        bestaande_review = None

        if request.method == 'POST':
            gebruikersnaam = request.form.get('gebruikersnaam')
            score = request.form.get('score')
            commentaar = request.form.get('commentaar')
            confirm = request.form.get('confirm')
            print(f"DEBUG: ontvangen score={score}, commentaar={commentaar}, gebruikersnaam={gebruikersnaam}")
           
        # Zoek de medespeler op basis van gebruikersnaam
            medespeler = db.session.query(Padelspeler).filter_by(padelspeler_name=gebruikersnaam).first()
            if not medespeler:
                return render_template('review_form.html', gebruikersnaam_bestaat=False, error_message="Medespeler gebruikersnaam bestaat niet.")

        # Controleer of er een bestaande review is
            bestaande_review = db.session.query(Review).filter_by(
                user_id_medespeler=medespeler.padelspeler_id,
                plaatser_id=plaatser_id
            ).first()

            if bestaande_review and not confirm:
            # Bevestiging vragen als er een bestaande review is
                return render_template('confirm_review.html', gebruikersnaam=gebruikersnaam, bestaande_review=bestaande_review, nieuwe_score=score,
                nieuw_commentaar=commentaar)

            if bestaande_review and confirm == 'ja':
            # Overschrijf de bestaande review
                
                bestaande_review.score = score
                bestaande_review.commentaar = commentaar
                db.session.commit()
                return redirect(url_for('succesreview'))
            
            if not bestaande_review:
            # Maak een nieuwe review aan als er geen bestaande review is
                nieuwe_review = Review(
                    plaatser_id=plaatser_id,
                    user_id_medespeler=medespeler.padelspeler_id,
                    score = score,
                    commentaar=commentaar
                )
                db.session.add(nieuwe_review)
                db.session.commit()
                return redirect(url_for('succesreview'))

        # Als overschrijven wordt geweigerd
            if bestaande_review and confirm == 'nee':
                return redirect(url_for('zoekertjes'))

        return render_template('review_form.html')

    
    @app.route('/succesreview')
    def succesreview():
        return render_template('succesreview.html')
    
    @app.route('/eigentransacties', methods=['GET'])
    def eigentransacties():

        userID = session['userID']  

        transacties_betaler = db.session.query(Transaction).select_from(Transaction) \
            .filter_by(betaler_id=userID) \
            .join(Zoekertje, Transaction.listing_id == Zoekertje.listing_id) \
            .join(Locatie, Zoekertje.sportclub == Locatie.sportclub) \
            .add_columns(Zoekertje.name, Zoekertje.prijs, Locatie.sportclub_naam, Locatie.straat, Locatie.postcode, Locatie.nummer, Locatie.stad, Locatie.land) \
            .all()

        transacties_ontvanger = db.session.query(Transaction).select_from(Transaction) \
            .filter_by(ontvanger_id=userID) \
            .join(Zoekertje, Transaction.listing_id == Zoekertje.listing_id) \
            .join(Locatie, Zoekertje.sportclub == Locatie.sportclub) \
            .add_columns(Zoekertje.name, Zoekertje.prijs, Locatie.sportclub_naam, Locatie.straat, Locatie.postcode, Locatie.nummer, Locatie.stad, Locatie.land) \
            .all()

        return render_template(
            'eigentransacties.html',  
            transacties_betaler=transacties_betaler,
            transacties_ontvanger=transacties_ontvanger
        )
    @app.route('/logout', methods=['GET'])
    def logout():
        # Verwijder de gebruiker uit de sessie
        session.pop('userID', None)  # Zorg ervoor dat 'userID' wordt verwijderd
        session.clear()  # Optioneel: verwijder alle sessiegegevens

        return redirect(url_for('home')) 
    @app.route('/profielen', methods=['GET'])
    def profielen():
        zoekterm = request.args.get('zoekterm', '').strip()  # Haal de zoekterm uit de queryparameters
        if zoekterm:
            profielen = Padelspeler.query.filter(Padelspeler.padelspeler_name.ilike(f"%{zoekterm}%")).all()
        else:
            profielen = Padelspeler.query.all()

        return render_template('profielen.html', profielen=profielen, zoekterm=zoekterm)
    

    @app.route('/ical/<int:listing_id>')
    def toevoegen_calendar(listing_id):
        zoekertje = Zoekertje.query.filter_by(listing_id=listing_id).first_or_404()

        event_date = zoekertje.datum 
        start_datetime = datetime.combine(event_date, zoekertje.start_time)
        end_datetime = datetime.combine(event_date, zoekertje.end_time)

        calendar = Calendar()
        event = Event()
        event.name = zoekertje.name  
        event.begin = start_datetime
        event.end = end_datetime 
        event.description = zoekertje.description or "Geen beschrijving beschikbaar"
        event.location = zoekertje.locatie.sportclub_naam or "Geen locatie beschikbaar"

        calendar.events.add(event)

        ical_content = str(calendar)

        event_name = zoekertje.name.replace(" ", "_") if zoekertje.name else "evenement"
        response = Response(ical_content, mimetype="text/calendar")
        response.headers['Content-Disposition'] = f'attachment; filename={event_name}.ics'
        return response
    
    @app.route('/analyse/update-frequent-play-day', methods=['POST'])
    def update_frequent_play_day():
        Padelspeler.update_frequent_play_days()
        return "Frequent play days successfully updated for all players!"

    @app.route('/frequent_day_reminder', methods=['GET'])
    def frequent_day_reminder():
        userID = session.get('userID')
        update_verlopen_zoekertjes()


   
        user = Padelspeler.query.get_or_404(userID)


        open_zoekertjes = user.check_open_zoekertje_op_frequent_day()

        city_zoekertjes = Zoekertje.query.join(Locatie).filter(
            Locatie.stad == user.woonplaats,
            Zoekertje.status == True,
            Zoekertje.padelspeler_id != userID
        ).order_by(Zoekertje.datum.asc()).all()


        return render_template(
            'frequent_day_reminder.html',
            zoekertjes=open_zoekertjes,
            frequent_day=user.frequent_play_day,
            city_zoekertjes=city_zoekertjes
        )
    
    @app.route('/eigenprofiel/specifiekzoekertje/<int:listing_id>', methods=['GET'])
    def eigenprofiel_specifiek_zoekertje(listing_id):
        zoekertje = Zoekertje.query.get_or_404(listing_id)
        eigenaar = Padelspeler.query.get_or_404(zoekertje.padelspeler_id)

        return render_template(
            'eigenprofiel_specifiek_zoekertje.html',
            zoekertje=zoekertje,
            eigenaar=eigenaar
        )
