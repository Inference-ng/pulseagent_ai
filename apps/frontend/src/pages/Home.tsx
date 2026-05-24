import { motion } from 'framer-motion';
import { ArrowRight, BrainCircuit, Database, Globe, MessageSquareText, Sparkles, UserRound, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';
import { RUN_MODE } from '../lib/api';

const features = [
  {
    icon: UserRound,
    title: 'Nigerian persona engine',
    description: 'Choose from Emmanuel (Lagos), Chioma (Abuja), Tunde (Kano cold-start), or Ngozi (PH) — or build a custom profile with full behavioral signals.',
    color: 'text-emerald',
    bg: 'bg-emerald/10 border-emerald/20',
  },
  {
    icon: MessageSquareText,
    title: 'Task A — Review simulation',
    description: 'Submit any product and watch the agent generate an authentic Nigerian review: star rating, written review in Pidgin, and agent reasoning.',
    color: 'text-amber',
    bg: 'bg-amber/10 border-amber/20',
  },
  {
    icon: BrainCircuit,
    title: 'Task B — Ranked recommendations',
    description: 'Get 10 semantically ranked items via FAISS retrieval + Gemini re-ranking. Handles cold-start users, cross-domain suggestions, and multi-turn follow-ups.',
    color: 'text-emerald',
    bg: 'bg-emerald/10 border-emerald/20',
  },
];

const techStack = [
  { label: 'LangGraph',         sub: 'Agentic workflow' },
  { label: 'Gemini 2.5 Flash',  sub: 'LLM backbone' },
  { label: 'FAISS',             sub: 'Vector retrieval' },
  { label: 'FastAPI',           sub: 'REST backend' },
  { label: 'Amazon Reviews 23', sub: 'Primary dataset' },
  { label: 'Yelp + Goodreads',  sub: 'Cross-domain data' },
];

const stats = [
  { value: '0.74',  label: 'NDCG@10',          sub: 'vs 0.48 collab filter' },
  { value: '0.76',  label: 'BERTScore F1',      sub: 'Task A review quality' },
  { value: '0.58',  label: 'Cold-start HR@10',  sub: 'vs 0.21 baseline' },
];

export function HomePage() {
  return (
    <div className="space-y-12 py-8 sm:py-12">

      {/* ── Hero ── */}
      <motion.section
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative overflow-hidden rounded-2xl border border-white/[0.06] bg-panel p-7 sm:p-10"
      >
        {/* Background glows */}
        <div className="pointer-events-none absolute inset-0 bg-hero-glow opacity-60" />
        <div className="pointer-events-none absolute inset-0 bg-amber-glow opacity-40" />
        <div className="pointer-events-none absolute inset-0 bg-grid-pattern bg-grid opacity-[0.4]" />

        <div className="relative">
          <div className="flex flex-wrap items-center gap-2 mb-5">
            <span className="badge-emerald">BCT × DSN Hackathon 2026</span>
            {RUN_MODE === 'mock' && (
              <span className="badge-amber">
                <Zap className="h-2.5 w-2.5" />
                Mock mode active
              </span>
            )}
          </div>

          <h1 className="text-4xl font-extrabold leading-tight text-ink sm:text-5xl lg:text-6xl">
            Meet{' '}
            <span className="bg-gradient-to-r from-emerald to-gold bg-clip-text text-transparent">
              PulseAgent AI
            </span>
          </h1>
          <p className="mt-2 text-lg font-medium text-mist sm:text-xl">
            The agent that knows your customers.
          </p>
          <p className="mt-5 max-w-2xl text-sm leading-7 text-mist sm:text-base">
            A dual-task LLM system for <strong className="text-ink">user modeling</strong> and{' '}
            <strong className="text-ink">personalized recommendation</strong> — built on LangGraph,
            FAISS, and Gemini, contextualized for Nigerian e-commerce.
          </p>

          <div className="mt-7 flex flex-wrap gap-3">
            <Link to="/demo" className="btn-primary px-6">
              Launch Demo
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link to="/demo" className="btn-ghost px-6">
              View Task A + B
            </Link>
          </div>
        </div>
      </motion.section>

      {/* ── Stats ── */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.08 }}
            className="card text-center"
          >
            <p className="text-4xl font-extrabold text-emerald">{s.value}</p>
            <p className="mt-2 text-sm font-semibold text-ink">{s.label}</p>
            <p className="mt-1 text-xs text-mist">{s.sub}</p>
          </motion.div>
        ))}
      </section>

      {/* ── Features ── */}
      <section>
        <p className="eyebrow mb-4">What it does</p>
        <div className="grid gap-5 sm:grid-cols-3">
          {features.map((f, i) => {
            const Icon = f.icon;
            return (
              <motion.article
                key={f.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + i * 0.08 }}
                className="card group"
              >
                <span className={`inline-flex h-10 w-10 items-center justify-center rounded-xl border ${f.bg} mb-4`}>
                  <Icon className={`h-5 w-5 ${f.color}`} />
                </span>
                <h2 className="text-base font-bold text-ink">{f.title}</h2>
                <p className="mt-2 text-sm leading-6 text-mist">{f.description}</p>
              </motion.article>
            );
          })}
        </div>
      </section>

      {/* ── Architecture overview ── */}
      <section className="card">
        <p className="eyebrow mb-1 flex items-center gap-1.5">
          <Globe className="h-3 w-3" />System architecture
        </p>
        <h2 className="mb-5 text-xl font-bold text-ink">How PulseAgent works</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { step: '01', title: 'Data layer',   desc: 'Amazon Reviews 2023 + Yelp + Goodreads → embedded via Sentence-BERT into FAISS index.',          icon: Database },
            { step: '02', title: 'AI agents',    desc: 'Two LangGraph state machines (Task A + B) with retrieve → contextualize → generate → validate.',   icon: BrainCircuit },
            { step: '03', title: 'Backend',      desc: 'FastAPI exposes /simulate-review and /recommend endpoints. Background audit logging to SQLite.',   icon: Zap },
            { step: '04', title: 'Frontend',     desc: 'React dashboard with Nigerian personas, live typewriter results, and multi-turn follow-up chat.',   icon: Sparkles },
          ].map(({ step, title, desc, icon: Icon }) => (
            <div key={step} className="card-sm relative overflow-hidden">
              <p className="absolute right-3 top-3 font-mono text-4xl font-extrabold text-white/[0.04]">{step}</p>
              <Icon className="h-5 w-5 text-emerald mb-3" />
              <h3 className="text-sm font-bold text-ink">{title}</h3>
              <p className="mt-1.5 text-xs leading-5 text-mist">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Tech stack ── */}
      <section>
        <p className="eyebrow mb-4">Tech stack</p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {techStack.map(({ label, sub }) => (
            <div key={label} className="card-sm text-center">
              <p className="text-xs font-bold text-ink">{label}</p>
              <p className="mt-0.5 text-[10px] text-mist">{sub}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
