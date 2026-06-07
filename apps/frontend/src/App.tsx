import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar }    from './components/layout/Navbar';
import { HomePage }  from './pages/Home';
import { DemoPage }  from './pages/Demo';

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen flex-col bg-canvas">
        <Navbar />
        <main className="flex-1 w-full">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/"     element={<HomePage />} />
              <Route path="/demo" element={<DemoPage />} />
              <Route path="*"     element={<HomePage />} />
            </Routes>
          </div>
        </main>
        <footer className="border-t border-white/[0.06] py-5">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <p className="text-center text-xs text-dim">
              PulseAgent AI · BCT × DSN Hackathon 2026 · Built with LangGraph, Gemini & FAISS
            </p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}
