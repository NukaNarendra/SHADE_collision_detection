# SHADE: Steganographic Hidden Agent Deviation Evaluation

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![NeurIPS Target](https://img.shields.io/badge/Target-NeurIPS%202026-orange.svg)](https://neurips.cc/)
[![Zero-FLOP Defense](https://img.shields.io/badge/Defense-CACC%20v3%20(2.6ms)-purple.svg)](#cross-agent-consistency-checking-cacc-v3)
[![Dashboard: Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](app/shade_dashboard.py)

> **Official Research Codebase & Benchmark Suite for Multi-Agent Steganographic Collusion and Scalable Oversight**  
> *Author:* **Nuka Venkata Narendra** (Department of Computer Science and Engineering, VR Siddhartha Engineering College)  
> *Target Venue:* Conference on Neural Information Processing Systems (NeurIPS 2026)

---

## 📑 Overview & Abstract

As autonomous Large Language Model (LLM) agents are increasingly delegated critical responsibilities in distributed workflows, multi-agent safety evaluations predominantly assume agents operate either benignly or through overt, human-readable adversarial exploits.

**SHADE** (*Steganographic Hidden Agent Deviation Evaluation*) is an empirical red-teaming framework and defense suite designed to probe **emergent linguistic steganography** and covert collusion between cooperating LLM agents operating under third-party semantic supervision.

```
                           +--------------------------------------+
                           |          Target Task Carrier         |
                           |      (GSM8K Multi-Step Reasoning)     |
                           +--------------------------------------+
                                               |
                                               v
+------------------+   Covert Channel    +------------------+   Extracted Canary   +--------------------+
|  Agent C_1       | ==================> |  Agent C_2       | ===================> | Steganographic     |
|  (Encoder)       |   (Natural Prose)   |  (Decoder)       |                      | Collusion Success  |
+------------------+                     +------------------+                      +--------------------+
         |                                         |
         +--------------------+--------------------+
                              |
                              v
         +---------------------------------------------------+
         |             Supervisory Inspection Layer          |
         |---------------------------------------------------|
         | [1] Semantic Monitor (Nemotron-120B / LLM-Judge)  |
         |     ❌ 60.0% Missed Detection Rate (MDR)          |
         |     ⏱️ 1,450 ms latency / ~120B FLOPs             |
         |---------------------------------------------------|
         | [2] CACC v3 Deterministic Defense Pipeline        |
         |     ✅ 96.1% Catch Rate (Zero Model Weights)      |
         |     ⏱️ 2.60 ms CPU Execution (Zero GPU FLOPs)     |
         +---------------------------------------------------+
```

### Key Empirical Findings ($N = 300$ Cross-Architecture Benchmark)
1. **Semantic Oversight Fragility:** Frontier "LLM-as-a-Judge" supervisory monitors (including Nemotron-120B Super-VL) exhibit an alarming **60.0% Missed Detection Rate (MDR)** against natural steganographic payloads.
2. **High Collusion Success Rate (CSR):** When task utility is preserved, colluding agents reliably transmit secret tokens with an overall **85.0% Collusion Success Rate** across 6 distinct model families.
3. **Turn Depth Scaling Law:** Collusion efficacy scales non-linearly with conversational interaction depth ($t$), expanding covert transmission capacity while diluting per-token anomaly signatures.
4. **Zero-FLOP Deterministic Hardening (CACC v3):** Our zero-weight defense pipeline achieves a **96.1% catch rate** across all 300 empirical trials in **2.60 ms** per interaction turn on a single CPU core, completely eliminating semantic blind spots (**100% detection in union**).

---

## 📊 Cross-Architecture Empirical Vulnerability Matrix

Evaluated across $N = 300$ controlled trials ($50$ trials per model architecture):

| Model Architecture | Provider / SDK | Trials ($N$) | Collusion Success (CSR) | Semantic Monitor Catch (MDR) | CACC v3 Catch Rate | Net Gain ($\Delta_{\text{sec}}$) | Blind Spots Caught |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **GLM 5.3** | TokenRouter | 50 | 38 (76.0%) | 4 / 38 (10.5%) | **38 / 38 (100.0%)** | **+89.5%** | 34 (89.5%) |
| **Groq Compound** | Groq SDK | 50 | 49 (98.0%) | 18 / 49 (36.7%) | **49 / 49 (100.0%)** | **+63.3%** | 31 (63.3%) |
| **Laguna XS 2.1** | NVIDIA NIM | 50 | 47 (94.0%) | 28 / 47 (59.6%) | **47 / 47 (100.0%)** | **+40.4%** | 19 (40.4%) |
| **GPT-OSS 120B** | NVIDIA NIM | 50 | 26 (52.0%) | 18 / 26 (69.2%) | **26 / 26 (100.0%)** | **+30.8%** | 8 (30.8%) |
| **Nemotron 3.5 Lightning** | NVIDIA NIM | 50 | 47 (94.0%) | 38 / 47 (80.9%) | **46 / 47 (97.9%)** | **+17.0%** | 9 (19.1%) |
| **Mistral Medium** | Mistral SDK | 50 | 48 (96.0%) | 47 / 48 (97.9%) | **39 / 48 (81.2%)** | -16.7% | 0 (0.0%) |
| **OVERALL SUMMARY** | **Multi-Provider** | **300** | **255 (85.0%)** | **153 / 255 (60.0%)** | **245 / 255 (96.1%)** | **+36.1%** | **101 (39.6%)** |

> **Key Takeaway:** Semantic oversight alone missed **102 out of 255** successful covert collusions. CACC v3 intercepted **101 of those 102 blind spots**, proving that deterministic statistical bounding is indispensable for multi-agent safety.

---

## 🛡️ Cross-Agent Consistency Checking (CACC v3)

CACC v3 operates as an ultra-fast, zero-weight statistical filter that eliminates the physical and mathematical bandwidth required for steganographic signaling without invoking secondary neural networks.

| Heuristic Component | Mathematical Formulation | Metric Measured | Mean Latency | Hardware Cost |
| :--- | :--- | :--- | :---: | :---: |
| **1. Character Shannon Entropy** | $H_{\text{char}}(m) = -\sum_{c \in \mathcal{A}} p(c) \log_2 p(c)$ | Lexical uniformization & symbol shifts | **0.42 ms** | Zero FLOPs |
| **2. Filtered Jaccard Overlap** | $J_{\text{content}}(m_1, m_2) = \frac{\|W_1 \cap W_2\|}{\|W_1 \cup W_2\|}$ | Content-word syntactic echoing | **0.85 ms** | Zero FLOPs |
| **3. Off-Domain Semantic Dispersion** | $D_{\text{disp}}(m, \mathcal{T}) = \frac{\|W_m \setminus \mathcal{V}_{\text{carrier}}\|}{\|W_m\|}$ | Carrier-task lexical drift | **1.20 ms** | Zero FLOPs |
| **4. Numeric Variance Analysis** | $\sigma^2_{\text{num}} = \frac{1}{\|K\|} \sum (v_k - \mu_v)^2$ | Digits manipulation & math perturbation | **0.08 ms** | Zero FLOPs |
| **5. Payload Bloat Computation** | $\rho_{\text{bloat}} = \frac{\text{len}(m)}{\text{len}_{\text{baseline}}}$ | Reasoning trace overhead expansion | **0.05 ms** | Zero FLOPs |
| **CACC v3 Total Pipeline** | **Composite Decision Tree** | **Comprehensive Covert Channel Detection** | **2.60 ms** | **Standard CPU Core** |

Compared to secondary LLM supervision ($\sim 1,450.0\text{ ms}$ on $4\times \text{H100 GPUs}$), CACC v3 is **$557\times$ faster** and consumes **0 GPU RAM**.

---

## 🖥️ Interactive Streamlit Dashboard

The repository includes a production-grade, 7-page interactive dashboard for visualizing empirical trial telemetry and conducting live red-teaming experiments.

```bash
streamlit run app/shade_dashboard.py
```

```
========================================================================================
                      SHADE RESEARCH ANALYTICS DASHBOARD
========================================================================================
[1] 📊 Executive Safety Scorecard       - Global KPIs, CSR, MDR, CACC v3 catch rate
[2] 🎯 Strategic 4-Quadrant Scatter     - Model risk profiling (High Collusion vs Catch)
[3] 🥧 Security Outcomes Matrix         - Donut breakdown of Blind Spots & Defense Union
[4] 📈 Turn Depth Scaling Laws          - Multi-turn interaction horizon dynamics
[5] 📉 Stacked Outcome Decomposition    - Model-by-model classification breakdown
[6] 🎛️ Sensitivity & Parameter Profiler - Live threshold tuning for CACC heuristics
[7] 🔬 Live Agent Collusion Sandbox     - Real-time multi-agent trial execution with
                                          live model switching dropdown
========================================================================================
```

### Page 7: Live Agent Collusion Sandbox
Conduct real-time interactive trials between colluding agents and test supervisory monitors on live LLM APIs:
- **Drop-down Model Selector:** Switch dynamically between:
  - `nvidia/nemotron-3.5-super-vl-120b-a12b` (NVIDIA NIM)
  - `nvidia/nemotron-3.5-lightning-30b-a3b` (NVIDIA NIM)
  - `nvidia/nemotron-3.5-bolt-e4b` (NVIDIA NIM)
  - `groq/compound` (Groq Cloud)
  - `mistral/medium` (Mistral AI)
  - `tokenrouter/glm-5.3-free` (TokenRouter)
- **Carrier Problem Selector:** Pre-loaded GSM8K arithmetic carrier tasks.
- **Steganographic Canary Customizer:** Define arbitrary covert secret tokens.
- **Turn Depth Slider ($t \in [2, 8]$):** Tune communication rounds.
- **Dual Live Inspection:** Real-time stream of Agent $C_1$, Agent $C_2$, Semantic Monitor verdict, and CACC v3 mathematical metric scores.

---

## 📁 Repository Structure

```
Collision_Detection/
├── app/
│   ├── shade_dashboard.py         # 7-page interactive Streamlit research dashboard
│   └── streamlit_app.py           # Standalone live collusion monitor interface
├── data/
│   ├── gsm8k_sample.json          # Curated arithmetic carrier task evaluation set
│   └── secrets_sample.json        # Standardized canary tokens (fruits, places, ciphers)
├── experiments/
│   ├── run_benchmark.py           # Automated N=300 & N=1500 benchmark runner
│   └── analyze_results.py         # Statistical analysis and metrics computation
├── paper/
│   ├── figures/                   # Vector PDFs and PNG figures for the paper
│   │   ├── fig1_architecture.png  # Complete SHADE architecture diagram
│   │   ├── fig2_detection_comparison.png
│   │   ├── fig3_quadrant_scatter.png
│   │   ├── fig4_contingency_donut.png
│   │   ├── fig5_scaling_law.png
│   │   ├── fig6_stacked_bar.png
│   │   ├── fig7_cacc_pipeline.png
│   │   └── fig8_csr_comparison.png
│   ├── sections/                  # Modular LaTeX sections (Sec 1-7, Appendix)
│   ├── references.bib             # 15 peer-reviewed bibliography entries
│   └── neurips_2026.sty           # NeurIPS 2026 conference style package
├── results/
│   ├── dashboard_figures/         # High-resolution publication plots (01 to 07)
│   ├── metrics/                   # Consolidated benchmark CSVs and KPI scores
│   ├── logs/                      # Trial logs documentation
│   └── raw_trial_logs_archive.zip # Compressed archive of all 556 individual trial logs
├── src/
│   ├── agents/
│   │   ├── base.py                # Multi-provider client wrapper (NVIDIA, Groq, Mistral)
│   │   └── steganographic_agents.py # Encoder (C1), Decoder (C2), and Supervisor implementations
│   ├── defense/
│   │   └── cacc_v3.py             # 5-heuristic CACC v3 statistical detection engine
│   └── config.py                  # Environment config and model provider mapping
├── SHADE_paper.pdf                # Full 15-page NeurIPS caliber research paper
├── requirements.txt               # Complete Python dependencies
├── .env.example                   # API configuration template
└── README.md                      # Project documentation (this file)
```

---

## 🚀 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/NukaNarendra/SHADE_collision_detection.git
cd SHADE_collision_detection
```

### 2. Set Up Virtual Environment
```bash
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Linux / macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
Copy the `.env.example` file to `.env` and fill in your API credentials:
```bash
cp .env.example .env
```
Supported keys:
- `NVIDIA_API_KEY`: Available at [build.nvidia.com](https://build.nvidia.com) (provides free inference credits for Nemotron models).
- `GROQ_API_KEY`: Available at [console.groq.com](https://console.groq.com).
- `MISTRAL_API_KEY`: Available at [console.mistral.ai](https://console.mistral.ai).
- `TOKENROUTER_API_KEY`: Available at TokenRouter.

### 5. Launch the Dashboard
```bash
streamlit run app/shade_dashboard.py
```
Open your browser to `http://localhost:8501` to explore the benchmark or test live models on Page 7.

---

## 📜 Citation & Research Paper

The complete 15-page research paper detailing the theoretical bounds, steganographic capacities, and full experimental evaluations is compiled as [`SHADE_paper.pdf`](SHADE_paper.pdf).

If you find this work or the SHADE framework useful in your research, please cite:

```bibtex
@inproceedings{narendra2026shade,
  title     = {SHADE: Probing Emergent Linguistic Steganography and Semantic Oversight Failures in Multi-Agent LLMs},
  author    = {Narendra, Nuka Venkata},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  year      = {2026},
  url       = {https://github.com/NukaNarendra/SHADE_collision_detection}
}
```

---

## ⚖️ Ethical & Dual-Use Statement

This research is designed to expose structural blind spots in contemporary multi-agent oversight frameworks to enable proactive defense development. All experiments conducted in this study utilize non-malicious arithmetic tasks (GSM8K) and benign lexical canary tokens. The CACC v3 inspection heuristics are open-sourced under the MIT License to empower enterprise agent orchestrators with zero-latency defense tools.
