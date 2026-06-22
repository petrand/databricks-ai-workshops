// Client-side PDF → text conversion. Runs in the browser as a document is
// loaded so the extracted text is immediately editable before it is uploaded
// to the Lakebase policy table.
//
// pdf.js is vendored as same-origin static assets under /pdfjs/ and loaded
// lazily at runtime (rather than as an npm dependency) because the Databricks
// Apps npm proxy does not mirror the pdfjs-dist package. The server never needs
// it; only the browser does.

// Minimal shape of the bits of the pdf.js API we use.
interface PdfTextItem {
  str: string;
  hasEOL: boolean;
}
interface PdfJsModule {
  GlobalWorkerOptions: { workerSrc: string };
  getDocument(src: { data: ArrayBuffer }): {
    promise: Promise<{
      numPages: number;
      getPage(n: number): Promise<{
        getTextContent(): Promise<{ items: Array<PdfTextItem | unknown> }>;
      }>;
    }>;
  };
}

const PDFJS_URL = '/pdfjs/pdf.min.mjs';
const PDFJS_WORKER_URL = '/pdfjs/pdf.worker.min.mjs';

let pdfjsPromise: Promise<PdfJsModule> | null = null;

async function loadPdfjs(): Promise<PdfJsModule> {
  if (!pdfjsPromise) {
    pdfjsPromise = (
      import(/* @vite-ignore */ PDFJS_URL) as Promise<PdfJsModule>
    ).then((mod) => {
      mod.GlobalWorkerOptions.workerSrc = PDFJS_WORKER_URL;
      return mod;
    });
  }
  return pdfjsPromise;
}

export interface ExtractedPdf {
  /** Plain text with line/paragraph breaks reconstructed from the layout. */
  text: string;
  pageCount: number;
}

/**
 * Extract readable text from a PDF File. Reconstructs line breaks from pdf.js
 * end-of-line markers and separates pages with a blank line. Not a perfect
 * layout converter — but good enough that a reviewer can clean it up in the
 * editor before saving.
 */
export async function extractPdfText(file: File): Promise<ExtractedPdf> {
  const pdfjsLib = await loadPdfjs();
  const data = await file.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data }).promise;
  const pages: string[] = [];

  for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
    const page = await pdf.getPage(pageNum);
    const content = await page.getTextContent();
    let line = '';
    const lines: string[] = [];
    for (const item of content.items) {
      // Marked-content items have no `str`; skip them.
      if (!item || typeof item !== 'object' || !('str' in item)) continue;
      const textItem = item as PdfTextItem;
      line += textItem.str;
      if (textItem.hasEOL) {
        lines.push(line.trimEnd());
        line = '';
      }
    }
    if (line.trim()) lines.push(line.trimEnd());
    pages.push(
      lines
        .join('\n')
        .replace(/\n{3,}/g, '\n\n')
        .trim(),
    );
  }

  return {
    text: pages.filter(Boolean).join('\n\n').trim(),
    pageCount: pdf.numPages,
  };
}
