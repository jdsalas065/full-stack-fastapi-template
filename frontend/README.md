# FastAPI Project - Frontend (Standalone)

The frontend is built with [Vite](https://vitejs.dev/), [React](https://reactjs.org/), [TypeScript](https://www.typescriptlang.org/), [TanStack Query](https://tanstack.com/query), [TanStack Router](https://tanstack.com/router) and [Tailwind CSS](https://tailwindcss.com/).

This frontend can run completely independently - it only needs a backend API URL to connect to.

## Quick Start

### 1. Setup Environment Variables

Create a `.env` file in the `frontend/` directory:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000

# Node Environment
NODE_ENV=development
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start Development Server

```bash
npm run dev
```

The frontend will be available at http://localhost:5173/

## Frontend Development

Before you begin, ensure that you have either the Node Version Manager (nvm) or Fast Node Manager (fnm) installed on your system.

* To install fnm follow the [official fnm guide](https://github.com/Schniz/fnm#installation). If you prefer nvm, you can install it using the [official nvm guide](https://github.com/nvm-sh/nvm#installing-and-updating).

* After installing either nvm or fnm, proceed to the `frontend` directory:

```bash
cd frontend
```

* If the Node.js version specified in the `.nvmrc` file isn't installed on your system, you can install it using the appropriate command:

```bash
# If using fnm
fnm install

# If using nvm
nvm install
```

* Once the installation is complete, switch to the installed version:

```bash
# If using fnm
fnm use

# If using nvm
nvm use
```

* Within the `frontend` directory, install the necessary NPM packages:

```bash
npm install
```

* And start the live server with the following `npm` script:

```bash
npm run dev
```

* Then open your browser at http://localhost:5173/.

Notice that this live server is not running inside Docker, it's for local development, and that is the recommended workflow. Once you are happy with your frontend, you can build the frontend Docker image and start it, to test it in a production-like environment. But building the image at every change will not be as productive as running the local development server with live reload.

Check the file `package.json` to see other available options.

## Generate OpenAPI Client

The frontend uses a generated TypeScript client based on the backend's OpenAPI schema. You need to regenerate this client whenever the backend API changes.

### Method 1: Using the Script (Recommended)

The frontend includes a standalone script that can fetch the OpenAPI schema from a running backend:

```bash
# Make sure the backend is running at the URL specified in VITE_API_URL
bash scripts/generate-client.sh
```

Or if you have `VITE_API_URL` set differently:

```bash
VITE_API_URL=http://localhost:8000 bash scripts/generate-client.sh
```

### Method 2: Manual Generation

1. **Option A: From a running backend**
   - Ensure your backend is running
   - Download the OpenAPI JSON from `http://localhost:8000/api/v1/openapi.json`
   - Save it as `openapi.json` in the `frontend/` directory
   - Run: `npm run generate-client`

2. **Option B: From an existing openapi.json file**
   - Place `openapi.json` in the `frontend/` directory
   - Run: `npm run generate-client`

### Method 3: Using Python (if backend is local)

If you have the backend code locally and Python installed:

```bash
# From the backend directory
cd ../backend
python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../frontend/openapi.json

# From the frontend directory
cd ../frontend
npm run generate-client
```

**Note:** Every time the backend API changes (changing the OpenAPI schema), you should regenerate the client using one of the methods above.

## Using a Remote API

If you want to use a remote API instead of localhost, set the `VITE_API_URL` environment variable:

### Option 1: Environment File

Create or update `frontend/.env`:

```env
VITE_API_URL=https://api.my-domain.example.com
```

### Option 2: Environment Variable

```bash
# Linux/Mac
export VITE_API_URL=https://api.my-domain.example.com
npm run dev

# Windows PowerShell
$env:VITE_API_URL="https://api.my-domain.example.com"
npm run dev

# Windows CMD
set VITE_API_URL=https://api.my-domain.example.com
npm run dev
```

Then, when you run the frontend, it will use that URL as the base URL for the API.

## Building for Production

### Build the Frontend

```bash
npm run build
```

This will create a `dist/` directory with the production-ready files.

### Preview Production Build

```bash
npm run preview
```

### Docker Build

The frontend includes a `Dockerfile` for containerized deployment:

```bash
docker build -t frontend:latest .
```

Or with build arguments:

```bash
docker build \
  --build-arg VITE_API_URL=https://api.example.com \
  --build-arg NODE_ENV=production \
  -t frontend:latest .
```

## Standalone Operation

This frontend is designed to run completely independently:

- ✅ All configuration in `frontend/.env`
- ✅ No dependencies on parent directory
- ✅ Can connect to any backend API via `VITE_API_URL`
- ✅ Can be deployed separately from backend
- ✅ All scripts are self-contained

The frontend only needs:
- A backend API URL (configured via `VITE_API_URL`)
- Node.js and npm installed
- No backend code or files required

## Code Structure

The frontend code is structured as follows:

```
frontend/
├── src/
│   ├── client/              # Generated OpenAPI client (auto-generated)
│   ├── components/          # React components
│   │   ├── Admin/          # Admin components
│   │   ├── Common/         # Common/shared components
│   │   ├── Items/          # Item-related components
│   │   ├── Pending/        # Pending items/users components
│   │   ├── Sidebar/        # Sidebar components
│   │   ├── ui/             # UI primitives (shadcn/ui)
│   │   └── UserSettings/   # User settings components
│   ├── hooks/              # Custom React hooks
│   ├── routes/             # TanStack Router routes
│   ├── lib/                # Utility libraries
│   └── data/               # Sample/static data
├── public/                 # Static assets
├── scripts/                # Utility scripts
│   └── generate-client.sh # OpenAPI client generator
├── .env                    # Environment variables (create from .env.example)
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration
├── tsconfig.json           # TypeScript configuration
└── Dockerfile              # Docker configuration
```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Lint code with Biome
- `npm run generate-client` - Generate TypeScript client from OpenAPI schema

## Troubleshooting

### Cannot connect to backend API

- Verify the backend is running
- Check `VITE_API_URL` in `.env` matches your backend URL
- Ensure CORS is properly configured on the backend
- Check browser console for CORS errors

### Client generation fails

- Ensure backend is running and accessible
- Check `VITE_API_URL` is correct
- Verify `openapi.json` exists if using manual method
- Check network connectivity to backend

### Port already in use

- Change the port in `vite.config.ts` or use:
  ```bash
  npm run dev -- --port 3000
  ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |
| `NODE_ENV` | Node environment | `development` |

## Development Tips

1. **Hot Reload**: The dev server automatically reloads on file changes
2. **Type Safety**: The generated OpenAPI client provides full TypeScript types
3. **API Changes**: Always regenerate the client after backend API changes
4. **Remote Backend**: You can develop frontend against a remote/staging backend by setting `VITE_API_URL`
