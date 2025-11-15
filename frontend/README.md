# Write Aid AI Checker - React Frontend

This is the React frontend for the Write Aid AI Checker application.

Deployed on Vercel.

## Development

### Prerequisites
- Node.js 16+ and npm
- Backend server running on `http://localhost:5001`

### Setup
```bash
cd frontend
npm install
```

### Run Development Server
```bash
npm start
```

The app will open at `http://localhost:3000` and proxy API requests to `http://localhost:5001`.

### Build for Production
```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

## Configuration

### Development
The app uses a proxy configured in `package.json` to forward API requests to the backend:
```json
"proxy": "http://localhost:5001"
```

### Production
Set the backend URL via environment variable:
- In Vercel: Add `REACT_APP_BACKEND_URL` in Settings → Environment Variables
- Locally: Copy `env.example` to `.env.production.local` and update the URL

## Project Structure

```
frontend/
├── public/           # Static assets
├── src/
│   ├── App.js       # Main application component
│   ├── App.css      # Application styles
│   ├── index.js     # Entry point
│   └── services/
│       └── FinChatClient.js  # Backend API client
├── package.json     # Dependencies and scripts
└── README.md        # This file
```

## Features

- **Text Input Panel**: Paste or type text to analyze
- **Evaluation Panel**: View AI detection results
- **MCP Integration**: Connects to FinChat MCP via backend
- **Real-time Status**: Shows connection status and analysis progress
- **Responsive Design**: Works on desktop and mobile

## API Integration

The frontend communicates with the backend API:
- `GET /health` - Check backend health
- `GET /api/config` - Get backend configuration
- `POST /api/mcp/analyze` - Analyze text via MCP

## Deployment

See [../DEPLOYMENT.md](../DEPLOYMENT.md) for deployment instructions to Vercel.

## Troubleshooting

### "Backend Offline" Error
1. Make sure backend server is running on port 5001
2. Check `REACT_APP_BACKEND_URL` environment variable
3. Verify CORS is configured on backend

### Build Errors
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

## Technologies

- **React 19** - UI library
- **Create React App** - Build tooling
- **Fetch API** - HTTP client
- **CSS3** - Styling

