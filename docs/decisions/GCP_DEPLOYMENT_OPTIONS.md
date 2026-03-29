# 🌌 GCP Deployment Enlightenment

## Introduction to the Google Cloud Platform
Since you're new to GCP, think of it as a giant LEGO set of professional tools. For our Saloon Marketplace, we only need three specific "bricks."

---

## 1. Cloud Run (The Backend Engine) 🚀
**What it is**: A "Serverless Container" service.
- **How it works**: We give Google our Docker container. They run it only when requested.
- **Why it's perfect for us**: 
    - **Scale-to-Zero**: If no one is using the site, Google turns the container off and charges you **$0**.
    - **Dead Simple**: We don't have to manage OS updates, firewalls, or SSL certificates. Google handles "Auto-HTTPS" for us.

## 2. Cloud SQL (The Database Vault) 🔒
**What it is**: A managed PostgreSQL service.
- **How it works**: Google runs the database for us. 
- **Why it's perfect for us**:
    - **Safety**: It takes automatic backups every night. If you mess up the DB, you can "travel back in time" to fix it.
    - **Reliability**: Pro-grade storage that never fails.

## 3. Artifact Registry (The Container Garage) 📦
- This is where we will "store" our built backend containers before Google Cloud Run pulls them to start the site.

---

## 🏗️ The Deployment Workflow
1. **Local**: We build the docker image (`docker build`).
2. **Push**: We send that image to Google Cloud.
3. **Deploy**: We tell Cloud Run to start using that image.
4. **Result**: Your app is live at `https://saloon-app-random-id.a.run.app`.

---

## 💰 The "Free Tier" Benefit
Google Cloud offers a "Free Tier" for Cloud Run (first 2 million requests per month) and a $300 credit for new accounts. For this project, you will likely pay **nothing** for months.
