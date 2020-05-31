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
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('homepage'))

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