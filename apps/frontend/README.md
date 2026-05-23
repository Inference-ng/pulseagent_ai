# 🎨 Frontend Dashboard — Victor's Domain
> **Victor Chukwuebuka** | React Demo Dashboard

---

## Your Mission
Build the visual demo that judges will interact with. This is the **face of PulseAgent AI**. Your dashboard must make it dead-simple for a judge to test both Task A (review simulation) and Task B (recommendations) — and be impressed by the UI.

---

## Your Deliverables

1. **User Persona Builder** — form to define a user (name, history, preferences)
2. **Task A Demo** — input a product → see simulated review + star rating
3. **Task B Demo** — input a persona + context → see ranked recommendations
4. **Cold-Start Demo** — toggle "New User" mode to show cold-start handling
5. **Pre-loaded Nigerian Personas** — 3–4 demo users judges can pick from

---

## Directory Structure

```
apps/frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Navbar.jsx
│   │   │   └── Sidebar.jsx
│   │   ├── persona/
│   │   │   ├── PersonaBuilder.jsx     # Form to create user persona
│   │   │   └── PersonaCard.jsx        # Display a persona summary
│   │   ├── tasks/
│   │   │   ├── TaskAPanel.jsx         # Review simulation UI
│   │   │   └── TaskBPanel.jsx         # Recommendation UI
│   │   ├── results/
│   │   │   ├── ReviewResult.jsx       # Shows simulated review + rating stars
│   │   │   ├── RecommendationList.jsx # Ranked list of recommendations
│   │   │   └── ReasoningCard.jsx      # Shows agent's reasoning
│   │   └── ui/
│   │       ├── StarRating.jsx         # Visual star rating component
│   │       ├── LoadingSpinner.jsx
│   │       └── Badge.jsx
│   ├── pages/
│   │   ├── Home.jsx                   # Landing / hero
│   │   ├── Demo.jsx                   # Main interactive demo
│   │   └── About.jsx                  # About the project
│   ├── hooks/
│   │   ├── useSimulateReview.js       # API call hook for Task A
│   │   └── useRecommendations.js      # API call hook for Task B
│   ├── data/
│   │   └── demo-personas.js           # Pre-loaded Nigerian demo personas
│   ├── lib/
│   │   └── api.js                     # Axios API client config
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── index.html
├── vite.config.js
├── tailwind.config.js
├── Dockerfile
├── .env.example
└── README.md
```

---

## Tech Stack
| Tool | Purpose |
|---|---|
| **React 18** | UI framework |
| **Vite** | Build tool (fast HMR) |
| **TailwindCSS** | Styling |
| **React Router v6** | Page routing |
| **Axios** | HTTP calls to backend |
| **Framer Motion** | Smooth animations |
| **React Hook Form** | Persona builder form |
| **Lucide React** | Icons |

---

## Pre-Loaded Demo Personas (data/demo-personas.js)

```javascript
export const DEMO_PERSONAS = [
  {
    id: "emmanuel_01",
    name: "Emmanuel (Lagos)",
    avatar: "🧑🏿",
    description: "Price-sensitive sneaker lover from Lagos",
    purchase_history: ["Nike Air Force 1", "Adidas Slides", "Puma Socks"],
    avg_rating_given: 3.2,
    price_sensitivity: "high",
    preferred_categories: ["footwear", "sportswear"],
    is_cold_start: false
  },
  {
    id: "chioma_02",
    name: "Chioma (Abuja)",
    avatar: "👩🏿",
    description: "Fashion-forward Abuja professional",
    purchase_history: ["Zara Dress", "Mac Lipstick", "Aldo Heels"],
    avg_rating_given: 4.5,
    price_sensitivity: "low",
    preferred_categories: ["fashion", "beauty"],
    is_cold_start: false
  },
  {
    id: "tunde_03",
    name: "Tunde (Kano) — NEW USER",
    avatar: "👨🏿",
    description: "New user, no purchase history",
    purchase_history: [],
    avg_rating_given: null,
    price_sensitivity: "medium",
    preferred_categories: [],
    is_cold_start: true
  },
  {
    id: "ngozi_04",
    name: "Ngozi (PH)",
    avatar: "👩🏿‍💼",
    description: "Book lover and online learner from Port Harcourt",
    purchase_history: ["Rich Dad Poor Dad", "Atomic Habits", "Coursera Sub"],
    avg_rating_given: 4.8,
    price_sensitivity: "medium",
    preferred_categories: ["books", "education"],
    is_cold_start: false
  }
];
```

---

## Key UI Requirements

### Task A Panel (Review Simulation)
- Persona selector (dropdown of demo personas OR custom builder)
- Product input form: name, category, price (₦), brand, description
- **Submit button → loading spinner → reveal animation**
- Result card showing:
  - ⭐ Star rating (animated fill)
  - Review text in a styled quote block
  - Confidence badge (e.g. "82% confident")
  - Agent reasoning (collapsible)

### Task B Panel (Recommendations)
- Persona selector
- Context input: "What are you looking for?" (free text)
- Domain filter: Fashion | Electronics | Books | Food
- Cold-start toggle (auto-set based on persona)
- Result: Ranked list of cards (item name, score bar, reason chip)

### Design Theme
- **Dark mode** preferred (judges = tech people)
- Accent colour: **emerald green** (#10b981) + **amber** (#f59e0b)
- Font: **Inter** (Google Fonts)
- Nigerian flag colours (green/white) as subtle accents
- Mobile-responsive

---

## Dockerfile

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

---

## Setup (Local Dev)

```bash
cd apps/frontend
npm install

# Create .env
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Run dev server
npm run dev
# Open: http://localhost:5173
```

---

## lib/api.js (Axios client)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000, // AI calls can take ~30s
  headers: { 'Content-Type': 'application/json' }
});

export const simulateReview = (payload) =>
  api.post('/api/v1/simulate-review', payload);

export const getRecommendations = (payload) =>
  api.post('/api/v1/recommend', payload);

export default api;
```

---

## Git Workflow
```bash
git checkout -b feat/frontend
# Work in apps/frontend/
git add apps/frontend/
git commit -m "feat(frontend): add persona builder and Task A review panel"
git push origin feat/frontend
# Open PR to main when done
```
