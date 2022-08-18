# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import datetime
import logging
import re
from logging import Formatter, FileHandler

import babel
import dateutil.parser
from flask import render_template, request, flash, redirect, url_for, abort, jsonify

from forms import *
# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#
from models import app, Venue, Show, db, Artist


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    return render_template('pages/venues.html', areas=venues_query())


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    search_term = request.form.get('search_term', '')
    response = search_by_name(Venue, search_term)
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    return render_template('pages/show_venue.html', venue=show_venue_query(venue_id))


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    # after successful authentication add data to database
    add_form_data(Venue, 'Venue')
    return redirect(url_for('index'))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    try:
        venue = Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Venue ' + venue.name + ' was deleted successfully.')

    except:
        # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
        db.session.rollback()
        flash('An error occurred. Venue could not be listed.')
        abort(500)
    finally:
        db.session.close()
    return redirect(url_for('index'))


# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
# clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    all_artists = Artist.query.all()
    data = []
    for artist in all_artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    response = search_by_name(Artist, search_term)
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = get_data_by_id(Artist, artist_id)
    shows_data = Show.query.filter_by(artist_id=artist_id).all()

    past_shows_data = []
    up_shows_data = []
    for show in shows_data:
        if datetime.now() > show.start_time:
            past_shows_data.append({"venue_id": show.venue.id,
                                    "venue_name": show.venue.name,
                                    "venue_image_link": show.venue.image_link,
                                    "start_time": str(show.start_time)})

        elif datetime.now() <= show.start_time:
            up_shows_data.append({"venue_id": show.venue.id,
                                  "venue_name": show.venue.name,
                                  "venue_image_link": show.venue.image_link,
                                  "start_time": str(show.start_time)})

    past_shows = past_shows_data
    up_shows = up_shows_data
    artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:],
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": up_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(up_shows),
    }
    return render_template('pages/show_artist.html', artist=artist_data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO: populate form with fields from artist with ID <artist_id>
    artist = get_data_by_id(Artist, artist_id)
    artist = artist.__dict__
    form = ArtistForm(data=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # retrieving artist from form
    update_db(Artist, artist_id, 'Artist')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>
    venue = get_data_by_id(Venue, venue_id)
    venue = venue.__dict__
    form = VenueForm(data=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # calling update db to get data from form and also update database
    update_db(Venue, venue_id, 'Venue')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    add_form_data(Artist, 'Artist')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # TODO: replace with real venues data.
    data = []
    all_shows = Show.query.all()
    for show in all_shows:
        data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')
    error_in_insert = False
    # on successful db insert, flash success
    # flash('Show was successfully listed!')
    try:
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    # form = ShowForm()
    except:
        error_in_insert = True
        db.session.rollback()
    finally:
        db.session.close()

    if error_in_insert:
        flash(f'An error occurred.  Show could not be listed.')
    else:
        flash('Show was successfully listed!')
    return render_template('pages/home.html')


# begin of helper functions

def venues_query():
    city_state = Venue.query.distinct(Venue.city, Venue.state).all()
    db_venues = Venue.query.all()
    all_venues = []
    for loc in city_state:
        my_venues = []
        temp = {"city": loc.city, "state": loc.state, "venues": []}
        for venue in db_venues:
            if venue.city == loc.city and venue.state == loc.state:
                my_venues.append({"id": venue.id, "name": venue.name,
                                  'num_upcoming_shows': Show.query.filter_by(venue_id=venue.id).count()})
        temp['venues'] = my_venues
        all_venues.append(temp)
    return all_venues


def past_shows_by_date(data):
    hold_shows = []
    for show in data.shows:
        if datetime.now() > show.start_time:
            hold_shows.append({"artist_id": show.artist.id,
                               "artist_name": show.artist.name,
                               "artist_image_link": show.artist.image_link,
                               "start_time": str(show.start_time)})
    return hold_shows


def upcoming_shows_by_date(data):
    hold_shows = []
    for show in data.shows:
        if datetime.now() <= show.start_time:
            hold_shows.append({"artist_id": show.artist.id,
                               "artist_name": show.artist.name,
                               "artist_image_link": show.artist.image_link,
                               "start_time": str(show.start_time)})
    return hold_shows


def show_venue_query(venue_id):
    venue = Venue.query.get(venue_id)
    past_shows = past_shows_by_date(venue)
    up_shows = upcoming_shows_by_date(venue)
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:],
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": up_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(up_shows),
    }
    return data


def search_by_name(table_name, search_term):
    result = table_name.query.filter(table_name.name.ilike('%' + search_term + '%')).all()
    data = []
    for v in result:
        data.append({
            "id": v.id,
            "name": v.name,
            "num_upcoming_shows": len(
                [s for s in v.shows if s.start_time > datetime.now()]),
        })
    return {
        "count": len(data),
        "data": data
    }


def get_data_by_id(data, data_id):
    db_data = data.query.get(data_id)
    if not db_data:
        return not_found_error(404)

    if data == Venue:
        return Venue(id=db_data.id, name=db_data.name, city=db_data.city, state=db_data.state, address=db_data.address,
                     phone=db_data.phone, genres=db_data.genres, seeking_talent=db_data.seeking_talent,
                     seeking_description=db_data.seeking_description, image_link=db_data.image_link,
                     website_link=db_data.website_link, facebook_link=db_data.facebook_link)
    elif data == Artist:
        return Artist(id=db_data.id, name=db_data.name, city=db_data.city, state=db_data.state, phone=db_data.phone,
                      genres=db_data.genres, seeking_venue=db_data.seeking_venue, image_link=db_data.image_link,
                      seeking_description=db_data.seeking_description, website_link=db_data.website_link,
                      facebook_link=db_data.facebook_link)


def get_form_data(form):
    data = None
    seeking_talent = None
    seeking_venue = None
    address = None
    name = request.form.get("name")
    city = request.form.get("city")
    state = request.form.get("state")
    phone = re.sub('\D', '', request.form.get("phone"))
    genres = request.form.getlist("genres")
    facebook_link = request.form.get("facebook_link")
    seeking_description = request.form.get('seeking_description')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')

    if form == Venue:
        seeking_talent = True if 'seeking_talent' in request.form else False
        address = request.form.get("address")
        data = Venue(name=name, city=city, state=state, address=address, phone=phone,
                     genres=genres, seeking_talent=seeking_talent, seeking_description=seeking_description,
                     image_link=image_link, website_link=website_link, facebook_link=facebook_link)
    elif form == Artist:
        seeking_venue = True if 'seeking_venue' in request.form else False
        data = Artist(name=name, city=city, state=state, phone=phone, genres=genres,
                      seeking_venue=seeking_venue, seeking_description=seeking_description,
                      image_link=image_link, website_link=website_link, facebook_link=facebook_link)
    return data


def add_form_data(data, object_name):
    try:
        db.session.add(get_form_data(data))
        db.session.commit()
        flash(object_name.upper() + ' ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        db.session.rollback()
        flash('An error occurred. ' + object_name.upper() + ' ' + request.form['name'] + ' could not be listed.')
        abort(500)
    finally:
        db.session.close()


def update_db(data, data_id, object_name):
    try:
        # getting data from form
        form = get_form_data(data)
        # getting data from db
        db_data = data.query.get(data_id)
        if data == Venue:
            db_data.address = form.address
            db_data.seeking_talent = form.seeking_talent
        elif data == Artist:
            db_data.seeking_venue = form.seeking_venue
        db_data.name = form.name
        db_data.city = form.city
        db_data.state = form.state
        db_data.phone = form.phone
        db_data.genres = form.genres
        db_data.seeking_description = form.seeking_description
        db_data.image_link = form.image_link
        db_data.website_link = form.website_link
        db_data.facebook_link = form.facebook_link
        db.session.commit()
        flash(object_name + ' ' + request.form['name'] + ' was successfully updated!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        db.session.rollback()
        flash('An error occurred. ' + object_name + ' ' + request.form['name'] + ' could not be updated.')
        abort(500)
    finally:
        db.session.close()


# end of helper functions

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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
