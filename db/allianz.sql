-- Table: public.alliance

-- DROP TABLE IF EXISTS public.alliance;

CREATE TABLE IF NOT EXISTS bot.alliance
(
    "dbKey" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    "allianceId" integer,
    "allianceName" text COLLATE pg_catalog."default",
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT allianz_pkey PRIMARY KEY ("dbKey"),
    CONSTRAINT id_name_alliance_unique UNIQUE ("allianceId")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.alliance
    OWNER to poll;

GRANT TRUNCATE, TRIGGER ON TABLE public.alliance TO "pdb-admin";

GRANT DELETE ON TABLE public.alliance TO "pdb-overquota";

GRANT SELECT ON TABLE public.alliance TO "pdb-ro";

GRANT UPDATE, DELETE, INSERT, REFERENCES ON TABLE public.alliance TO "pdb-rw";

GRANT ALL ON TABLE public.alliance TO poll;