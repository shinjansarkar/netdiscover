# NetDiscover Deployment Guide

This guide explains how to take your completely detached, secure backend and frontend and deploy them to the cloud using Render (for the Python backend) and Vercel (for the Next.js frontend).

> [!WARNING]
> **Limitations of Cloud Hosting a Network Scanner:**
> NetDiscover is designed to scan local network architectures. When you deploy the backend to Render, the application will be running inside Render's cloud data centers. It will no longer have access to your local home network (like `192.168.x.x`). You will only be able to scan public IP addresses, domains, or Render's internal infrastructure. 
>
> If your goal is to scan your own local WiFi, you *must* keep the backend running locally on your laptop, though you can still deploy the frontend to Vercel and connect it to your local backend (using tools like Ngrok or Cloudflare Tunnels).

## 1. Preparing the Repository
Before you deploy, you must push your entire project to a **GitHub repository**.
Your repository should look like this:
```text
netdiscover/
├── client/       <-- Next.js app
├── server/       <-- Python backend code
└── .gitignore
```
*(Make sure `.env` and `netdiscover.db` are strictly ignored and not pushed!)*

---

## 2. Deploying the Backend on Render
Render is perfect for hosting Python Flask applications.

1. Go to [Render.com](https://render.com/) and sign in with GitHub.
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository containing the NetDiscover code.
4. Configure the Web Service:
   - **Name:** `netdiscover-backend` (or whatever you prefer)
   - **Language:** `Python 3`
   - **Branch:** `main`
   - **Root Directory:** `server`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
5. **Environment Variables:**
   Scroll down to the Environment Variables section and add your secret key:
   - **Key:** `NETDISCOVER_API_KEY`
   - **Value:** *(paste the 64-character hex key generated earlier)*
6. Click **Create Web Service**. Render will build and deploy your backend. 
7. **Copy the URL:** Once live, copy your backend URL (e.g., `https://netdiscover-backend.onrender.com`).

> [!NOTE]
> **Database Persistence:** Render's free tier uses an ephemeral file system. Because we use SQLite, your `netdiscover.db` file will be wiped out every time the Render server restarts or goes to sleep.

---

## 3. Deploying the Frontend on Vercel
Vercel is the creator of Next.js and provides the best hosting experience for the frontend.

1. Go to [Vercel.com](https://vercel.com/) and sign in with GitHub.
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository.
4. Configure the Project:
   - **Project Name:** `netdiscover-ui`
   - **Framework Preset:** `Next.js`
   - **Root Directory:** Click Edit and select `client`. *(This tells Vercel to only build the Next.js code)*.
5. **Environment Variables:**
   Expand the Environment Variables section and add the following two keys to connect it to your newly deployed backend:
   
   - **Key:** `NEXT_PUBLIC_API_KEY`
     - **Value:** *(must exactly match the key you put in Render!)*
   
   - **Key:** `NEXT_PUBLIC_API_BASE_URL`
     - **Value:** `https://your-render-url-here.onrender.com/api` *(Make sure you append `/api` to the end!)*

6. Click **Deploy**. Vercel will build your Next.js application and provide you with a live domain URL!

---

## 4. How They Communicate
Because we set the `NEXT_PUBLIC_API_BASE_URL` environment variable in Vercel, your Next.js application automatically knows to stop looking at `http://localhost:5000/api` and instead route all its fetch requests across the internet to your Render URL.

Because we set the `NEXT_PUBLIC_API_KEY` in Vercel, the frontend automatically attaches your secret key to the headers of every request. The Render backend intercepts the request, checks the `X-API-Key` header against its own `NETDISCOVER_API_KEY` variable, verifies they match, and grants access!
