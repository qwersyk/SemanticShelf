-- Additive migration: preserve original records and E5 vectors for rollback/genres.
BEGIN;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE TABLE IF NOT EXISTS semanticshelf.catalog_run (
 id text PRIMARY KEY, budget_usd numeric(12,6) NOT NULL CHECK(budget_usd > 0),
 created_at timestamptz NOT NULL DEFAULT now(), notes text NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS semanticshelf.catalog_request (
 request_hash text PRIMARY KEY, run_id text NOT NULL REFERENCES semanticshelf.catalog_run(id),
 model text NOT NULL, purpose text NOT NULL, status text NOT NULL,
 reserved_usd numeric(12,6) NOT NULL, charged_usd numeric(12,6),
 usage jsonb, response jsonb, error_code text,
 created_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz
);
ALTER TABLE semanticshelf.catalog_request ADD COLUMN IF NOT EXISTS book_ids bigint[] NOT NULL DEFAULT '{}';
CREATE TABLE IF NOT EXISTS semanticshelf.book_description_version (
 id bigserial PRIMARY KEY, book_id bigint NOT NULL REFERENCES semanticshelf.book(id),
 description_de text NOT NULL CHECK(length(btrim(description_de)) > 0),
 basis text NOT NULL CHECK(basis IN ('model_knowledge','metadata_only','source_backed','manual')),
 confidence smallint NOT NULL CHECK(confidence BETWEEN 0 AND 3),
 needs_review boolean NOT NULL, review_reason text NOT NULL,
 topics jsonb NOT NULL DEFAULT '[]', sources jsonb NOT NULL DEFAULT '[]',
 model text NOT NULL, prompt_version text NOT NULL, metadata_hash text NOT NULL,
 request_hash text REFERENCES semanticshelf.catalog_request(request_hash),
 created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(book_id, request_hash)
);
ALTER TABLE semanticshelf.book_description_version ADD COLUMN IF NOT EXISTS metadata_snapshot jsonb NOT NULL DEFAULT '{}';
CREATE TABLE IF NOT EXISTS semanticshelf.book_enrichment (
 book_id bigint PRIMARY KEY REFERENCES semanticshelf.book(id),
 version_id bigint NOT NULL REFERENCES semanticshelf.book_description_version(id),
 manual_locked boolean NOT NULL DEFAULT false,
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS semanticshelf.book_search_document (
 book_id bigint PRIMARY KEY REFERENCES semanticshelf.book(id),
 version_id bigint NOT NULL REFERENCES semanticshelf.book_description_version(id),
 model text NOT NULL, dimensions integer NOT NULL CHECK(dimensions=1536),
 document_version text NOT NULL, metadata_hash text NOT NULL,
 content_hash text NOT NULL, metadata_content_hash text NOT NULL,
 content_text text NOT NULL, metadata_text text NOT NULL,
 title_normalized text NOT NULL, authors_text text NOT NULL,
 isbn_normalized text NOT NULL, work_key text NOT NULL,
 search_tsv tsvector GENERATED ALWAYS AS
   (to_tsvector('german'::regconfig, content_text)) STORED,
 embedding_vector public.vector(1536) NOT NULL,
 metadata_vector public.vector(1536) NOT NULL,
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS book_search_document_tsv_idx
 ON semanticshelf.book_search_document USING gin(search_tsv);
CREATE INDEX IF NOT EXISTS book_search_document_title_idx
 ON semanticshelf.book_search_document USING gin(title_normalized public.gin_trgm_ops);
CREATE INDEX IF NOT EXISTS description_version_review_idx
 ON semanticshelf.book_description_version(needs_review, confidence, book_id);
CREATE INDEX IF NOT EXISTS catalog_request_run_idx ON semanticshelf.catalog_request(run_id);
CREATE INDEX IF NOT EXISTS catalog_request_books_idx ON semanticshelf.catalog_request USING gin(book_ids);
CREATE OR REPLACE VIEW semanticshelf.catalog_review_queue AS
 SELECT b.id, b.title, b.isbn13, b.year, v.description_de, v.basis,
        v.confidence, v.needs_review, v.review_reason, v.topics, v.sources,
        v.model, v.prompt_version, v.id AS version_id, e.manual_locked, e.updated_at
 FROM semanticshelf.book b JOIN semanticshelf.book_enrichment e ON e.book_id=b.id
 JOIN semanticshelf.book_description_version v ON v.id=e.version_id;

-- Direct edits through SQL/admin tools are also protected from future AI overwrites.
CREATE OR REPLACE FUNCTION semanticshelf.capture_manual_description() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE previous_id bigint; previous_hash text; new_id bigint;
BEGIN
 IF current_setting('semanticshelf.enrichment_writer',true)='pipeline' THEN RETURN NEW; END IF;
 SELECT e.version_id,v.metadata_hash INTO previous_id,previous_hash
 FROM semanticshelf.book_enrichment e JOIN semanticshelf.book_description_version v ON v.id=e.version_id
 WHERE e.book_id=NEW.id;
 IF previous_id IS NOT NULL AND length(btrim(coalesce(NEW.description,'')))>0 THEN
   INSERT INTO semanticshelf.book_description_version
    (book_id,description_de,basis,confidence,needs_review,review_reason,model,prompt_version,metadata_hash,metadata_snapshot)
   SELECT NEW.id,NEW.description,'manual',3,false,'Manuell bearbeitet.','manual','manual',previous_hash,metadata_snapshot
   FROM semanticshelf.book_description_version WHERE id=previous_id
   RETURNING id INTO new_id;
   UPDATE semanticshelf.book_enrichment SET version_id=new_id,manual_locked=true,updated_at=now() WHERE book_id=NEW.id;
   DELETE FROM semanticshelf.book_search_document WHERE book_id=NEW.id;
 END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS capture_manual_description ON semanticshelf.book;
CREATE TRIGGER capture_manual_description AFTER UPDATE OF description ON semanticshelf.book
 FOR EACH ROW WHEN (OLD.description IS DISTINCT FROM NEW.description)
 EXECUTE FUNCTION semanticshelf.capture_manual_description();
COMMIT;
