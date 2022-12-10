-- Table: pdb3.player

-- DROP TABLE IF EXISTS pdb3.player;

CREATE TABLE IF NOT EXISTS pdb3.player
(
    "dbKey" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    "playerId" integer NOT NULL,
    "playerName" text COLLATE pg_catalog."default",
    "playerUniverse" smallint,
    "playerGalaxy" smallint,
    "allianceId" integer,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT player_pkey PRIMARY KEY ("dbKey"),
    CONSTRAINT id_name_player_unique UNIQUE ("playerId", "playerName")
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS pdb3.player
    OWNER to pi;