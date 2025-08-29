# 5G Network Simulator Pro 🚀

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://network-simulator-pro.onrender.com)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?logo=fastapi)
![WebSocket](https://img.shields.io/badge/WebSocket-Enabled-orange)

## 🔴 Live Demo

**[https://network-simulator-pro.onrender.com](https://network-simulator-pro.onrender.com)**

> ⚠️ **Note**: Free hosting tier may take 30-50 seconds to wake up on first visit. Please be patient.

## 📸 Screenshots

![Dashboard Preview](api-docs.png)

## 🎯 Overview

A real-time 5G network simulator with interactive dashboard, built to demonstrate network slicing, device management, and performance monitoring capabilities of 5G networks. Features WebSocket-based live updates and comprehensive REST API.

## ✨ Features

### Core Functionality
- **Real-time Network Simulation** - Live metrics updated every 2 seconds
- **5G Network Slices** - eMBB, URLLC, mMTC support
- **Device Management** - Add/remove IoT devices, smartphones, and vehicles
- **Performance Monitoring** - Track latency, throughput, and network load
- **Data Export** - Export metrics to JSON format
- **WebSocket Support** - Real-time bidirectional communication

### Technical Features
- RESTful API with automatic documentation
- Interactive Swagger/OpenAPI interface
- Health check endpoints for monitoring
- CORS enabled for cross-origin requests
- Responsive Bootstrap 5 dashboard
- Chart.js for dynamic visualizations

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **WebSockets** - Real-time communication
- **Pydantic** - Data validation

### Frontend
- **HTML5/CSS3** - Markup and styling
- **Bootstrap 5** - UI framework
- **Chart.js** - Data visualization
- **JavaScript** - Interactive functionality

### Deployment
- **Render.com** - Cloud hosting
- **GitHub Actions** - CI/CD
- **Docker** - Containerization (optional)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip package manager

### Local Installation

```bash
# Clone repository
git clone https://github.com/mohammedsubo/network-simulator-pro.git
cd network-simulator-pro

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/api.py