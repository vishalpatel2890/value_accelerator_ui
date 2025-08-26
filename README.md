# TD Value Accelerator MVP

A React + Python web application that allows users to deploy Treasure Data starter pack workflows through a guided interface.

## 📁 Project Structure

```
td-value-accelerator-ui/
├── src/                # Frontend React application
├── server/            # Backend FastAPI server
├── docs/              # Documentation files
├── tests/             # Test scripts
└── README.md          # This file
```

## 📚 Documentation

All documentation has been organized in the `docs/` folder:
- [Quick Start Guide](./docs/QUICKSTART.md)
- [Deployment Guide](./docs/DEPLOYMENT_README.md) 
- [Troubleshooting](./docs/TROUBLESHOOTING.md)
- [All Documentation](./docs/README.md)

## 🧪 Testing

Test scripts are located in the `tests/` folder:
- [Test Documentation](./tests/README.md)
- Run deployment tests with `python tests/test_deployment.py`

## Features

- **Configuration Screen**: Test TD connectivity and configure credentials
- **Starter Pack Selection**: Choose between QSR and Retail starter packs
- **Deployment Interface**: Configure and deploy workflows with real-time progress tracking
- **Modern UI**: Clean, consistent interface following CDP Platform style guide

## Tech Stack

### Frontend
- React 18 + TypeScript + Vite
- TailwindCSS + Radix UI components
- React Router for navigation
- React Query for state management
- WebSocket for real-time updates

### Backend
- FastAPI with Python
- WebSocket support for real-time logs
- TD MCP server integration
- GitHub repository integration

## Quick Start

For detailed setup instructions, see the [Quick Start Guide](./docs/QUICKSTART.md).

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- TD MCP server running locally (assumed on localhost:8001)

### Installation

1. **Install frontend dependencies:**
   ```bash
   npm install
   ```

2. **Install backend dependencies:**
   ```bash
   npm run server:install
   ```
   
   **Note:** If you encounter pip version issues with Anaconda, the setup script will create a virtual environment to avoid conflicts.
   
   **Alternative manual setup:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   cd server && pip install -r requirements.txt
   ```

### Development

1. **Run both frontend and backend:**
   ```bash
   npm run dev:full
   ```

2. **Or run separately:**
   ```bash
   # Frontend (http://localhost:3000)
   npm run dev

   # Backend (http://localhost:8000)
   npm run server
   ```

### Usage

1. **Configuration**: Enter your TD API credentials and test connectivity
2. **Selection**: Choose between QSR or Retail starter pack
3. **Deployment**: Configure parameters and deploy workflows
4. **Monitor**: Watch real-time deployment progress and logs

## Detailed Project Structure

```
td-value-accelerator-ui/
├── src/                          # Frontend React app
│   ├── components/
│   │   ├── shared/              # Reusable UI components
│   │   ├── configuration/       # Configuration page
│   │   ├── selection/           # Starter pack selection
│   │   ├── deployment/          # Deployment interface
│   │   └── ui/                  # Base UI components
│   ├── types/                   # TypeScript type definitions
│   ├── utils/                   # Utility functions
│   └── hooks/                   # React hooks
├── server/                      # Backend FastAPI app
│   ├── routers/                 # API route handlers
│   ├── services/                # Business logic services
│   ├── models/                  # Pydantic models
│   └── main.py                  # FastAPI app entry point
├── docs/                        # Documentation
│   ├── QUICKSTART.md           # Quick start guide
│   ├── DEPLOYMENT_README.md    # Deployment documentation
│   └── TROUBLESHOOTING.md      # Common issues
├── tests/                       # Test scripts
│   ├── test_deployment.py      # Deployment API tests
│   └── README.md               # Test documentation
└── public/                      # Static assets
```

## API Endpoints

### TD Integration
- `POST /api/td/test-connection` - Test TD connectivity
- `GET /api/td/databases` - List available databases
- `GET /api/td/tables/{database}` - List tables in database

### GitHub Integration
- `GET /api/github/starter-packs` - Get available starter packs
- `GET /api/github/pack-details/{pack_name}` - Get pack details
- `GET /api/github/pack-files/{pack_name}` - Get pack files

### Deployment
- `POST /api/deploy/create` - Create and deploy to GitHub repository
- `GET /api/deploy/packages` - List available starter packages

## Configuration

The application expects TD MCP server to be running on `localhost:8001`. Update the `TDMCPService` class in `server/services/td_service.py` to modify the connection settings.

## Development Notes

- The frontend uses a modern React setup with TypeScript for type safety
- The backend is structured with clear separation of concerns
- WebSocket integration provides real-time deployment monitoring
- The UI follows the CDP Platform design system with consistent styling
- Mock data is used for demonstration purposes where external services aren't available

## Production Deployment

For production deployment:

1. Build the frontend: `npm run build`
2. Serve the built files with a web server
3. Deploy the FastAPI backend with a WSGI server like Gunicorn
4. Configure proper TD MCP server endpoints
5. Set up environment variables for sensitive data
6. Configure CORS settings appropriately

## License

This project is part of the Treasure Data SE Starter Pack collection.