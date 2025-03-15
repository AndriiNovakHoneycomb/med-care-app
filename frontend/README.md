# Med Care Admin Dashboard

A modern admin dashboard for managing patient records, built with React, TypeScript, and Material-UI.

## Features

- 🔐 JWT Authentication
- 👥 Patient Management
- 📊 Data Grid with Sorting and Filtering
- 🎨 Modern UI with Material Design
- 📱 Responsive Layout
- 🔄 Real-time Data Updates
- ✨ Clean and Maintainable Code

## Tech Stack

- React 18
- TypeScript
- Material-UI (MUI)
- React Query
- Zustand
- React Router
- React Hook Form
- Yup
- Axios

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd med-care-app/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the root directory:
   ```env
   VITE_API_URL=http://localhost:3000/api
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5173`.

### Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/         # Page components
├── services/      # API services
├── store/         # Global state management
├── hooks/         # Custom React hooks
├── utils/         # Utility functions
├── types/         # TypeScript type definitions
└── theme.ts       # MUI theme configuration
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
