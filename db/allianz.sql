-- Table: pdb3.alliance

-- DROP TABLE IF EXISTS pdb3.alliance;

CREATE TABLE IF NOT EXISTS pdb3.alliance
(
    "dbKey" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    "allianceId" integer,
    "allianceName" text COLLATE pg_catalog."default",
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT allianz_pkey PRIMARY KEY ("dbKey"),
    CONSTRAINT id_name_alliance_unique UNIQUE ("allianceId", "allianceName")
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS pdb3.alliance
    OWNER to pi;