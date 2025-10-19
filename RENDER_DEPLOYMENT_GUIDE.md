# Jeeva.AI Backend - Render.com Deployment Guide

## 🚀 **Step-by-Step Deployment Instructions**

### **Step 1: Create PostgreSQL Database**
1. Go to [Render.com Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"PostgreSQL"**
3. Fill in the details:
   - **Name**: `jeeva-db`
   - **Database**: `jeeva_db`
   - **User**: `jeeva_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free (for testing) or Starter (for production)
4. Click **"Create Database"**
5. **IMPORTANT**: Copy the `DATABASE_URL` that Render provides (it will look like: `postgresql://username:password@hostname:port/database`)

### **Step 2: Create Web Service**
1. In Render.com dashboard, click **"New"** → **"Web Service"**
2. Connect your GitHub repository: `nvtarakanadh/jeeva.ai_backend`
3. Choose branch: `main`
4. Configure the service:

#### **Build & Deploy Settings**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `bash start.sh`

#### **Environment Variables**
Add these environment variables in the "Environment" tab:

```bash
SECRET_KEY=fc+wt)r77c6kkwosf@(%q=zddf@t*bvt(@s6e#_r2rudp4@5f8
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=postgresql://username:password@hostname:port/database
```

**Note**: Replace `your-app-name.onrender.com` with your actual Render app URL, and use the `DATABASE_URL` from Step 1.

### **Step 3: Deploy**
1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Set up the database
   - Start your service

### **Step 4: Verify Deployment**
1. Check the deployment logs for any errors
2. Your API will be available at: `https://your-app-name.onrender.com`
3. Test the API endpoints

## 🔧 **Configuration Files**

### **Build Command**
```bash
pip install -r requirements.txt
```

### **Start Command**
```bash
bash start.sh
```

### **Environment Variables Required**
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Your Render app domain
- `DATABASE_URL`: PostgreSQL connection string from Render

## 🐛 **Troubleshooting**

### **Common Issues**
1. **Build Fails**: Check that all dependencies are in `requirements.txt`
2. **Database Connection Error**: Verify `DATABASE_URL` is correct
3. **Service Won't Start**: Check the logs for specific error messages

### **Logs Location**
- Go to your service dashboard
- Click on "Logs" tab
- Look for error messages

## 📞 **Support**
If you encounter issues:
1. Check the deployment logs
2. Verify all environment variables are set correctly
3. Ensure the PostgreSQL database is created and running

## 🎯 **Expected Result**
After successful deployment, your backend API will be available at:
`https://your-app-name.onrender.com/api/`

The service will automatically:
- Install all Python dependencies
- Set up the database with migrations
- Start the Django application with Gunicorn
