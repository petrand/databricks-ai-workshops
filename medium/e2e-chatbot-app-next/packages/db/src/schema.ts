import type { InferSelectModel } from 'drizzle-orm';
import {
  varchar,
  timestamp,
  json,
  jsonb,
  uuid,
  text,
  boolean,
  pgSchema,
  primaryKey,
} from 'drizzle-orm/pg-core';
import type { LanguageModelV3Usage } from '@ai-sdk/provider';
import type { User as SharedUser } from '@chat-template/utils';

const schemaName = 'ai_chatbot';
const customSchema = pgSchema(schemaName);

// Helper function to create table with proper schema handling
// Use the schema object for proper drizzle-kit migration generation
const createTable = customSchema.table;

export const user = createTable('User', {
  id: text('id').primaryKey().notNull(),
  email: varchar('email', { length: 64 }).notNull(),
  // Password removed - using Databricks SSO authentication
});

export type User = SharedUser;

export const chat = createTable('Chat', {
  id: uuid('id').primaryKey().notNull().defaultRandom(),
  createdAt: timestamp('createdAt').notNull(),
  title: text('title').notNull(),
  userId: text('userId').notNull(),
  visibility: varchar('visibility', { enum: ['public', 'private'] })
    .notNull()
    .default('private'),
  lastContext: jsonb('lastContext').$type<LanguageModelV3Usage | null>(),
});

export type Chat = InferSelectModel<typeof chat>;

export const message = createTable('Message', {
  id: uuid('id').primaryKey().notNull().defaultRandom(),
  chatId: uuid('chatId')
    .notNull()
    .references(() => chat.id),
  role: varchar('role').notNull(),
  parts: json('parts').notNull(),
  attachments: json('attachments').notNull(),
  createdAt: timestamp('createdAt').notNull(),
  traceId: text('traceId'), // MLflow trace ID for feedback submission
});

export type DBMessage = InferSelectModel<typeof message>;

export const vote = createTable(
  'Vote',
  {
    chatId: uuid('chatId')
      .notNull()
      .references(() => chat.id),
    messageId: uuid('messageId')
      .notNull()
      .references(() => message.id),
    isUpvoted: boolean('isUpvoted').notNull(),
  },
  (table) => ({
    pk: primaryKey({ columns: [table.chatId, table.messageId] }),
  }),
);

export type Vote = InferSelectModel<typeof vote>;

// Policy review decisions captured from the Policy Compliance dashboard.
// This is the transactional audit log in Lakebase; the latest decision is also
// written back to the Delta policy table for analytics.
export const policyReview = createTable('PolicyReview', {
  id: uuid('id').primaryKey().notNull().defaultRandom(),
  policyId: text('policyId').notNull(),
  decision: varchar('decision', {
    enum: ['approved', 'changes_requested'],
  }).notNull(),
  comment: text('comment'),
  reviewer: text('reviewer').notNull(),
  createdAt: timestamp('createdAt').notNull().defaultNow(),
});

export type PolicyReview = InferSelectModel<typeof policyReview>;

// Uploaded policies land here first (Lakebase Postgres). The PDF is converted
// to text in the browser as it loads, so the `content` column is editable
// before and after upload. Lakebase Change Data Feed (wal2delta) streams every
// insert/update on this table to a Unity Catalog Delta history table, which a
// pipeline merges into the Delta `policy_docs` table the agent searches.
// Requires `ALTER TABLE ai_chatbot."PolicyUpload" REPLICA IDENTITY FULL;` for CDF.
export const policyUpload = createTable('PolicyUpload', {
  id: uuid('id').primaryKey().notNull().defaultRandom(),
  policyId: text('policyId').notNull().unique(), // UPL-### (distinct from seed POL-###)
  docName: text('docName').notNull(),
  category: text('category'),
  title: text('title').notNull(),
  owner: text('owner'),
  version: text('version'),
  effectiveDate: text('effectiveDate'), // YYYY-MM-DD; CAST to DATE in the merge
  reviewDate: text('reviewDate'),
  content: text('content').notNull(),
  sourceFilename: text('sourceFilename'),
  uploadedBy: text('uploadedBy').notNull(),
  createdAt: timestamp('createdAt').notNull().defaultNow(),
  updatedAt: timestamp('updatedAt').notNull().defaultNow(),
});

export type PolicyUpload = InferSelectModel<typeof policyUpload>;
