# 🚀 Bison Tracking System - Render Deployment Guide

## Quick Deploy to Render

### Option 1: One-Click Deploy (Recommended)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Option 2: Manual Deployment

1. **Go to [render.com](https://render.com)**
2. **Sign up/Login** with GitHub
3. **Connect your repository**
4. **Create New Web Service**

## Backend Configuration

### Service Settings:
- **Name**: `bison-backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python backend/simple_server.py`
- **Plan**: Free

### Environment Variables:
```
RTSP_URL=rtsps://cr-14.hostedcloudvideo.com:443/publish-cr/_definst_/G0W2EP7IKAXYETM1ANDVQ6DBRXNXCN7VK3MM7SP9/6b55ae911a8dbd2bd7d3a75ae4547acc976d0b9e?action=PLAY
API_HOST=0.0.0.0
API_PORT=10000
LOG_LEVEL=INFO
```

## Frontend Configuration

### Service Settings:
- **Name**: `bison-frontend`
- **Environment**: `Static Site`
- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `cdist`
- **Plan**: Free

### Environment Variables:
```
VITE_API_URL=https://your-backend-url.onrender.com
VITE_STREAM_URL=https://your-backend-url.onrender.com/stream
VITE_USE_MOCK_DATA=false
```

## Deployment Steps

### 1. Prepare Your Repository
```bash
# Make sure all files are committed
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Deploy Backend
1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure as shown above
5. Click "Create Web Service"

### 3. Deploy Frontend
1. After backend is deployed, note the URL
2. Click "New +" → "Static Site"
3. Connect the same repository
4. Configure as shown above
5. Update `VITE_API_URL` with your backend URL
6. Click "Create Static Site"

## Architecture on Render

```
┌─────────────────────────────────────────────────────────────┐
│                        Render Platform                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   Frontend      │    │         Backend                 │ │
│  │   (Static)      │◄──►│      (Web Service)             │ │
│  │                 │    │                                 │ │
│  │ • React App     │    │ • FastAPI Server               │ │
│  │ • Real-time UI  │    │ • YOLO Integration             │ │
│  │ • Analytics     │    │ • RTSP Processing              │ │
│  │ • Charts        │    │ • SSE Streaming                │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Testing Your Deployment

### Backend Health Check:
```
https://your-backend-url.onrender.com/health
```

### API Endpoints:
```
https://your-backend-url.onrender.com/api/latest
https://your-backend-url.onrender.com/api/status
https://your-backend-url.onrender.com/stream
```

### Frontend:
```
https://your-frontend-url.onrender.com
```

## Render-Specific Features

### Auto-Deploy
- Automatic deployments on git push
- Preview deployments for pull requests
- Rollback capabilities

### Monitoring
- Built-in logs and metrics
- Health check monitoring
- Performance insights

### Scaling
- Easy scaling from free to paid plans
- Custom domains
- SSL certificates included

## Environment Variables Reference

### Backend (.env)
```bash
RTSP_URL=your_rtsp_stream_url
API_HOST=0.0.0.0
API_PORT=10000
LOG_LEVEL=INFO
MODEL_PATH=best.pt
BISON_CLASS_ID=0
CONFIDENCE_THRESHOLD=0.25
```

### Frontend (Vite)
```bash
VITE_API_URL=https://your-backend.onrender.com
VITE_STREAM_URL=https://your-backend.onrender.com/stream
VITE_USE_MOCK_DATA=false
```

## Troubleshooting

### Common Issues:

1. **Build Failures**
   - Check Python/Node versions
   - Verify all dependencies in requirements.txt
   - Check build logs in Render dashboard

2. **CORS Errors**
   - Ensure backend CORS includes frontend domain
   - Check environment variables

3. **SSE Connection Issues**
   - Verify stream endpoint is accessible
   - Check network connectivity

4. **RTSP Stream Issues**
   - Verify RTSP URL is accessible
   - Check firewall/network restrictions

### Support Resources:
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- [Render Status](https://status.render.com)

## Production Checklist

- [ ] Repository connected to Render
- [ ] Backend service deployed and healthy
- [ ] Frontend service deployed
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Custom domain configured (optional)
- [ ] SSL certificates active
- [ ] Monitoring enabled
- [ ] Error tracking set up

## Cost Considerations

### Free Tier Limits:
- **Backend**: 750 hours/month (sleeps after 15 min inactivity)
- **Frontend**: Unlimited static hosting
- **Bandwidth**: 100GB/month

### Paid Plans:
- **Starter**: $7/month (always-on backend)
- **Standard**: $25/month (better performance)
- **Pro**: $85/month (production features)

## Next Steps After Deployment

1. **Test all endpoints**
2. **Configure custom domain** (optional)
3. **Set up monitoring**
4. **Enable error tracking**
5. **Configure backups**
6. **Set up CI/CD pipeline**
