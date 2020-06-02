from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)

config = yaml.load(open('config.yaml'))

app.secret_key = 'mddafafafadewdweqdw2dqdqdqwdqw558d5qdqdq'
app.config['MYSQL_HOST'] = config['mysql_host']
app.config['MYSQL_USER'] = config['mysql_user']
app.config['MYSQL_PASSWORD'] = config['mysql_password']
app.config['MYSQL_DB'] = config['mysql_db']

mysql = MySQL(app)

@app.route('/insertalbum/<string:artist_id>', methods = ['POST'])
def insertalbum(artist_id):
    if request.method == 'POST':
        flash('Album is added successfully!')
        title = request.form['title']
        genre = request.form['genre']
        song_title = request.form['songname']
        cur = mysql.connection.cursor()
        cur.execute('insert into album (genre, title, artist_id) values (%s, %s, %s)', [genre, title, artist_id])
        mysql.connection.commit()
        cur.execute("SELECT last_insert_id()")
        album_id = cur.fetchall()[0]
        cur.execute('insert into song (title, album_id) values (%s, %s)', [song_title, album_id])  
        mysql.connection.commit()
        cur.execute("SELECT last_insert_id()")
        song_id = cur.fetchall()[0]
        cur.execute('insert into songs_artists (artist_id, song_id) values (%s, %s)', [artist_id, song_id])  
        mysql.connection.commit()
        return redirect(url_for('artisthome', artist_id = artist_id))

@app.route('/insertsong/<string:artist_id>/<string:album_id>', methods = ['POST'])
def insertsong(artist_id, album_id):
    if request.method == 'POST':
        flash('Song is added successfully!')
        title = request.form['title']
        cur = mysql.connection.cursor()
        cur.execute('insert into song (title, album_id) values (%s, %s)', [title, album_id])  
        mysql.connection.commit()
        cur.execute("SELECT last_insert_id()")
        song_id = cur.fetchall()[0]
        cur.execute('insert into songs_artists (artist_id, song_id) values (%s, %s)', [artist_id, song_id])  
        mysql.connection.commit()
        return redirect(url_for('managesongs', artist_id = artist_id, album_id = album_id))

@app.route('/updatesong/<string:artist_id>/<string:album_id>', methods = ['POST'])
def updatesong(artist_id, album_id):
    if request.method == 'POST':
        flash('Updated song successfully!')
        song_id = request.form['id']
        title = request.form['title']
        cur = mysql.connection.cursor()
        cur.execute('update song set title = %s where song_id = %s', [title, song_id])
        mysql.connection.commit()
        return redirect(url_for('managesongs', artist_id = artist_id, album_id = album_id))

@app.route('/searchsong', methods = ['POST'])
def searchsong():
    if request.method == 'POST':
        keyword = request.form['keyword']
        cur = mysql.connection.cursor()
        cur.execute("select * from song where title like " + "'%" + keyword + "%'")
        result = cur.fetchall()
        return render_template('search_result.html', result = result)

@app.route('/addartist/<string:artist_id>/<string:album_id>', methods = ['POST'])
def addartist(artist_id, album_id):
    if request.method == 'POST':
        song_id = request.form['id']
        artist_id_add = request.form['col_id']
        cur = mysql.connection.cursor()
        cur.execute("select * from artist where artist_id = %s", [artist_id_add])
        artist_data = cur.fetchall()
        if len(artist_data) == 0:
            flash('Artist not found!')
            return redirect(url_for('managesongs', artist_id = artist_id, album_id = album_id))
        cur.execute('select * from songs_artists where song_id = %s and artist_id = %s', [song_id, artist_id_add])
        temp = cur.fetchall()
        if len(temp) == 1:
            flash('Artist has already been added to that song.')
            return redirect(url_for('managesongs', artist_id = artist_id, album_id = album_id))
        flash('Added artist successfully')
        cur.execute('insert into songs_artists (artist_id, song_id) values (%s, %s)', [artist_id_add, song_id])
        mysql.connection.commit()
        return redirect(url_for('managesongs', artist_id = artist_id, album_id = album_id))

