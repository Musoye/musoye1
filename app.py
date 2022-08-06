#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
from flask_moment import Moment
from sqlalchemy.sql.expression import func
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db=SQLAlchemy(app)
migrate=Migrate(app,db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:musoye2004@localhost:5432/musoye1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show(db.Model):
    __tablename__='Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f'Id;{self.id} Artist;{self.artist_id} Venue;{self.venue_id}'

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column((db.String(120)))
    website_link=db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean,default=False)
    seeking_description=db.Column(db.String())
    shows = db.relationship('Show', backref="venue", lazy=True) 


    def __repr__(self): 
      return f'Id;{self.id} Name of Venue;{self.name} Address;{self.address}'





class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link =db.Column(db.String(120))
    seeking_venue =db.Column(db.Boolean,default=False)
    seeking_description =db.Column(db.String(120))
    shows = db.relationship('Show', backref="artist", lazy=True)


    def __repr__(self): 
      return f'Id;{self.id} Name of Artist;{self.name} Address;{self.phone}'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
#db.create_all()

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  avenues = db.session.query(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []
  for avenue in avenues:
    allvenues = Venue.query.filter(Venue.state==avenue.state).filter(Venue.city==avenue.city).all()
    venue_data = []
    for venue in allvenues:
      upcoming = len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
      venue_data.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": upcoming,
      })
    data.append({
      "city": avenue.city,
      "state": avenue.state, 
      "venues": venue_data
    })
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
    # "city": "San Francisco",
    # "state": "CA",
    # "venues": [{
      # "id": 1,
      # "name": "The Musical Hop",
      # "num_upcoming_shows": 0,
    # }, {
      # "id": 3,
      # "name": "Park Square Live Music & Coffee",
      # "num_upcoming_shows": 1,
    # }]
  # }, {
    # "city": "New York",
    # "state": "NY",
    # "venues": [{
      # "id": 2,
      # "name": "The Dueling Pianos Bar",
      # "num_upcoming_shows": 0,
    # }]
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  searches = []

  for result in results:
    upcoming=len((Show).query.filter(Show.venue_id == result.id).filter(Show.start_time > datetime.now()).all())
    searches.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": upcoming,
    })
  
  response={}
  response['count']=len(results)
  response['data']=searches



  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
    # "count": 1,
    # "data": [{
      # "id": 2,
      # "name": "The Dueling Pianos Bar",
      # "num_upcoming_shows": 0,
    # }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):    
  ven = db.session.query(Venue).get(venue_id)
  if ven == '': 
    abort(404)
  upcoming_shows = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_show = []

  previous_shows= Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  for show in previous_shows:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  for show in upcoming_shows:
    upcoming_show.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
    })
  data = {}
  upcoming=len(upcoming_show)
  past=len(past_shows)
  data['id']=ven.id
  data['name']=ven.name
  data['genres']=ven.genres
  data['address']= ven.address
  data['city']=ven.city
  data['state']=ven.state
  data['phone']=ven.phone
  data['website_link']=ven.website_link
  data['facebook_link']=ven.facebook_link
  data['seeking_talent']=ven.seeking_talent
  data['seeking_description']=ven.seeking_description
  data['image_link']=ven.image_link
  data['past_shows']=past_shows
  data['upcoming_shows']=upcoming_show
  data['past_shows_count']=past
  data['upcoming_shows_count']=upcoming
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
    # "id": 1,
    # "name": "The Musical Hop",
    # "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    # "address": "1015 Folsom Street",
    # "city": "San Francisco",
    # "state": "CA",
    # "phone": "123-123-1234",
    # "website": "https://www.themusicalhop.com",
    # "facebook_link": "https://www.facebook.com/TheMusicalHop",
    # "seeking_talent": True,
    # "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    # # "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    # "past_shows": [{
      # "artist_id": 4,
      # "artist_name": "Guns N Petals",
      # # "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      # "start_time": "2019-05-21T21:30:00.000Z"
    # }],
    # "upcoming_shows": [],
    # "past_shows_count": 1,
    # "upcoming_shows_count": 0,
  # }
  # data2={
    # "id": 2,
    # "name": "The Dueling Pianos Bar",
    # "genres": ["Classical", "R&B", "Hip-Hop"],
    # "address": "335 Delancey Street",
    # "city": "New York",
    # "state": "NY",
    # "phone": "914-003-1132",
    # "website": "https://www.theduelingpianos.com",
    # "facebook_link": "https://www.facebook.com/theduelingpianos",
    # "seeking_talent": False,
    # # "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    # "past_shows": [],
    # "upcoming_shows": [],
    # "past_shows_count": 0,
    # "upcoming_shows_count": 0,
  # }
  # data3={
    # "id": 3,
    # "name": "Park Square Live Music & Coffee",
    # "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    # "address": "34 Whiskey Moore Ave",
    # "city": "San Francisco",
    # "state": "CA",
    # "phone": "415-000-1234",
    # "website": "https://www.parksquarelivemusicandcoffee.com",
    # "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    # "seeking_talent": False,
    # # "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    # "past_shows": [{
      # "artist_id": 5,
      # "artist_name": "Matt Quevedo",
      # # "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      # "start_time": "2019-06-15T23:00:00.000Z"
    # }],
    # "upcoming_shows": [{
      # "artist_id": 6,
      # "artist_name": "The Wild Sax Band",
      # # "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      # "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
      # "artist_id": 6,
      # "artist_name": "The Wild Sax Band",
      # # "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      # "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
      # "artist_id": 6,
      # "artist_name": "The Wild Sax Band",
      # # "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      # "start_time": "2035-04-15T20:00:00.000Z"
    # }],
    # "past_shows_count": 1,
    # "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try: 
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_talent = True if 'seeking_talent' in request.form else False 
    seeking_description = request.form['seeking_description']

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone,genres=genres,facebook_link=facebook_link,image_link=image_link, website_link=website_link, seeking_talent=seeking_talent,seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()

  if not error: 
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['get'])
def delete_venue(venue_id):
  error = False
  try:
    venue = db.session.query(Venue).get(venue_id)
    mus=venue.name
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error: 
    flash(f'An error occurred!. Venue {mus} could not be deleted')
  else: 
    flash(f'Venue {mus} was successfully deleted!.')
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artist_data = Artist.query.all()
  # TODO: replace with real data returned from querying the database
  # data=[{
    # "id": 4,
    # "name": "Guns N Petals",
  # }, {
    # "id": 5,
    # "name": "Matt Quevedo",
  # }, {
    # "id": 6,
    # "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=artist_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  search_term=search_term.lower()
  results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  searches = []

  for result in results:
    upcoming=len(Show.query.filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all())
    searches.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": upcoming,
    })
  
  response={}
  response['num']=len(results)
  response['data']=searches

  # num =len(results)
  # response.num=num
  # response.data=searches
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
    # "count": 1,
    # "data": [{
      # "id": 4,
      # "name": "Guns N Petals",
      # "num_upcoming_shows": 0,
    # }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist_query= db.session.query(Artist).get(artist_id)

  if artist_query == '':
    abort(404)
  previous_shows= db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  past_shows = []

  for show in previous_shows:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  upcoming_showsq = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []

  for show in upcoming_showsq:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
    })


  data = {}
  upcoming=len(upcoming_shows)
  previous=len(past_shows)
  data['id']=artist_query.id
  data['name']=artist_query.name
  data['genres']=artist_query.genres,
  data['city']=artist_query.city,
  data['state']=artist_query.state,
  data['phone']=artist_query.phone,
  data['website_link']=artist_query.website_link,
  data['facebook_link']=artist_query.facebook_link
  data['seeking_venue']=artist_query.seeking_venue
  data['seeking_description']=artist_query.seeking_description
  data['image_link']=artist_query.image_link
  data['past_shows']=past_shows
  data['upcoming_shows']=upcoming_shows
  data['past_shows_count']=previous
  data['upcoming_shows_count']=upcoming
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # data1={
    # "id": 4,
    # "name": "Guns N Petals",
    # "genres": ["Rock n Roll"],
    # "city": "San Francisco",
    # "state": "CA",
    # "phone": "326-123-5000",
    # "website": "https://www.gunsnpetalsband.com",
    # "facebook_link": "https://www.facebook.com/GunsNPetals",
    # "seeking_venue": True,
    # "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    # # "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    # "past_shows": [{
      # "venue_id": 1,
      # "venue_name": "The Musical Hop",
      # # "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      # "start_time": "2019-05-21T21:30:00.000Z"
    # }],
    # "upcoming_shows": [],
    # "past_shows_count": 1,
    # "upcoming_shows_count": 0,
  # }
  # data2={
    # "id": 5,
    # "name": "Matt Quevedo",
    # "genres": ["Jazz"],
    # "city": "New York",
    # "state": "NY",
    # "phone": "300-400-5000",
    # "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    # "seeking_venue": False,
    # # "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    # "past_shows": [{
      # "venue_id": 3,
      # "venue_name": "Park Square Live Music & Coffee",
      # # "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      # "start_time": "2019-06-15T23:00:00.000Z"
    # }],
    # "upcoming_shows": [],
    # "past_shows_count": 1,
    # "upcoming_shows_count": 0,
  # }
  # data3={
    # "id": 6,
    # "name": "The Wild Sax Band",
    # "genres": ["Jazz", "Classical"],
    # "city": "San Francisco",
    # "state": "CA",
    # "phone": "432-325-5432",
    # "seeking_venue": False,
    # # "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    # "past_shows": [],
    # "upcoming_shows": [{
      # "venue_id": 3,
      # "venue_name": "Park Square Live Music & Coffee",
      # # "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      # "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
      # "venue_id": 3,
      # "venue_name": "Park Square Live Music & Coffee",
      # # "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      # "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
      # "venue_id": 3,
      # "venue_name": "Park Square Live Music & Coffee",
      # # "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      # "start_time": "2035-04-15T20:00:00.000Z"
    # }],
    # "past_shows_count": 0,
    # "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  art = db.session.query(Artist).filter(Artist.id==artist_id).first()
  if art != '': 
    form.name.data = art.name
    form.city.data = art.city
    form.state.data = art.state
    form.phone.data = art.phone
    form.genres.data = art.genres
    form.facebook_link.data = art.facebook_link
    form.image_link.data = art.image_link
    form.website_link.data = art.website_link
    form.seeking_venue.data = art.seeking_venue
    form.seeking_description.data = art.seeking_description
  # artist={
    # "id": 4,
    # "name": "Guns N Petals",
    # "genres": ["Rock n Roll"],
    # "city": "San Francisco",
    # "state": "CA",
    # "phone": "326-123-5000",
    # "website": "https://www.gunsnpetalsband.com",
    # "facebook_link": "https://www.facebook.com/GunsNPetals",
    # "seeking_venue": True,
    # "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    # # "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=art)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error=False  
  art = db.session.query(Artist).get(artist_id)

  try: 
    art.name = request.form['name']
    art.city = request.form['city']
    art.state = request.form['state']
    art.phone = request.form['phone']
    art.genres = request.form.getlist('genres')
    art.image_link = request.form['image_link']
    art.facebook_link = request.form['facebook_link']
    art.website_link = request.form['website_link']
    art.seeking_venue = True if 'seeking_venue' in request.form else False 
    art.seeking_description = request.form['seeking_description']

    db.session.commit()
  except: 
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()

  if error: 
    flash('An error occurred. Artist could not be changed.')
  else: 
    flash('Artist was successfully updated!')
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=db.session.query(Venue).get(venue_id)

  if venue != '': 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
  # venue={
    # "id": 1,
    # "name": "The Musical Hop",
    # "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    # "address": "1015 Folsom Street",
    # "city": "San Francisco",
    # "state": "CA",
    # "phone": "123-123-1234",
    # "website": "https://www.themusicalhop.com",
    # "facebook_link": "https://www.facebook.com/TheMusicalHop",
    # "seeking_talent": True,
    # "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    # # "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False  
  venue =db.session.query(Venue).get(venue_id)

  try: 
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash(f'An error occurred. Venue could not be changed.')
  if not error: 
    flash(f'Venue was successfully updated!')
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    name = request.form['name']
    city =request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres =request.form.getlist('genres')
    facebook_link =request.form['facebook_link']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    seeking_venue =True if 'seeking_venue' in request.form else False
    seeking_description= request.form['seeking_description']
    artist = Artist(name=name,city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link,image_link=image_link,website_link=website_link,seeking_venue=seeking_venue,
    seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('Artist ' + request.form['name'] + ' was not successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  shows = db.session.query(Show).join(Venue).join(Artist).all()

  data = []
  for show in shows: 
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  # TODO: replace with real venues data.
  # data=[{
    # "venue_id": 1,
    # "venue_name": "The Musical Hop",
    # "artist_id": 4,
    # "artist_name": "Guns N Petals",
    # # "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    # "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
    # "venue_id": 3,
    # "venue_name": "Park Square Live Music & Coffee",
    # "artist_id": 5,
    # "artist_name": "Matt Quevedo",
    # # "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    # "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
    # "venue_id": 3,
    # "venue_name": "Park Square Live Music & Coffee",
    # "artist_id": 6,
    # "artist_name": "The Wild Sax Band",
    # # "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    # "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
    # "venue_id": 3,
    # "venue_name": "Park Square Live Music & Coffee",
    # "artist_id": 6,
    # "artist_name": "The Wild Sax Band",
    # # "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    # "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
    # "venue_id": 3,
    # "venue_name": "Park Square Live Music & Coffee",
    # "artist_id": 6,
    # "artist_name": "The Wild Sax Band",
    # # "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    # "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  if not error:
    flash('Show was successfully listed!')
  else:
    flash('An error occurred. Show could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

