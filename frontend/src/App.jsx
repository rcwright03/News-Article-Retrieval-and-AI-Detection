import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  Search,
  Flame,
  Layers,
  BarChart3,
  BookOpenText,
  ExternalLink,
  Rocket,
  Info,
  Sparkles,
} from "lucide-react";
import api from "./api";

// ---- Site meta ----
const SITE = {
  title: "R&D · News Retrieval and AI Detection",
  org: "Worcester Polytechnic Institute",
  course: "CS 548 - Information Retrieval",
  instructor: "Professor Kyumin Lee",
  date: "October 27, 2025",
  authors: ["Caleb Duah", "Brian Jin", "Shikshya Shiwakoti", "Ryan Wright"],
};

// ---- Local mock results (fallback if backend fails) ----
const MOCK_RESULTS = [
  {
    id: "a1",
    title: "City council passes budget after marathon session",
    source: "Local Daily",
    url: "https://example.com/a1",
    publishedAt: "2025-10-26",
    bm25: 7.42,
    cosine: 0.83,
    aiScore: 0.22,
    snippet:
      "After a ten hour debate, members approved a revised spending plan that funds schools and transit...",
  },
  {
    id: "a2",
    title: "New study finds coral reefs show signs of recovery",
    source: "Science Wire",
    url: "https://example.com/a2",
    publishedAt: "2025-10-25",
    bm25: 6.31,
    cosine: 0.78,
    aiScore: 0.64,
    snippet:
      "Researchers observed improved bleaching resistance across multiple sites over three years...",
  },
  {
    id: "a3",
    title: "Quarterly earnings beat expectations for chip maker",
    source: "Market Watcher",
    url: "https://example.com/a3",
    publishedAt: "2025-10-24",
    bm25: 5.88,
    cosine: 0.75,
    aiScore: 0.11,
    snippet:
      "Revenue rose thirteen percent as demand for AI accelerators held steady through Q3...",
  },
  {
    id: "a4",
    title: "Will be replaced by the backend very soon",
    source: "Waiting for backend",
    url: "https://example.com/a4",
    publishedAt: "2025-10-24",
    bm25: 5.12,
    cosine: 0.70,
    aiScore: 0.35,
    snippet: "Demo placeholder while the real search pipeline is wired in.",
  },
];

// ---- Small UI helpers ----
function Pill({ children }) {
  return (
    <span className="inline-flex items-center rounded-full bg-slate-800/80 border border-slate-700 px-3 py-1 text-xs text-slate-200">
      {children}
    </span>
  );
}

function Section({ id, title, icon: Icon, children }) {
  return (
    <section id={id} className="scroll-mt-24 py-14">
      <div className="mx-auto max-w-6xl px-4">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="mb-6 flex items-center gap-2"
        >
          {Icon ? <Icon className="h-5 w-5 text-amber-400" /> : null}
          <h2 className="text-2xl font-semibold text-white">{title}</h2>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4, delay: 0.05 }}
          className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 text-slate-200 leading-7"
        >
          {children}
        </motion.div>
      </div>
    </section>
  );
}

function ScoreBar({ label, value, color = "bg-emerald-500" }) {
  const pct = Math.max(0, Math.min(1, value)) * 100;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-slate-300">
        <span>{label}</span>
        <span className="text-white font-medium">
          {Number.isFinite(value) ? value.toFixed(2) : "-"}
        </span>
      </div>
      <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-10 text-center">
      <div className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-xl bg-slate-800 text-slate-200">
        <Info className="h-6 w-6" />
      </div>
      <h4 className="text-white font-semibold">No results yet</h4>
      <p className="mt-1 text-slate-300 text-sm">
        Try a topic like “Boston transit budget” or “coral reef recovery”.
      </p>
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <div className="h-5 w-2/3 bg-slate-800 rounded" />
      <div className="mt-3 h-4 w-1/3 bg-slate-800 rounded" />
      <div className="mt-4 h-16 w-full bg-slate-800 rounded" />
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <div className="h-6 bg-slate-800 rounded" />
        <div className="h-6 bg-slate-800 rounded" />
        <div className="h-6 bg-slate-800 rounded" />
      </div>
    </div>
  );
}

