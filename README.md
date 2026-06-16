# 📈 DataAgent AI — Enterprise Business Intelligence

An automated, token-efficient Enterprise Business Intelligence (BI) dashboard powered by **Gemini 2.0 Flash**. This application allows users to upload multiple datasets, auto-detects relational data schemas, visualizes instant financial analytics (P&L), and provides an interactive AI Chat Agent capable of providing precise business insights without exploding API token usage.

Built natively with **Streamlit**, **Pandas**, and **Plotly**.

---

## ✨ Key Features

* 📁 **Multi-Dataset Support:** Upload multiple CSV files simultaneously and switch seamlessly between them via a unified dashboard interface.
* 🧠 **Auto-Heuristic Schema Mapping:** Automatically detects critical business columns such as *Dates, Revenue, Cost (HPP), Quantities,* and *Product Categories* based on smart keyword matching.
* 📈 **Instant P&L Performance Summary:** Real-time generation of Executive Dashboards tracking Total Revenue, Total Cost, Net Profit, and Profit Margins.
* 🤖 **Token-Efficient AI Insights:** Features a dynamic background aggregation system. Instead of feeding thousands of raw data rows into the LLM, it processes compressed summaries and true aggregates, keeping latency low and API costs minimal.
* 🔄 **State Isolation & Memory Cleansing:** Automatically flushes the AI chat memory upon switching datasets to avoid data leakage and cross-contamination.
* 🛠️ **Custom Chart Builder:** Provides a manual drag-and-drop styled visualization workbench for bespoke analytical deep dives.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your system.

### 2. Install Dependencies
Buka terminal di dalam folder proyek lo, lalu install semua library yang dibutuhkan dengan mengetik perintah: pip install -r requirements.txt

### 3. Run the Application
Jalankan server lokal Streamlit dengan mengetik perintah: streamlit run app.py

---

## ⚙️ Configuration & API Key

To use the **AI Insights** tab, you need a Gemini API Key:
1. Claim a free API Key at Google AI Studio.
2. Input the key securely into the application's sidebar password field.
3. The built-in connection tester will automatically validate the token and initialize the AI Agent interface.

---

## 📄 License

Distributed under the **MIT License**. See LICENSE for more information.

---

## 👨‍💻 Developer Profile

* **Developer:** Muhammad Abdurrasyid Fahrurozi
* **LinkedIn:** https://www.linkedin.com/in/m-abdurrasyid/
* **GitHub Repository:** https://github.com/RsydMathTech/agent-ai-bi
* **Company:** RsydMathTech

*"Turning raw enterprise data into precise, automated business actions."*