@app.route('/updatealbum/<string:artist_id>', methods = ['POST'])
def updatealbum(artist_id):
    if request.method == 'POST':
        flash('Updated album successfully!')
        album_id = request.form['id']
        title = request.form['title']
        genre = request.form['genre']
        cur = mysql.connection.cursor()
        cur.execute('update album set title = %s, genre = %s where album_id = %s', [title, genre, album_id])
        mysql.connection.commit()
        return redirect(url_for('artisthome', artist_id = artist_id))

@app.route('/deletesong/<string:artist_id>/<string:album_id>/<string:song_id>', methods = ['GET'])
def deletesong(artist_id, album_id, song_id):
    if request.method == 'GET':
        flash('Deleted song successfully!')
        cur = mysql.connection.cursor()
        cur.execute('delete from song where song_id = %s', [song_id])
        mysql.connection.commit()
        return redirect(url_for('managesongs', artist_id = artist_id, album_id = album_id))

@app.route('/deletealbum/<string:artist_id>/<string:album_id>', methods = ['GET'])
def deletealbum(artist_id, album_id):
    if request.method == 'GET':
        flash('Deleted album successfully!')
        cur = mysql.connection.cursor()
        cur.execute('delete from album where album_id = %s', [album_id])
        mysql.connection.commit()
        return redirect(url_for('artisthome', artist_id = artist_id))

@app.route('/managesongs/<string:artist_id>/<string:album_id>')
def managesongs(artist_id, album_id):
    cur = mysql.connection.cursor()
    cur.execute('select * from artist where artist_id = %s', [artist_id])
    artist_data = cur.fetchall()
    cur.execute('select * from album where album_id = %s', [album_id])
    album_data = cur.fetchall()
    cur.execute('select * from song where album_id = %s', [album_id])
    song_data = cur.fetchall()
    return render_template('song_artist.html', artist = artist_data, album = album_data, song = song_data)

