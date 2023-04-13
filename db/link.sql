-- Table: public.link

-- DROP TABLE IF EXISTS public.link;

CREATE TABLE IF NOT EXISTS bot.link
(
    "dbKey" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    "playerId" integer,
    "discordId" text COLLATE pg_catalog."default",
    "discordName" text COLLATE pg_catalog."default",
    CONSTRAINT link_pkey PRIMARY KEY ("dbKey"),
    CONSTRAINT "discordId_unique" UNIQUE ("discordId")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.link
    OWNER to poll;

GRANT TRUNCATE, TRIGGER ON TABLE public.link TO "pdb-admin";

GRANT DELETE ON TABLE public.link TO "pdb-overquota";

GRANT SELECT ON TABLE public.link TO "pdb-ro";

GRANT UPDATE, DELETE, INSERT, REFERENCES ON TABLE public.link TO "pdb-rw";

GRANT ALL ON TABLE public.link TO poll;