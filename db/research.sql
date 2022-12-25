-- Table: public.research

-- DROP TABLE IF EXISTS public.research;

CREATE TABLE IF NOT EXISTS public.research
(
    "dbKey" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    "playerId" integer,
    weapon smallint,
    shield smallint,
    armor smallint,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT research_pkey PRIMARY KEY ("dbKey"),
    CONSTRAINT player_unique UNIQUE ("playerId")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.research
    OWNER to poll;

GRANT TRUNCATE, TRIGGER ON TABLE public.research TO "pdb-admin";

GRANT DELETE ON TABLE public.research TO "pdb-overquota";

GRANT SELECT ON TABLE public.research TO "pdb-ro";

GRANT UPDATE, DELETE, INSERT, REFERENCES ON TABLE public.research TO "pdb-rw";

GRANT ALL ON TABLE public.research TO poll;