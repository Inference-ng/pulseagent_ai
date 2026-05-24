import { motion } from 'framer-motion';
import { ArrowRight, BrainCircuit, MessageSquareText, UserRound } from 'lucide-react';
import { Link } from 'react-router-dom';

const features = [
  {
    title: 'Persona builder',
    description: 'Create realistic Nigerian customer profiles with pricing signals, history, and shopping context.',
    icon: UserRound,
  },
  {
    title: 'Task A simulation',
    description: 'Submit a product and surface an AI-generated review with rating, confidence, and reasoning.',
    icon: MessageSquareText,
  },
  {
    title: 'Task B ranking',
    description: 'Test recommendation output across fashion, electronics, books, and food with cold-start toggles.',
    icon: BrainCircuit,
  },
];

const stats = [
  { value: '78%', label: 'purchase accuracy' },
  { value: '10ms', label: 'response' },
  { value: '3', label: 'datasets' },
];

export function HomePage() {
  return (
    <div className="space-y-10 py-8 sm:py-12">
      <motion.section
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="panel-card relative overflow-hidden"
      >
        <div className="absolute -right-24 top-10 h-56 w-56 rounded-full bg-emerald/15 blur-3xl" />
        <div className="absolute bottom-0 left-0 h-40 w-40 rounded-full bg-amber/10 blur-3xl" />

        <p className="relative text-xs uppercase tracking-[0.32em] text-emerald">PulseAgent AI frontend</p>
        <h1 className="relative mt-4 max-w-4xl text-4xl font-semibold leading-tight text-ink sm:text-5xl lg:text-6xl">
          Meet PulseAgent AI - The Agent That Knows Your Customers
        </h1>
        <p className="relative mt-6 max-w-2xl text-base leading-8 text-mist sm:text-lg">
          Explore Task A review simulation and Task B recommendations through a polished demo built for judges, with Nigerian personas, smooth motion,
          and direct backend integration.
        </p>

        <div className="relative mt-8 flex flex-wrap gap-4">
          <Link to="/demo?tab=task-a" className="action-button w-auto px-6">
            Try Task A (Review Simulation)
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link to="/demo?tab=task-b" className="ghost-button w-auto px-6">
            Try Task B (Recommendations)
          </Link>
        </div>

        <div className="relative mt-10 grid gap-4 md:grid-cols-3">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.4 }}
              transition={{ duration: 0.35, delay: index * 0.08, ease: 'easeOut' }}
              className="rounded-[1.75rem] border border-white/10 bg-white/5 p-5"
            >
              <p className="text-3xl font-semibold text-ink">{stat.value}</p>
              <p className="mt-2 text-sm uppercase tracking-[0.18em] text-mist">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </motion.section>

      <section className="grid gap-6 lg:grid-cols-3">
        {features.map((feature, index) => {
          const Icon = feature.icon;

          return (
            <motion.article
              key={feature.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.45, delay: index * 0.08, ease: 'easeOut' }}
              className="panel-card"
            >
              <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-emerald">
                <Icon className="h-5 w-5" />
              </span>
              <h2 className="mt-5 text-xl font-semibold text-ink">{feature.title}</h2>
              <p className="mt-3 text-sm leading-7 text-mist">{feature.description}</p>
            </motion.article>
          );
        })}
      </section>
    </div>
  );
}