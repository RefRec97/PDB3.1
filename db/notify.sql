-- Table: public.notify

-- DROP TABLE IF EXISTS public.notify;

CREATE TABLE IF NOT EXISTS bot.notify
(
    "dbKey" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    id text COLLATE pg_catalog."default",
    type character(1) COLLATE pg_catalog."default",
    "guildId" text COLLATE pg_catalog."default",
    "playerId" integer,
    CONSTRAINT notify_pkey PRIMARY KEY ("dbKey"),
    CONSTRAINT id_type_unique UNIQUE (id, type)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.notify
    OWNER to poll;

GRANT TRUNCATE, TRIGGER ON TABLE public.notify TO "pdb-admin";

GRANT DELETE ON TABLE public.notify TO "pdb-overquota";

GRANT SELECT ON TABLE public.notify TO "pdb-ro";

GRANT UPDATE, DELETE, INSERT, REFERENCES ON TABLE public.notify TO "pdb-rw";

GRANT ALL ON TABLE public.notify TO poll;