@app.route('/like/<string:user_id>/<string:song_id>')
def like(user_id, song_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM songs_likes where song_id = %s and listener_id = %s", [song_id, user_id])
    result = cur.fetchall()
    if str(result[0][0]) == "0":
        cur.execute("INSERT INTO songs_likes (listener_id, song_id) values(%s, %s)", [user_id, song_id])
        mysql.connection.commit()
        flash("Liked Song!")
    else:
        flash("You cannot like the same song twice")
    cur.close()
    return redirect(url_for('homepage', user = user_id))


@app.route('/albumsubs/<string:user_id>/<string:album_id>')
def albumsubs(user_id, album_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM album_likes where album_id = %s and listener_id = %s", [album_id, user_id])
    result = cur.fetchall()
    if str(result[0][0]) == "0":
        cur.execute("INSERT INTO album_likes (listener_id, album_id) values(%s, %s)", [user_id, album_id])
        mysql.connection.commit()
        flash("Liked Album!")
    else:
        flash("You cannot like the same album twice")
    cur.close()
    return redirect(url_for('homepage', user = user_id))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/artist/<string:artist_id>')
def artist_page(artist_id):
    cur = mysql.connection.cursor()
    cur.execute("select * from artist where artist_id = %s", [artist_id])
    artist_data = cur.fetchall()
    cur.execute("select album_id, genre, title from album where artist_id = %s", [artist_id])
    album_data = cur.fetchall()
    cur.execute("select song.song_id, song.title, album.title, (SELECT COUNT(*) FROM songs_likes where song_id = song.song_id) as likes from song "+
        "left join album  on song.album_id = album.album_id " +
        "left join songs_artists on song.song_id = songs_artists.song_id where songs_artists.artist_id = %s order by likes desc", [artist_id])
    song_data = cur.fetchall()
    return render_template("artist.html", artist = artist_data, album = album_data, song = song_data)

@app.route('/album/<string:album_id>')
def album_page(album_id):
    cur = mysql.connection.cursor()
    cur.execute("select song.song_id, song.title from song where album_id = %s", [album_id])
    song_data = cur.fetchall()
    cur.execute("select * from album where album_id = %s", [album_id])
    album_data = cur.fetchall()
    return render_template("album.html", album = album_data, song = song_data)

@app.route('/home')
def homepage():
    cur = mysql.connection.cursor()
    user_id = request.args['user']
    cur.execute("SELECT * FROM listener where listener_id = %s", [user_id])
    usr_data = cur.fetchall()
    cur.execute("SELECT song.song_id, song.title, album.title, (SELECT COUNT(*) FROM songs_likes where song_id = song.song_id) as likes, (SELECT COUNT(*) FROM songs_likes where song_id = song.song_id and listener_id = %s) as liked FROM dbtify.song left join dbtify.album on song.album_id = album.album_id order by likes desc", [user_id])
    song_data = cur.fetchall()
    cur.execute("select album.album_id, album.genre, album.title, artist.firstname, artist.lastname, (Select Count(*) from album_likes where album_id = album.album_id) as likes from album left join artist on album.artist_id = artist.artist_id order by likes desc")
    album_data = cur.fetchall()
    cur.execute("SELECT artist.artist_id, artist.firstname, artist.lastname, (Select Count(*) from song "+
                "left join songs_artists on songs_artists.song_id = song.song_id " +
                "join songs_likes on song.song_id = songs_likes.song_id " +
                "where artist_id = artist.artist_id) as total_likes from artist order by total_likes desc")
    artist_data = cur.fetchall()
    cur.execute("select * from listener")
    listener_data = cur.fetchall()
    return render_template('home.html', user = usr_data, song = song_data, album = album_data, artist = artist_data, listener = listener_data)

@app.route('/listener/<string:listener_id>')
def listener_page(listener_id):
    cur = mysql.connection.cursor()
    cur.execute("select album.album_id, album.genre, album.title from album " +
        "left join album_likes on album.album_id = album_likes.album_id " +
        "where album_likes.listener_id = %s", [listener_id])
    album_data = cur.fetchall()
    cur.execute("select song.song_id, song.title, album.title from song left join album on song.album_id = album.album_id " +
        "left join songs_likes on song.song_id = songs_likes.song_id where songs_likes.listener_id = %s", [listener_id])
    song_data = cur.fetchall()
    cur.execute("select * from listener where listener_id = %s", [listener_id])
    listener_data = cur.fetchall()
    return render_template('listener.html', listener = listener_data, album = album_data, song = song_data)

@app.route('/artistlog', methods = ['POST'])
def artistlog():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM artist where firstname = %s and lastname = %s", [name, surname])
        artist_data = cur.fetchall()
        if len(artist_data) == 0:
            flash("Account not found!")
            return render_template('index.html')
        else:
            artist_id = artist_data[0][0]
            return redirect(url_for('artisthome', artist_id = artist_id))

@app.route('/artisthome')
def artisthome():
    artist_id = request.args['artist_id']
    cur = mysql.connection.cursor()
    cur.execute('select * from artist where artist_id = %s', [artist_id])
    artist_data = cur.fetchall()
    cur.execute("select album_id, genre, title from album where artist_id = %s", [artist_id])
    album_data = cur.fetchall()
    cur.execute("select song.song_id, song.title, album.title from song "+
        "left join album on song.album_id = album.album_id " +
        "left join songs_artists on song.song_id = songs_artists.song_id where songs_artists.artist_id = %s", [artist_id])
    song_data = cur.fetchall()
    return render_template("home_artist.html", artist = artist_data, album = album_data, song = song_data)


@app.route('/artistregister', methods = ['POST'])
def artistregister():
    if request.method == 'POST':
        flash('Registered Successfully')
        name = request.form['name']
        surname = request.form['surname']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO artist (firstname, lastname) values (%s, %s)", [name, surname])
        mysql.connection.commit()
        return redirect(url_for('index'))

@app.route('/login', methods = ['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM listener where username = %s", [username])
        usr_data = cur.fetchall()
        if len(usr_data) == 0:
            flash("Account not found!")
            return render_template('index.html')
        else:
            return redirect(url_for('homepage', user = usr_data[0][0]))
        #return redirect(url_for('homepage', user = usr_data, song = song_data))

@app.route('/register', methods = ['POST'])
def register():
    if request.method == 'POST':
        flash('Registered successfully')
        username = request.form['username']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO listener (username, email) values (%s, %s)", [username, email])
        mysql.connection.commit()
        return redirect(url_for('index'))


app.run(debug=True)