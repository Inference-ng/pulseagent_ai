

# CONTEXT
You are building the **React demo dashboard** for PurseAgent AI. This is what judges will interact with. Make it visually impressive — dark mode, smooth animations, Nigerian-themed personas. It must clearly demonstrate both Task A and Task B.

Work directory: `apps/frontend/`
Backend API is at: `http://localhost:8000`

## TECH STACK
- React 18 + Vite
- TailwindCSS
- React Router v6
- Axios
- Framer Motion (animations)
- React Hook Form (persona builder)
- Lucide React (icons)

## TASK 1: Initialize the project
```bash
cd apps/frontend
npm create vite@latest . -- --template react
npm install tailwindcss @tailwindcss/forms framer-motion axios react-router-dom react-hook-form lucide-react
npx tailwindcss init -p
```

## TASK 2: Configure TailwindCSS (`tailwind.config.js`)
Theme colors:
- Primary: emerald (green) — `#10b981`
- Accent: amber — `#f59e0b`
- Background: `#0f172a` (slate-950)
- Card: `#1e293b` (slate-800)
- Text: `#f8fafc` (slate-50)
Add Inter font from Google Fonts in `index.html`.

## TASK 3: Create file structure
```
src/
├── components/
│   ├── layout/Navbar.jsx
│   ├── persona/PersonaSelector.jsx
│   ├── tasks/TaskAPanel.jsx
│   ├── tasks/TaskBPanel.jsx
│   ├── results/ReviewResult.jsx
│   ├── results/RecommendationList.jsx
│   └── ui/StarRating.jsx
├── pages/
│   ├── Home.jsx
│   └── Demo.jsx
├── data/demo-personas.js
├── lib/api.js
├── App.jsx
├── main.jsx
└── index.css
```

## TASK 4: Implement `src/lib/api.js`
```js
import axios from 'axios';
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 90000
});
export const simulateReview = (payload) => api.post('/api/v1/simulate-review', payload);
export const getRecommendations = (payload) => api.post('/api/v1/recommend', payload);
export default api;
```

## TASK 5: Implement `src/data/demo-personas.js`
Four pre-built Nigerian personas:
1. Emmanuel — Lagos, price-sensitive sneaker lover, avg rating 3.2, NOT cold-start
2. Chioma — Abuja professional, fashion + beauty, avg rating 4.5, NOT cold-start
3. Tunde — New user from Kano, empty history, IS cold-start
4. Ngozi — Port Harcourt, books + education lover, avg rating 4.8, NOT cold-start

## TASK 6: Implement `src/pages/Home.jsx`
Hero section with:
- Large headline: "Meet PurseAgent AI — The Agent That Knows Your Customers"
- Subtitle explaining Task A and Task B
- Two CTA buttons: "Try Task A (Review Simulation)" and "Try Task B (Recommendations)"
- Animated stat cards: "78% purchase accuracy", "10ms response", "3 datasets"
- Use Framer Motion for fade-in on scroll

## TASK 7: Implement `src/pages/Demo.jsx`
Two-tab layout (Tab A | Tab B) with:
- Top: PersonaSelector (dropdown of 4 demo personas OR "Build Custom Persona")
- Tab A: TaskAPanel (product input form → ReviewResult on submit)
- Tab B: TaskBPanel (context input + domain select → RecommendationList on submit)

## TASK 8: Implement `src/components/tasks/TaskAPanel.jsx`
Form fields:
- Product name (text input)
- Category (select: Fashion, Electronics, Books, Food, Beauty)
- Price in ₦ (number input)
- Brand (text input)
- Description (textarea, optional)
- Submit button with loading state ("Simulating review...")

On success → animate ReviewResult into view (Framer Motion slide-in)

## TASK 9: Implement `src/components/results/ReviewResult.jsx`
Display:
- Animated star rating (1-5 stars filling from left, gold colour)
- Review text in a styled blockquote
- Confidence badge (green if >0.7, amber if 0.5-0.7, red if <0.5)
- Collapsible "Agent Reasoning" section

## TASK 10: Implement `src/components/tasks/TaskBPanel.jsx`
Fields:
- Context text input: "What are you looking for?" (e.g. "shoes for a wedding")
- Domain selector: Fashion | Electronics | Books | Food
- Number of recommendations (slider: 3-10)
- Cold-start badge auto-shown if selected persona has is_cold_start=true
- Submit button with loading state ("Finding best matches...")

On success → animate RecommendationList into view

## TASK 11: Implement `src/components/results/RecommendationList.jsx`
Display each recommendation as a card:
- Rank number badge (#1, #2...)
- Item name + category badge
- Score bar (green gradient progress bar, 0-100%)
- Reason text (italic, muted)
- If cold-start → show yellow banner: "Cold-Start Mode: Recommendations based on context only"

## TASK 12: Implement `src/components/layout/Navbar.jsx`
- Logo: "PurseAgent AI" with emerald dot
- Links: Home | Demo
- GitHub link (opens repo in new tab)
- Dark background, blur backdrop

## TASK 13: Dockerfile
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

Create `nginx.conf`:
```nginx
server {
  listen 3000;
  location / {
    root /usr/share/nginx/html;
    index index.html;
    try_files $uri $uri/ /index.html;
  }
  location /api {
    proxy_pass http://backend:8000;
  }
}
```

## ACCEPTANCE CRITERIA
- Home page loads at http://localhost:3000 with hero section
- Demo page has both Task A and Task B tabs
- PersonaSelector shows all 4 demo personas
- Task A: submitting a product returns a review with star rating
- Task B: submitting a context returns a ranked list
- Cold-start persona (Tunde) shows cold-start banner
- All animations work (Framer Motion)
- Mobile-responsive layout

---
