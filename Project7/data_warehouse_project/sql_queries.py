import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')



# DROP TABLES
staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays cascade"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES
staging_events_table_create= ("""
CREATE TABLE staging_events (
    artist VARCHAR, 
    auth VARCHAR, 
    firstName VARCHAR, 
    gender VARCHAR, 
    itemInSession VARCHAR, 
    lastName VARCHAR, 
    length VARCHAR, 
    level VARCHAR, 
    location VARCHAR, 
    method VARCHAR, 
    page VARCHAR, 
    registration VARCHAR, 
    sessionId VARCHAR, 
    song VARCHAR, 
    status VARCHAR, 
    ts VARCHAR, 
    userAgent VARCHAR, 
    userId VARCHAR 
)
""")

staging_songs_table_create = ("""
CREATE TABLE staging_songs (
    song_id VARCHAR,
    num_songs INT,
    title VARCHAR, 
    artist_name VARCHAR,
    artist_latitude FLOAT,
    year INT,
    duration FLOAT,
    artist_id VARCHAR,
    artist_longitude FLOAT,
    artist_location VARCHAR
)
    
""")

songplay_table_create = ("""
CREATE TABLE songplays (
    songplay_id INT IDENTITY(0,1)  sortkey distkey, 
    start_time TIMESTAMP NOT NULL, 
    user_id VARCHAR NOT NULL, 
    level VARCHAR, 
    song_id VARCHAR NOT NULL, 
    artist_id VARCHAR NOT NULL, 
    session_id VARCHAR, 
    location VARCHAR, 
    user_agent VARCHAR
)
""")

user_table_create = ("""
CREATE TABLE users (
    user_id VARCHAR sortkey, 
    first_name VARCHAR, 
    last_name VARCHAR, 
    gender VARCHAR, 
    level VARCHAR
)diststyle all;
""")

song_table_create = ("""
CREATE TABLE songs (
    song_id VARCHAR sortkey,
    title VARCHAR, 
    artist_id VARCHAR, 
    year INT, 
    duration FLOAT
)diststyle all;
""")

artist_table_create = ("""
CREATE TABLE artists (
    artist_id VARCHAR sortkey, 
    name VARCHAR, 
    location VARCHAR, 
    lattitude FLOAT, 
    longitude FLOAT
)diststyle all;
""")

time_table_create = ("""
CREATE TABLE time (
    start_time TIMESTAMP sortkey,
    hour INT, 
    day INT, 
    week INT, 
    month INT,
    year INT, 
    weekday INT
)diststyle all;
""")

# STAGING TABLES

staging_events_copy =  ("""
COPY staging_events 
FROM {}
CREDENTIALS 'aws_iam_role={}'
region 'us-west-2' compupdate off
FORMAT AS JSON {};
""").format(config.get('S3', 'LOG_DATA'),
            config.get('IAM_ROLE', 'ARN'),
           config.get('S3', 'LOG_JSONPATH'))


staging_songs_copy = ("""
COPY staging_songs 
FROM {}
CREDENTIALS 'aws_iam_role={}'
region 'us-west-2' compupdate off
FORMAT AS JSON 'auto' truncatecolumns;
""").format(config.get('S3', 'SONG_DATA'),
            config.get('IAM_ROLE', 'ARN'))
# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
    (SELECT distinct timestamp 'epoch' + CAST(se.ts AS BIGINT)/1000 * interval '1 second' AS start_time, se.userId, se.level, tmp.song_id, tmp.artist_id, se.sessionId, se.location, se.userAgent  FROM staging_events as se 
    INNER JOIN
        (SELECT songs.song_id, artists.artist_id, songs.title, songs.duration, artists.name FROM songs INNER JOIN artists
        on songs.artist_id = artists.artist_id) as tmp
    ON tmp.title=se.song AND tmp.name=se.artist AND tmp.duration=se.length
    WHERE se.page='NextSong'
    )
    
""")


user_table_insert = ("""
INSERT INTO users (user_id, first_name, last_name, gender, level)
    SELECT userId, firstName, lastName, gender, level FROM (select userId, firstName, lastName, gender, level , row_number() over(partition by userId order by firstName desc) as sequence from staging_events ) a where sequence =1 
""")

song_table_insert = ("""
INSERT INTO songs (song_id, title, artist_id, year, duration)
    SELECT song_id, title, artist_id, year, duration FROM (select song_id, title, artist_id, year, duration , row_number() over(partition by song_id order by title desc) as sequence from staging_songs ) a where sequence =1  
""")

artist_table_insert = ("""
INSERT INTO artists(artist_id, name, location, lattitude, longitude)
    SELECT artist_id, artist_name, artist_location, artist_latitude, artist_longitude FROM  (select artist_id, artist_name, artist_location, artist_latitude, artist_longitude, row_number() over(partition by artist_id order by artist_location desc) as sequence from staging_songs ) a where sequence =1  
""")

time_table_insert = ("""
INSERT INTO time (start_time, hour, day, week, month, year, weekday)
SELECT  distinct timestamp 'epoch' + CAST(ts AS BIGINT)/1000 * interval '1 second' AS start_time,  EXTRACT (h FROM start_time) as hour, EXTRACT (dayofyear FROM start_time) as day, EXTRACT (w FROM  start_time) as week, EXTRACT (mon FROM start_time) as month, EXTRACT (y FROM start_time) as year, 
EXTRACT (dayofweek FROM start_time) as weekday
FROM staging_events
""")


# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
