-- Table: pdb3.stats

-- DROP TABLE IF EXISTS pdb3.stats;

CREATE TABLE IF NOT EXISTS pdb3.stats
(
    "dbKey" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    rank integer,
    score bigint,
    "researchRank" integer,
    "researchScore" bigint,
    "buildingRank" integer,
    "buildingScore" bigint,
    "defensiveRank" integer,
    "defensiveScore" bigint,
    "fleetRank" integer,
    "fleetScore" bigint,
    "battlesWon" bigint,
    "battlesLost" bigint,
    "battlesDraw" bigint,
    "debrisMetal" bigint,
    "debrisCrystal" bigint,
    "unitsDestroyed" bigint,
    "unitsLost" bigint,
    "playerId" integer NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT stats_pkey PRIMARY KEY ("dbKey")
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS pdb3.stats
    OWNER to pi;