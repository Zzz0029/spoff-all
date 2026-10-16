# spoff-all

Interactive Security Proof of Concept (PoC) demonstration suite and directory navigator.

## 🚀 Overview
A comprehensive collection of client-side web and browser security PoCs including:
- Address Bar & URL Spoofing
- Download & File Spoofing
- Origin & Permission Chooser Spoofing
- URL Scheme & Tel Protocol Handling
- UI Redressing & Bypass
- Standalone Root PoCs (XSS, CSRF, etc.)

## 🌐 Live Access & Deployment
This repository is configured to be hosted as a static site on **Vercel** or **GitHub Pages**.
- Entry point: `index.html`
- Configuration: `vercel.json`

## 🛠️ Rebuild Directory Listing
If you add or update PoC files, run:
```bash
python build_index.py
```
