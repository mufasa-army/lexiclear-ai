# ⚖️ LexiClear — AI-Powered Legal Document Auditor & Copilot

> Transforming complex legal legalese into plain, actionable transparency using Google Gemini.

🚀 **Live Demo:** [https://lexiclear-ai.streamlit.app](https://lexiclear-ai.streamlit.app)

---

## 📌 Problem Statement
Legal documents, NDAs, employment contracts, and service agreements are intentionally dense and full of complex legal jargon. Everyday users, freelancers, and small business owners often sign predatory contracts with hidden lock-ins, excessive penalties, and broad IP surrenders without having access to expensive legal counsel.

## 💡 Solution: LexiClear
**LexiClear** is an automated GenAI legal copilot designed to bridge the accessibility gap in legal navigation. By combining structured clause auditing with Gemini models, it turns intimidating legal documents into clear, risk-scored insights.

### 🌟 Key Features
- **Zero-Jargon Simplification:** Converts multi-page legal agreements into plain, layman English summaries.
- **Automated Red-Flag Radar:** Pinpoints predatory clauses (harsh non-competes, IP grabs, unilateral payment withholdings) and grades their risk severity (High / Medium / Low).
- **Interactive Document Q&A:** Grounded retrieval and question-answering with strict clause citations to eliminate hallucinations.
- **Pre-Signing Lawyer Checklist:** Generates an actionable list of targeted questions to consult a legal professional before signing.
- **High Performance & Accessibility:** Employs `@st.cache_data` for zero-redundancy PDF text caching, high-contrast accessible UI elements, and WCAG-aligned form labeling.
- **Resilient AI Architecture:** Built-in multi-model fallback across Gemini models ensuring uninterrupted reliability against API timeouts.

---

## 🛠️ Architecture & Tech Stack
- **AI Engine:** Google Gemini (`gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-2.5-flash`) via `google-genai` SDK
- **Frontend / Application Layer:** Streamlit
- **Document Processing:** PyPDF
- **Quality Assurance & Testing:** Pytest
- **Prompt Architecture:** Strict JSON Schema generation + Context-Grounded Document QA

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A Google AI Studio API Key ([Get one here](https://aistudio.google.com/))

### Installation & Run
1. Clone the repository:
```bash
git clone [https://github.com/mufasa-army/lexiclear-ai.git](https://github.com/mufasa-army/lexiclear-ai.git)
cd lexiclear-ai