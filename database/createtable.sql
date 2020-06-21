CREATE TABLE mentorAPI.public.profiles (
	id text,
	textdirection text,
	location text,
	username text,
	displayname text,
	languages text[],
	contact jsonb,
	keywords text[],
	about text,
	available bool
);
