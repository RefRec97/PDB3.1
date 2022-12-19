-- Table: pdb3.planet

-- DROP TABLE IF EXISTS pdb3.planet;

CREATE TABLE IF NOT EXISTS pdb3.planet
(
    "dbKey" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    "playerId" integer,
    "galaxy" smallint,
    "system" smallint,
    "position" smallint,
    "active" boolean,
    "moon" boolean,
    "sensorPhalanx" smallint,
    CONSTRAINT planet_pkey PRIMARY KEY ("dbKey"),
    CONSTRAINT position_unique UNIQUE ("galaxy", "system", "position")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS pdb3.planet
    OWNER to pi;