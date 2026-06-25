CREATE TABLE "ai_chatbot"."PolicyUpload" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"policyId" text NOT NULL,
	"docName" text NOT NULL,
	"category" text,
	"title" text NOT NULL,
	"owner" text,
	"version" text,
	"effectiveDate" text,
	"reviewDate" text,
	"content" text NOT NULL,
	"sourceFilename" text,
	"uploadedBy" text NOT NULL,
	"createdAt" timestamp DEFAULT now() NOT NULL,
	"updatedAt" timestamp DEFAULT now() NOT NULL,
	CONSTRAINT "PolicyUpload_policyId_unique" UNIQUE("policyId")
);
--> statement-breakpoint
-- Lakebase Change Data Feed (wal2delta) requires full row images to build the
-- change history that syncs down to the Delta policy table.
ALTER TABLE "ai_chatbot"."PolicyUpload" REPLICA IDENTITY FULL;
