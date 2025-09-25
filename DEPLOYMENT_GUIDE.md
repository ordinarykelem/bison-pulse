# 🚀 Bison Tracking System - Deployment Guide

## Netlify Frontend Deployment

### Step 1: Prepare for Deployment

1. **Build the project locally first:**
   ```bash
   npm run build
   ```

2. **Test the build:**
   ```bash
   npm run preview
   ```

### Step 2: Deploy to Netlify

#### Option A: Netlify CLI (Recommended)
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy
netlify deploy --prod --dir=dist
```

#### Option B: Netlify Web Interface
1. Go to [netlify.com](https://netlify.com)
2. Drag and drop your `dist` folder
3. Configure environment variables in Site Settings

### Step 3: Configure Environment Variables

In Netlify Dashboard → Site Settings → Environment Variables:

```
VITE_API_URL=https://your-backend-url.railway.app
VITE_STREAM_URL=https://your-backend-url.railway.app/stream
VITE_USE_MOCK_DATA=false
```

## Backend Deployment Options

### Option 1: Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Option 2: Render
1. Connect your GitHub repository
2. Select "Web Service"
3. Configure build command: `pip install -r requirements.txt`
4. Configure start command: `python backend/simple_server.py`

### Option 3: Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: python backend/simple_server.py" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## Complete Deployment Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Netlify       │    │   Railway/Render │    │   RTSP Stream   │
│   (Frontend)    │◄──►│   (Backend API)  │◄──►│   (Video Feed)  │
│                 │    │                  │    │                 │
│ • React App     │    │ • FastAPI        │    │ • Live Video    │
│ • Real-time UI  │    │ • YOLO Model     │    │ • Bison Stream  │
│ • Analytics     │    │ • SSE Stream     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Environment Configuration

### Frontend (Netlify)
- `VITE_API_URL`: Your deployed backend URL
- `VITE_STREAM_URL`: SSE endpoint URL
- `VITE_USE_MOCK_DATA`: Set to `false` for production

### Backend (Railway/Render/Heroku)
- `RTSP_URL`: Your RTSP stream URL
- `API_HOST`: Set to `0.0.0.0` for production
- `API_PORT`: Set to `8080` or use platform's PORT variable

## Testing Your Deployment

1. **Frontend**: Visit your Netlify URL
2. **Backend Health**: `https://your-backend-url.railway.app/health`
3. **API Test**: `https://your-backend-url.railway.app/api/latest`
4. **SSE Stream**: `https://your-backend-url.railway.app/stream`

## Troubleshooting

### Common Issues:
1. **CORS Errors**: Ensure backend CORS includes your Netlify domain
2. **SSE Connection**: Check if your hosting platform supports SSE
3. **Environment Variables**: Verify all env vars are set correctly
4. **Build Failures**: Check Node.js version compatibility

### Support:
- Netlify Docs: https://docs.netlify.com/
- Railway Docs: https://docs.railway.app/
- Render Docs: https://render.com/docs

## Production Checklist

- [ ] Frontend deployed to Netlify
- [ ] Backend deployed to Railway/Render/Heroku
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] SSL certificates active
- [ ] Domain configured (optional)
- [ ] Monitoring set up
- [ ] Error tracking enabled
