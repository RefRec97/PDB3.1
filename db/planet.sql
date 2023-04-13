-- Table: public.planet

-- DROP TABLE IF EXISTS public.planet;

CREATE TABLE IF NOT EXISTS bot.planet
(
    "dbKey" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    "playerId" integer,
    galaxy smallint,
    system smallint,
    "position" smallint,
    moon boolean,
    "sensorPhalanx" smallint,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    jumpgate smallint,
    CONSTRAINT planet_pkey PRIMARY KEY ("dbKey"),
    CONSTRAINT position_unique UNIQUE (galaxy, system, "position")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.planet
    OWNER to poll;

GRANT TRUNCATE, TRIGGER ON TABLE public.planet TO "pdb-admin";

GRANT DELETE ON TABLE public.planet TO "pdb-overquota";

GRANT SELECT ON TABLE public.planet TO "pdb-ro";

GRANT UPDATE, DELETE, INSERT, REFERENCES ON TABLE public.planet TO "pdb-rw";

GRANT ALL ON TABLE public.planet TO poll;