function ResultCard({ r, index }) {
  const aiColor =
    r.aiScore < 0.35
      ? "text-emerald-300 bg-emerald-500/10 border-emerald-600/40"
      : r.aiScore < 0.65
      ? "text-amber-300 bg-amber-500/10 border-amber-600/40"
      : "text-rose-300 bg-rose-500/10 border-rose-600/40";

  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white">
            <a
              href={r.url}
              className="hover:underline"
              target="_blank"
              rel="noreferrer"
            >
              {index + 1}. {r.title}
            </a>
          </h3>
          <p className="mt-1 text-sm text-slate-300">
            <span className="mr-2">{r.source}</span>• {r.publishedAt}
          </p>
        </div>
        <a
          href={r.url}
          target="_blank"
          rel="noreferrer"
          className="text-slate-300 hover:text-white"
        >
          <ExternalLink className="h-5 w-5" />
        </a>
      </div>

      <p className="mt-3 text-slate-200">{r.snippet}</p>

      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <ScoreBar label="Cosine" value={r.cosine ?? 0} color="bg-emerald-500" />
        <ScoreBar label="AI score" value={r.aiScore ?? 0} color="bg-rose-500" />
        <div>
          <div className="flex justify-between text-xs text-slate-300">
            <span>BM25</span>
            <span className="text-white font-medium">
              {Number.isFinite(r.bm25) ? r.bm25.toFixed(2) : "-"}
            </span>
          </div>
          <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-sky-500"
              style={{
                width: `${
                  Number.isFinite(r.bm25) ? Math.min(100, r.bm25 * 10) : 0
                }%`,
              }}
            />
          </div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <span
          className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs ${aiColor}`}
        >
          <Sparkles className="h-3 w-3" /> AI likelihood{" "}
          {Number.isFinite(r.aiScore)
            ? `${(r.aiScore * 100).toFixed(0)}%`
            : "–"}
        </span>
        <span className="inline-flex items-center gap-1 rounded-full border border-slate-700 px-2.5 py-1 text-xs text-slate-300">
          BM25 {Number.isFinite(r.bm25) ? r.bm25.toFixed(2) : "-"}
        </span>
        <span className="inline-flex items-center gap-1 rounded-full border border-slate-700 px-2.5 py-1 text-xs text-slate-300">
          Cos {Number.isFinite(r.cosine) ? r.cosine.toFixed(2) : "-"}
        </span>
      </div>
    </article>
  );
}

function Demo() {
  const [query, setQuery] = useState("news");
  const [topK, setTopK] = useState(10);
  const [rerank, setRerank] = useState(true);
  const [model, setModel] = useState("mpnet");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [ranOnce, setRanOnce] = useState(false);
  const [error, setError] = useState("");

  const visible = useMemo(() => items.slice(0, topK), [items, topK]);

  async function run() {
    setLoading(true);
    setRanOnce(true);
    setError("");
    try {
      const q = query.trim() || "news";
      const res = await api.get("/search", {
        params: { q, top_k: topK, rerank, model },
      });
      const fromApi = res.data?.items || [];
      setItems(fromApi.length ? fromApi : MOCK_RESULTS);
    } catch (e) {
      console.error(e);
      setError("Backend not reachable. Showing demo results instead.");
      setItems(MOCK_RESULTS);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6">
      <div className="grid gap-6 lg:grid-cols-[1fr,360px]">
        <div className="space-y-4">
          <div className="flex gap-2">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search news"
              className="flex-1 rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 focus:outline-none focus:ring-2 focus:ring-amber-400"
            />
            <button
              type="button"
              onClick={run}
              className="inline-flex items-center gap-2 rounded-xl bg-amber-400 px-4 py-3 font-medium text-slate-950 hover:opacity-90"
            >
              <Search className="h-4 w-4" /> Search
            </button>
          </div>

          {error && (
            <p className="text-sm text-amber-300 mt-1">
              {error}
            </p>
          )}

          <div className="grid gap-4">
            {loading && [0, 1, 2].map((i) => <SkeletonCard key={i} />)}
            {!loading &&
              visible.map((r, i) => <ResultCard r={r} index={i} key={r.id} />)}
            {!loading && ranOnce && !visible.length ? <EmptyState /> : null}
          </div>
        </div>

        <aside className="space-y-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
            <h4 className="text-white font-semibold flex items-center gap-2">
              <Layers className="h-4 w-4 text-amber-400" /> Pipeline
            </h4>
            <ul className="mt-3 space-y-2 text-sm text-slate-300 list-disc pl-5">
              <li>Collect via APIs or crawler</li>
              <li>Rank with BM25 Top K</li>
              <li>Rerank with cosine and embeddings</li>
              <li>Detect AI vs human authorship</li>
            </ul>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 space-y-3">
            <h4 className="text-white font-semibold flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-amber-400" /> Controls
            </h4>
            <label className="block text-sm">Top K</label>
            <input
              type="range"
              min={1}
              max={20}
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-slate-300">Showing {topK}</div>

            <label className="mt-3 flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={rerank}
                onChange={(e) => setRerank(e.target.checked)}
              />{" "}
              Use rerank
            </label>

            <label className="block mt-3 text-sm">Embedding model</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            >
              <option value="mpnet">MPNet</option>
              <option value="sbert">SBERT</option>
            </select>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 text-sm text-slate-300">
            <p className="mb-2 font-medium text-white">Tip</p>
            <p>
              When you wire the full backend, return fields:{" "}
              <code className="bg-slate-800 px-1 py-0.5 rounded">
                title,url,source,publishedAt,bm25,cosine,aiScore,snippet
              </code>
              .
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}

// ---- Main app shell ----
export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Decorative gradient backdrop */}
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div
          className="absolute inset-0 opacity-30"
          style={{
            background:
              "radial-gradient(600px 300px at 20% 10%, rgba(251,191,36,0.18), transparent), radial-gradient(600px 300px at 80% 20%, rgba(14,165,233,0.15), transparent), radial-gradient(600px 300px at 50% 80%, rgba(34,197,94,0.12), transparent)",
          }}
        />
      </div>

      {/* Nav */}
      <nav className="sticky top-0 z-20 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-amber-400 font-black text-slate-900">
              R&D
            </span>
            <span className="hidden sm:block font-medium">
              News Retrieval and AI Detection
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm text-slate-300">
            <a href="#about" className="hover:text-white">
              About
            </a>
            <a href="#need" className="hover:text-white">
              Why
            </a>
            <a href="#compare" className="hover:text-white">
              Compare
            </a>
            <a href="#build" className="hover:text-white">
              Build
            </a>
            <a href="#resources" className="hover:text-white">
              Resources
            </a>
            <a href="#demo" className="hover:text-white">
              Demo
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <header className="bg-gradient-to-b from-slate-900/60 to-slate-950">
        <div className="mx-auto max-w-6xl px-4 py-16">
          <motion.p
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="text-sm text-slate-300"
          >
            {SITE.org}
          </motion.p>
          <motion.h1
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.05 }}
            className="mt-2 text-3xl sm:text-5xl font-bold text-white"
          >
            {SITE.title}
          </motion.h1>
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mt-3 flex flex-wrap gap-2"
          >
            {SITE.authors.map((a) => (
              <Pill key={a}>{a}</Pill>
            ))}
          </motion.div>
          <p className="mt-4 text-slate-300">
            {SITE.course} · {SITE.instructor} · {SITE.date}
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <a
              href="#demo"
              className="inline-flex items-center gap-2 rounded-xl bg-amber-400 px-4 py-3 font-medium text-slate-950 hover:opacity-90"
            >
              <Rocket className="h-4 w-4" /> Try demo
            </a>
            <a
              href="#resources"
              className="inline-flex items-center gap-2 rounded-xl border border-slate-700 px-4 py-3 font-medium text-slate-100 hover:bg-slate-900/60"
            >
              <BookOpenText className="h-4 w-4" /> Read more
            </a>
          </div>
        </div>
      </header>

      <Section id="about" title="What the tool does" icon={Search}>
        <p>
          Enter a query and the system gathers relevant news from multiple
          sources. It ranks with Okapi BM25 for the initial order, then reranks
          the top results using cosine similarity and embeddings to capture
          context. Each result shows an estimated AI authorship score from a
          classifier trained on human and AI text.
        </p>
      </Section>

      <Section id="need" title="Why it matters" icon={Flame}>
        <p>
          Readers face a constant stream of articles and a growing share may be
          machine written. This site helps you judge relevance and likely
          authorship before clicking. It supports students, instructors, and
          anyone who wants quick, trustworthy discovery.
        </p>
      </Section>

      <Section id="compare" title="How it differs" icon={Layers}>
        <p>
          Paste-in detectors score text you provide. This site goes further by
          fetching articles for your query, ranking them, and showing likely AI
          authorship inline so you can triage without opening each page.
        </p>
      </Section>

      <Section id="build" title="How we will build it" icon={BarChart3}>
        <ul className="list-disc pl-6 space-y-2">
          <li>
            Collect with NewsAPI, GDELT, or Currents. If needed, use a crawler
            with BeautifulSoup and Scrapy.
          </li>
          <li>
            Rank with BM25 and select Top K. Rerank with cosine and embeddings
            such as SBERT or MPNet.
          </li>
          <li>
            Evaluate with datasets like MSMARCO and Glasgow. Report precision,
            recall, F1, MAP, and NDCG.
          </li>
          <li>
            Detect AI vs human using a trained classifier. Start from public
            baselines and refine with our data.
          </li>
        </ul>
      </Section>

      <Section id="resources" title="Resources" icon={BookOpenText}>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <h4 className="font-semibold text-white mb-2">Datasets</h4>
            <ul className="list-disc pl-6 space-y-1 text-slate-300">
              <li>MSMARCO</li>
              <li>Glasgow collections</li>
              <li>CISI</li>
              <li>Human / AI paired text datasets</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-2">APIs and code</h4>
            <ul className="list-disc pl-6 space-y-1 text-slate-300">
              <li>NewsAPI, GDELT, Currents</li>
              <li>BeautifulSoup and Scrapy</li>
              <li>SBERT and MPNet embeddings</li>
            </ul>
          </div>
        </div>
      </Section>

      <section id="demo" className="py-14">
        <div className="mx-auto max-w-6xl px-4">
          <div className="mb-6 flex items-center gap-2">
            <Search className="h-5 w-5 text-amber-400" />
            <h2 className="text-2xl font-semibold text-white">
              Interactive demo
            </h2>
          </div>
          <Demo />
        </div>
      </section>

      <footer className="border-t border-slate-800 py-10">
        <div className="mx-auto max-w-6xl px-4 text-slate-300">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-white font-medium">{SITE.title}</div>
              <div className="text-sm">
                {SITE.org} · {SITE.course}
              </div>
            </div>
            <div className="flex gap-2">
              {SITE.authors.map((a) => (
                <Pill key={a}>{a}</Pill>
              ))}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
