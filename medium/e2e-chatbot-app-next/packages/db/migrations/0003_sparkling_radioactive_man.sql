CREATE TABLE "ai_chatbot"."PolicyReview" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"policyId" text NOT NULL,
	"decision" varchar NOT NULL,
	"comment" text,
	"reviewer" text NOT NULL,
	"createdAt" timestamp DEFAULT now() NOT NULL
);
