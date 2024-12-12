from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db
from sqlalchemy.orm import relationship
from sqlalchemy import func


class Locatie(db.Model):
    __tablename__ = "locatie"

    sportclub = db.Column(db.Integer, primary_key=True)
    sportclub_naam = db.Column(db.String(50))
    straat = db.Column(db.String(100), nullable=False)
    postcode = db.Column(db.String(10), nullable=False)
    nummer = db.Column(db.Integer, nullable=False)
    stad = db.Column(db.String(50), nullable=False)
    land = db.Column(db.String(50), nullable=False)

class Padelspeler(db.Model):
    _tablename_ = "padelspeler"

    padelspeler_id = db.Column(db.Integer, primary_key=True)
    padelspeler_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telephone_number = db.Column(db.String(20))
    woonplaats = db.Column(db.String(50))
    niveau = db.Column(db.String(50))
    frequent_play_day = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now())
    
    @classmethod
    def update_frequent_play_days(cls):
        # Mapping voor Nederlandse dagen
        weekdag_mapping = {
            '0': 'Zondag',
            '1': 'Maandag',
            '2': 'Dinsdag',
            '3': 'Woensdag',
            '4': 'Donderdag',
            '5': 'Vrijdag',
            '6': 'Zaterdag',
        }

        # Combineer geplaatste zoekertjes en deelgenomen zoekertjes
        alle_speeldagen_per_speler = (
            db.session.query(
                Zoekertje.padelspeler_id.label('speler_id'),
                func.extract('dow', Zoekertje.datum).label('weekday'),
                func.count(Zoekertje.listing_id).label('speel_count')
            )
            .group_by(Zoekertje.padelspeler_id, func.extract('dow', Zoekertje.datum))
            .union(
                db.session.query(
                    Transaction.betaler_id.label('speler_id'),
                    func.extract('dow', Zoekertje.datum).label('weekday'),
                    func.count(Transaction.transaction_id).label('speel_count')
                )
                .join(Zoekertje, Zoekertje.listing_id == Transaction.listing_id)
                .group_by(Transaction.betaler_id, func.extract('dow', Zoekertje.datum))
            )
            .subquery()
        )

       
    # Subquery om de maximale speel_count per speler te vinden
        max_speel_count_per_speler = (
            db.session.query(
                alle_speeldagen_per_speler.c.speler_id,
                func.max(alle_speeldagen_per_speler.c.speel_count).label('max_speel_count')
            )
            .group_by(alle_speeldagen_per_speler.c.speler_id)
            .subquery()
        )

    # Zoek de meest gespeelde dag per speler
        meest_gespeelde_dag = (
            db.session.query(
                alle_speeldagen_per_speler.c.speler_id,
                alle_speeldagen_per_speler.c.weekday
            )
            .join(
                max_speel_count_per_speler,
                (alle_speeldagen_per_speler.c.speler_id == max_speel_count_per_speler.c.speler_id) &
                (alle_speeldagen_per_speler.c.speel_count == max_speel_count_per_speler.c.max_speel_count)
            )
            .all()
        )

        # Update de frequent_play_day voor elke speler
        for speler_id, weekday in meest_gespeelde_dag:
            speler = cls.query.get(speler_id)
            if speler:
                frequent_day = weekdag_mapping[str(int(weekday))]
                speler.frequent_play_day = frequent_day
        
        db.session.commit()

    def check_open_zoekertje_op_frequent_day(self):
        if not self.frequent_play_day:
            return None  # Geen frequent play day ingesteld.

        # Mapping voor dagen in het Nederlands
        day_mapping = {
            'Zondag': 0,
            'Maandag': 1,
            'Dinsdag': 2,
            'Woensdag': 3,
            'Donderdag': 4,
            'Vrijdag': 5,
            'Zaterdag': 6,
        }

        # Convert de frequent day naar een numerieke waarde
        frequent_day_num = day_mapping.get(self.frequent_play_day)

        vandaag = datetime.now().date()
        open_zoekertje = Zoekertje.query.filter(
            Zoekertje.datum >= vandaag,
            func.extract('dow', Zoekertje.datum) == frequent_day_num,  # Specifieke dag van de week
            Zoekertje.status == True,  # Alleen actieve zoekertjes
            Zoekertje.padelspeler_id != self.padelspeler_id  # Niet door de gebruiker zelf geplaatst
        ).outerjoin(
            Transaction, (Transaction.listing_id == Zoekertje.listing_id) & (Transaction.betaler_id == self.padelspeler_id)
        ).filter(
            Transaction.transaction_id == None  # Geen transactie door deze gebruiker
        ).order_by(
            Zoekertje.datum.asc()
        ).all()

        return open_zoekertje



class Zoekertje(db.Model):
    __tablename__ = "zoekertje"

    listing_id = db.Column(db.Integer, primary_key=True)
    padelspeler_id = db.Column(db.Integer, db.ForeignKey("padelspeler.padelspeler_id"))
    sportclub = db.Column(db.Integer, db.ForeignKey("locatie.sportclub"))
    niveau = db.Column(db.String(50))
    aantal_personen = db.Column(db.Integer)
    type_spel = db.Column(db.String(50))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Boolean, default=True)
    prijs = db.Column(db.Numeric(10, 2))
    plein_nr = db.Column(db.Integer)
    datum = db.Column(db.Date, nullable = False)
    start_time = db.Column(db.Time, nullable = False)
    end_time = db.Column(db.Time, nullable = False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    """gebruik een backref zodat je vanuit een Padelspeler direct bijbehorende zoekertjes kunt ophalen."""

    padelspeler = relationship("Padelspeler", backref="zoekertje")
    locatie = relationship("Locatie", backref="zoekertje")
    
    def formatted_date(self):
        """Formatteer datum naar dag van de week en datum."""
        if self.datum:
            # Mapping van weekdagen (correct voor maandag = 0)
            weekdagen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
            weekdag_index = self.datum.weekday()  # weekday() geeft maandag = 0, zondag = 6
            weekdag = weekdagen[weekdag_index]
            return f"{weekdag} {self.datum.strftime('%d-%m-%Y')}"
        return "Niet opgegeven"

class Transaction(db.Model):
    __tablename__ = "transaction"

    transaction_id = db.Column(db.Integer, primary_key=True)
    ontvanger_id = db.Column(db.Integer, db.ForeignKey("padelspeler.padelspeler_id"))
    betaler_id = db.Column(db.Integer, db.ForeignKey("padelspeler.padelspeler_id"))
    listing_id = db.Column(db.Integer, db.ForeignKey("zoekertje.listing_id"))
    prijs = db.Column(db.Numeric(10, 2), nullable=False)
    commision_fee = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.now())


class Review(db.Model):
    __tablename__ = "review"

    plaatser_id = db.Column(db.Integer, db.ForeignKey("padelspeler.padelspeler_id"), primary_key=True)
    user_id_medespeler = db.Column(db.Integer, db.ForeignKey("padelspeler.padelspeler_id"), primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    commentaar = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now())
