-- Table: public.planet

-- DROP TABLE IF EXISTS public.planet;

CREATE TABLE IF NOT EXISTS public.planet
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

ALTER TABLE IF EXISTS public.planet
    OWNER to poll;