# أنشئ README محدث
@"
# 5G Network Simulator Pro 🚀

![Build](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)

## 🔴 Live Demo
**[https://network-simulator-pro.onrender.com](https://network-simulator-pro.onrender.com)**

> Note: Free tier may sleep after inactivity. First load takes ~30 seconds.

## 📸 Screenshots
![Dashboard](api-docs.png)

## ✨ Features
- Real-time 5G network simulation
- WebSocket live updates
- Interactive dashboard
- REST API with Swagger docs
- Device management (IoT, Vehicle, Smartphone)
- Network slices (eMBB, URLLC, mMTC)
- Metrics export to JSON

## 🏗️ Architecture
\`\`\`
Simulator → FastAPI → WebSocket/REST → Dashboard
           ↓
        Metrics Export
\`\`\`

## 🚀 Quick Start
\`\`\`bash
# Clone
git clone https://github.com/mohammedsubo/network-simulator-pro.git
cd network-simulator-pro

# Install
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Run
python src/api.py
# Open http://localhost:8000
\`\`\`

## 📚 API Documentation
- Interactive Docs: `/docs`
- ReDoc: `/redoc`
- Health Check: `/health`

## 🛠️ Tech Stack
- **Backend**: FastAPI, Python 3.10+
- **Real-time**: WebSocket
- **Frontend**: HTML5, Chart.js, Bootstrap 5
- **Deployment**: Render.com

## 📈 Roadmap
- [ ] PostgreSQL integration
- [ ] JWT authentication
- [ ] Docker support
- [ ] Export to PDF
- [ ] Mobile app

## 📝 License
MIT

---
**Made with ❤️ by Mohammed**
"@ | Set-Content README.md

git add README.md
git commit -m "Update README with live demo"
git push origin main