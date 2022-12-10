-- Table: pdb3.authorization

-- DROP TABLE IF EXISTS pdb3."authorization";

CREATE TABLE IF NOT EXISTS pdb3."authorization"
(
    "dbKey" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    "userId" text COLLATE pg_catalog."default" NOT NULL,
    "roleId" integer NOT NULL,
    CONSTRAINT authorization_pkey PRIMARY KEY ("dbKey"),
    CONSTRAINT "userId_unique" UNIQUE ("userId")
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS pdb3."authorization"
    OWNER to pi;