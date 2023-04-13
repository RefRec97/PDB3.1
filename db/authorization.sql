-- Table: public.authorization

-- DROP TABLE IF EXISTS public."authorization";

CREATE TABLE IF NOT EXISTS bot."authorization"
(
    "dbKey" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    "userId" text COLLATE pg_catalog."default" NOT NULL,
    "roleId" integer NOT NULL,
    username text COLLATE pg_catalog."default",
    CONSTRAINT authorization_pkey PRIMARY KEY ("dbKey"),
    CONSTRAINT "userId_unique" UNIQUE ("userId")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."authorization"
    OWNER to poll;

GRANT TRUNCATE, TRIGGER ON TABLE public."authorization" TO "pdb-admin";

GRANT DELETE ON TABLE public."authorization" TO "pdb-overquota";

GRANT SELECT ON TABLE public."authorization" TO "pdb-ro";

GRANT UPDATE, DELETE, INSERT, REFERENCES ON TABLE public."authorization" TO "pdb-rw";

GRANT ALL ON TABLE public."authorization" TO poll;