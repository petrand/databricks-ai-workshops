import { useCallback, useRef, useState } from 'react';
import { Streamdown } from 'streamdown';
import { toast } from 'sonner';
import {
  CheckCircle2,
  Eye,
  FileText,
  Pencil,
  UploadCloud,
  X,
} from 'lucide-react';
import {
  uploadPolicy,
  updatePolicyContent,
  useUploads,
  type UploadedPolicy,
} from '@/hooks/usePoliciesData';
import { extractPdfText } from '@/lib/extractPdfText';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';

interface FormState {
  title: string;
  category: string;
  owner: string;
  version: string;
  effectiveDate: string;
  reviewDate: string;
  content: string;
  sourceFilename: string;
}

const EMPTY_FORM: FormState = {
  title: '',
  category: '',
  owner: '',
  version: '1.0',
  effectiveDate: '',
  reviewDate: '',
  content: '',
  sourceFilename: '',
};

/** Turn "tenant_onboarding_policy.pdf" into "Tenant Onboarding Policy". */
function titleFromFilename(name: string): string {
  return name
    .replace(/\.pdf$/i, '')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function Field({
  label,
  children,
  hint,
}: {
  label: string;
  children: React.ReactNode;
  hint?: string;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="font-medium text-foreground text-sm">{label}</span>
      {children}
      {hint && <span className="text-muted-foreground text-xs">{hint}</span>}
    </div>
  );
}

export default function UploadPolicyPage() {
  const { uploads, refresh } = useUploads();
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [extracting, setExtracting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [preview, setPreview] = useState(false);
  const [pageCount, setPageCount] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const handleFile = useCallback(async (file: File) => {
    if (file.type !== 'application/pdf' && !/\.pdf$/i.test(file.name)) {
      toast.error('Please choose a PDF file.');
      return;
    }
    setExtracting(true);
    setPageCount(null);
    try {
      const { text, pageCount } = await extractPdfText(file);
      setPageCount(pageCount);
      setForm((f) => ({
        ...f,
        content: text,
        sourceFilename: file.name,
        title: f.title || titleFromFilename(file.name),
      }));
      if (!text.trim()) {
        toast.warning(
          'No text could be extracted (the PDF may be scanned images). You can type the policy text manually.',
        );
      } else {
        toast.success(`Extracted text from ${pageCount} page(s).`);
      }
    } catch (e) {
      toast.error(
        e instanceof Error ? e.message : 'Failed to read the PDF file.',
      );
    } finally {
      setExtracting(false);
    }
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  async function submit() {
    if (!form.title.trim()) {
      toast.error('A title is required.');
      return;
    }
    if (!form.content.trim()) {
      toast.error('No policy text — upload a PDF or type the content.');
      return;
    }
    setSubmitting(true);
    try {
      const res = await uploadPolicy({
        title: form.title.trim(),
        category: form.category.trim() || undefined,
        owner: form.owner.trim() || undefined,
        version: form.version.trim() || undefined,
        effectiveDate: form.effectiveDate || undefined,
        reviewDate: form.reviewDate || undefined,
        content: form.content,
        sourceFilename: form.sourceFilename || undefined,
      });
      toast.success(
        `Added ${res.policy.policyId}. Syncing to the policy table via Lakebase CDF…`,
      );
      setForm(EMPTY_FORM);
      setPageCount(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      await refresh();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Upload failed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <div className="flex flex-wrap items-start justify-between gap-3 border-border border-b px-6 py-4">
        <div>
          <h1 className="font-semibold text-foreground text-lg">
            Add a policy
          </h1>
          <p className="text-muted-foreground text-sm">
            Upload a PDF — it's converted to editable text, saved to Lakebase,
            then synced into the policy table via Change Data Feed.
          </p>
        </div>
      </div>

      <div className="flex flex-col gap-6 p-6">
        {/* Drop zone */}
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          className={cn(
            'flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors',
            dragging
              ? 'border-primary bg-primary/5'
              : 'border-border hover:bg-muted/40',
          )}
        >
          <UploadCloud className="h-8 w-8 text-muted-foreground" />
          <span className="font-medium text-foreground text-sm">
            {extracting
              ? 'Reading PDF…'
              : 'Drop a PDF here, or click to choose a file'}
          </span>
          <span className="text-muted-foreground text-xs">
            {form.sourceFilename
              ? `${form.sourceFilename}${pageCount ? ` · ${pageCount} page(s)` : ''}`
              : 'PDF only · text is extracted in your browser'}
          </span>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf,.pdf"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
            }}
          />
        </button>

        {/* Metadata */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field label="Title">
            <Input
              value={form.title}
              onChange={(e) => set('title', e.target.value)}
              placeholder="e.g. Tenant Onboarding Policy"
            />
          </Field>
          <Field label="Category">
            <Input
              value={form.category}
              onChange={(e) => set('category', e.target.value)}
              placeholder="e.g. Tenant & Leasing"
            />
          </Field>
          <Field label="Owner">
            <Input
              value={form.owner}
              onChange={(e) => set('owner', e.target.value)}
              placeholder="e.g. Risk & Compliance"
            />
          </Field>
          <Field label="Version">
            <Input
              value={form.version}
              onChange={(e) => set('version', e.target.value)}
              placeholder="1.0"
            />
          </Field>
          <Field label="Effective date">
            <Input
              type="date"
              value={form.effectiveDate}
              onChange={(e) => set('effectiveDate', e.target.value)}
            />
          </Field>
          <Field
            label="Review date"
            hint="When this policy is next due for review"
          >
            <Input
              type="date"
              value={form.reviewDate}
              onChange={(e) => set('reviewDate', e.target.value)}
            />
          </Field>
        </div>

        {/* Content */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="font-medium text-foreground text-sm">
              Policy text{' '}
              <span className="text-muted-foreground">
                ({form.content.length.toLocaleString()} chars)
              </span>
            </span>
            <button
              type="button"
              onClick={() => setPreview((p) => !p)}
              className="flex items-center gap-1 text-muted-foreground text-xs hover:text-foreground"
            >
              {preview ? (
                <>
                  <Pencil className="h-3.5 w-3.5" /> Edit
                </>
              ) : (
                <>
                  <Eye className="h-3.5 w-3.5" /> Preview
                </>
              )}
            </button>
          </div>
          {preview ? (
            <div className="min-h-60 rounded-md border border-border bg-muted/30 px-3 py-2 text-sm">
              {form.content.trim() ? (
                <Streamdown>{form.content}</Streamdown>
              ) : (
                <span className="text-muted-foreground text-xs">
                  Nothing to preview yet.
                </span>
              )}
            </div>
          ) : (
            <Textarea
              value={form.content}
              onChange={(e) => set('content', e.target.value)}
              placeholder="Upload a PDF to extract its text, or type the policy here…"
              className="min-h-60 font-mono text-xs"
            />
          )}
        </div>

        <div className="flex items-center justify-end gap-2">
          <Button
            variant="outline"
            onClick={() => {
              setForm(EMPTY_FORM);
              setPageCount(null);
              if (fileInputRef.current) fileInputRef.current.value = '';
            }}
            disabled={submitting}
          >
            Clear
          </Button>
          <Button onClick={submit} disabled={submitting || extracting}>
            {submitting ? 'Adding…' : 'Add policy'}
          </Button>
        </div>

        {/* Uploaded policies */}
        <div className="rounded-xl border border-border bg-card">
          <div className="flex items-center justify-between border-border border-b p-4">
            <h2 className="font-semibold text-foreground text-sm">
              Uploaded policies ({uploads.length})
            </h2>
            <span className="text-muted-foreground text-xs">
              Stored in Lakebase · synced to Delta via CDF
            </span>
          </div>
          {uploads.length === 0 ? (
            <p className="px-4 py-8 text-center text-muted-foreground text-sm">
              No uploaded policies yet.
            </p>
          ) : (
            <ul className="divide-y divide-border">
              {uploads.map((u) => (
                <UploadRow key={u.id} upload={u} onSaved={refresh} />
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

function UploadRow({
  upload,
  onSaved,
}: {
  upload: UploadedPolicy;
  onSaved: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [content, setContent] = useState(upload.content);
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      await updatePolicyContent(upload.policyId, content);
      toast.success(`Updated ${upload.policyId}. Re-syncing via Lakebase CDF…`);
      setEditing(false);
      await onSaved();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Save failed.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <li className="flex flex-col gap-3 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
            <span className="truncate font-medium text-foreground text-sm">
              {upload.title}
            </span>
          </div>
          <div className="mt-0.5 flex flex-wrap items-center gap-2 text-muted-foreground text-xs">
            <span className="font-mono">{upload.policyId}</span>
            {upload.category && <span>· {upload.category}</span>}
            <span>· by {upload.uploadedBy}</span>
            <Badge
              variant="outline"
              className="border-[var(--border-success)] bg-[var(--background-success)] text-[var(--success)]"
            >
              <CheckCircle2 className="mr-1 h-3 w-3" /> Lakebase
            </Badge>
          </div>
        </div>
        {editing ? (
          <button
            type="button"
            onClick={() => {
              setEditing(false);
              setContent(upload.content);
            }}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        ) : (
          <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
            <Pencil className="mr-2 h-3.5 w-3.5" /> Edit text
          </Button>
        )}
      </div>

      {editing && (
        <div className="flex flex-col gap-2">
          <Textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="min-h-52 font-mono text-xs"
          />
          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setEditing(false);
                setContent(upload.content);
              }}
              disabled={saving}
            >
              Cancel
            </Button>
            <Button size="sm" onClick={save} disabled={saving}>
              {saving ? 'Saving…' : 'Save changes'}
            </Button>
          </div>
        </div>
      )}
    </li>
  );
}
