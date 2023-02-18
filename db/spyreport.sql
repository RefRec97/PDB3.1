-- Table: public.spyreport

-- DROP TABLE IF EXISTS public.spyreport;

CREATE TABLE IF NOT EXISTS public.spyreport
(
    "dbKey" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    "reportId" bigint,
    "playerId" integer NOT NULL,
    type smallint,
    galaxy smallint,
    system smallint,
    "position" smallint,
    metal bigint,
    crystal bigint,
    deuterium bigint,
    kt bigint,
    gt bigint,
    lj bigint,
    sj bigint,
    xer bigint,
    ss bigint,
    kolo bigint,
    rec bigint,
    spio bigint,
    b bigint,
    sats bigint,
    z bigint,
    rip bigint,
    sxer bigint,
    rak bigint,
    ll bigint,
    sl bigint,
    gauss bigint,
    ion bigint,
    plas bigint,
    klsk smallint,
    grsk smallint,
    simu text COLLATE pg_catalog."default",
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT spyreport_pkey PRIMARY KEY ("dbKey"),
    CONSTRAINT report_id_unique UNIQUE ("reportId")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.spyreport
    OWNER to poll;

GRANT TRUNCATE, TRIGGER ON TABLE public.spyreport TO "pdb-admin";

GRANT DELETE ON TABLE public.spyreport TO "pdb-overquota";

GRANT SELECT ON TABLE public.spyreport TO "pdb-ro";

GRANT UPDATE, DELETE, INSERT, REFERENCES ON TABLE public.spyreport TO "pdb-rw";

GRANT ALL ON TABLE public.spyreport TO poll;