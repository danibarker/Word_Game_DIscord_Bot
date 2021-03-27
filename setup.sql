BEGIN TRANSACTION;
DROP TABLE IF EXISTS "matches";
CREATE TABLE IF NOT EXISTS "matches" (
	"id"	integer,
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "players";
CREATE TABLE IF NOT EXISTS "players" (
	"id"	integer,
	"first_name"	varchar(50),
	"last_name"	varchar(50),
	"discord"	varchar(50),
	"isc"	varchar(50),
	"abbreviation"	VARCHAR(50) DEFAULT NULL,
	"rating"	INTEGER,
	"rung"	INTEGER,
	"full_name"	VARCHAR(50) DEFAULT NULL,
	"current_opponent"	INTEGER,
	FOREIGN KEY("current_opponent") REFERENCES "players"("id"),
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "pairing_methods";
CREATE TABLE IF NOT EXISTS "pairing_methods" (
	"id"	INTEGER,
	"name"	VARCHAR(50),
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "events";
CREATE TABLE IF NOT EXISTS "events" (
	"id"	INTEGER,
	"date"	DATE UNIQUE,
	"pairing_method"	INTEGER,
	FOREIGN KEY("pairing_method") REFERENCES "pairing_methods"("id"),
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "results";
CREATE TABLE IF NOT EXISTS "results" (
	"id"	integer,
	"score_1"	INTEGER,
	"score_2"	INTEGER,
	"round"	INTEGER,
	"event_id"	INTEGER,
	"group_id"	INTEGER,
	"player1"	INTEGER,
	"player2"	INTEGER,
	FOREIGN KEY("event_id") REFERENCES "events"("id"),
	FOREIGN KEY("group_id") REFERENCES "groups"("id"),
	FOREIGN KEY("player1") REFERENCES "players"("id"),
	FOREIGN KEY("player2") REFERENCES "players"("id"),
	PRIMARY KEY("id"),
	UNIQUE("player1","player2","round")
);
DROP TABLE IF EXISTS "event_attendees";
CREATE TABLE IF NOT EXISTS "event_attendees" (
	"id"	integer,
	"player_id"	integer,
	"event_id"	integer,
	"bye"	TINYINT,
	FOREIGN KEY("event_id") REFERENCES "events"("id"),
	FOREIGN KEY("player_id") REFERENCES "players"("id"),
	PRIMARY KEY("id"),
	UNIQUE("player_id","event_id")
);
DROP TABLE IF EXISTS "groups";
CREATE TABLE IF NOT EXISTS "groups" (
	"id"	INTEGER,
	"event_id"	INTEGER,
	"group_number"	INTEGER,
	"round_number"	INTEGER,
	FOREIGN KEY("event_id") REFERENCES "events"("id"),
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "player_groups";
CREATE TABLE IF NOT EXISTS "player_groups" (
	"id"	integer,
	"group_id"	INTEGER,
	"player_id"	INTEGER,
	"event_id"	INTEGER,
	FOREIGN KEY("group_id") REFERENCES "groups"("id"),
	FOREIGN KEY("player_id") REFERENCES "players"("id"),
	FOREIGN KEY("event_id") REFERENCES "events"("id"),
	PRIMARY KEY("id"),
	UNIQUE("group_id","player_id")
);

INSERT INTO "pairing_methods" ("id","name") VALUES (1,'Open 5 Rounds'),
 (2,'Ladder 3 Rounds');
COMMIT;