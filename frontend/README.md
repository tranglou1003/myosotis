# Myosotis 🌸
### Alzheimer Support Web Application

A modern, accessible web application designed to support people with Alzheimer's disease and their caregivers with daily care management, memory aids, and family communication tools.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/VietDSK6/myosotis.git
   cd myosotis
   ```

2. **Install dependencies**
   ```bash
   npm install --legacy-peer-deps
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env.local
   ```
   
   Update `.env.local` with your API URL:
   ```env
   VITE_API_URL=http://your-backend-url:8777
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

   Open [http://localhost:5173](http://localhost:5173) in your browser.

## 🏗️ Technology Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS + Custom accessibility classes
- **Routing**: React Router v6
- **State**: Zustand with persistence
- **Forms**: React Hook Form + Zod validation
- **HTTP**: Axios with interceptors
- **UI**: Headless components with focus management

## 📁 Project Structure

```
src/
├── app/                    # Core application setup
│   ├── main.tsx           # Entry point
│   ├── router.tsx         # Route definitions
│   └── AppWithAuth.tsx    # Auth wrapper
├── features/auth/          # Authentication module
│   ├── api.ts             # Auth API calls
│   ├── store.ts           # Auth state management
│   ├── types.ts           # TypeScript interfaces
│   ├── validation.ts      # Form validation schemas
│   ├── hooks.ts           # Auth-related hooks
│   ├── LoginForm.tsx      # Login form component
│   ├── RegisterForm.tsx   # Multi-step registration
│   └── components/        # Shared auth components
├── pages/                  # Page components
│   ├── WelcomePage.tsx    # Landing page
│   ├── DashboardPage.tsx  # Main user dashboard
│   ├── CaregiverGuidePage.tsx  # Caregiver resources
│   └── ForgotPasswordPage.tsx  # Password recovery
├── hooks/                  # Custom hooks
│   └── useSessionTimeout.ts   # 24-hour session management
└── accessibility.css      # Custom accessibility styles
```

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript checks
```

### Environment Variables
```env
VITE_API_URL=http://localhost:8777    # Backend API URL
VITE_APP_NAME=Myosotis               # Application name
VITE_APP_VERSION=1.0.0               # Version number
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

