# LLM Orchestrator

## Overview
The LLM Orchestrator is a powerful and modular Python library designed to manage and execute AI agents, leveraging Large Language Models (LLMs) for natural language understanding and vector databases for efficient tool retrieval. It provides a structured framework for defining agents and their tools, enabling dynamic execution based on user queries.

## Key Features
-   **LLM Integration:** Seamlessly integrates with Google Gemini for text generation and embeddings.
-   **Agent Management:** Define, register, and manage AI agents with structured tools and HTTP configurations.
-   **Vector-Based Tool Retrieval:** Utilizes Qdrant for efficient semantic search and retrieval of relevant tools based on user queries.
-   **Modular Design:** Built with a factory pattern for LLM clients and memory managers, allowing for easy extension and integration of new components.
-   **Schema Validation:** Ensures agent definitions adhere to a predefined schema for data integrity.

## Core Components
-   **`LLMOrchestrator`**: The main entry point, orchestrating agent registration, warm-up (saving and vectorizing agents), and query invocation.
-   **`AgentLoader`**: Handles the loading, validation, and vectorization of agent definitions from specified URLs into the system and Qdrant.
-   **`Executor`**: Responsible for processing user queries, finding the most relevant tools via vector search, and executing them.
-   **`QdrantHelper`**: A singleton utility for managing connections to Qdrant, creating collections, ensuring indexes, and performing upsert operations.
-   **`LLMGemini`**: Concrete implementation for interacting with the Google Gemini API for both text generation and embedding generation.
-   **`InMemoryManager`**: A thread-safe in-memory solution for temporary data storage, part of the extensible memory management system.

## How It Works
1.  **Agent Registration:** Agents, defined in structured JSON files (adhering to `AgentSchema`), are registered with the orchestrator. Their tools are then vectorized using the LLM and stored in Qdrant.
2.  **Query Execution:** When a user submits a query, the orchestrator:
    *   Generates an embedding for the query.
    *   Searches Qdrant for semantically similar tools.
    *   Uses the LLM to select the best tool and extract necessary parameters from the query.
    *   Executes the selected tool via an HTTP request.
    *   Generates a user-friendly response using the LLM based on the tool's output.

## Installation
This project uses Poetry for dependency management.
To install the dependencies, navigate to the project root and run:
```bash
poetry install
```
Ensure you have a `.env` file with your `GEMINI_API_KEY` and Qdrant configuration (if not using defaults).

## Usage
A basic example of how to use the orchestrator is provided in `main.py`:
```python
from llm_orchestrator import LLMOrchestrator
from llm_orchestrator.types.agents import Agent
async def main():
    llm_orchestrator = LLMOrchestrator()
    
    await llm_orchestrator.register_agents(
        [
            Agent(
                name="AgentTest",
                urlAgentFile="https://raw.githubusercontent.com/Azzarnuji/llm_orchestrator/refs/heads/main/test_agents/agent-test/agent.json"
            )
        ]
    )
    await llm_orchestrator.warm_up()
    
    while True:
        query = input("Enter your query: ")
        if query == "exit":
            break
        
        # STREAM EXAMPLE
        response = await llm_orchestrator.invoke_query(query, stream=True)
        for chunk in response:
            print(chunk.text, end="")
        print("\n")
        
        #NON STREAM EXAMPLE
        # response = await llm_orchestrator.invoke_query(query)
        # print(response.text)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

# LLM Orchestrator

## Gambaran Umum
LLM Orchestrator adalah pustaka Python yang kuat dan modular yang dirancang untuk mengelola dan mengeksekusi agen AI, memanfaatkan Large Language Models (LLM) untuk pemahaman bahasa alami dan basis data vektor untuk pengambilan alat yang efisien. Ini menyediakan kerangka kerja terstruktur untuk mendefinisikan agen dan alat mereka, memungkinkan eksekusi dinamis berdasarkan kueri pengguna.

## Fitur Utama
-   **Integrasi LLM:** Terintegrasi secara mulus dengan Google Gemini untuk pembuatan teks dan embeddings.
-   **Manajemen Agen:** Mendefinisikan, mendaftarkan, dan mengelola agen AI dengan alat terstruktur dan konfigurasi HTTP.
-   **Pengambilan Alat Berbasis Vektor:** Memanfaatkan Qdrant untuk pencarian semantik yang efisien dan pengambilan alat yang relevan berdasarkan kueri pengguna.
-   **Desain Modular:** Dibangun dengan pola pabrik (factory pattern) untuk klien LLM dan manajer memori, memungkinkan perluasan dan integrasi komponen baru dengan mudah.
-   **Validasi Skema:** Memastikan definisi agen mematuhi skema yang telah ditentukan untuk integritas data.

## Komponen Inti
-   **`LLMOrchestrator`**: Titik masuk utama, mengorkestrasi pendaftaran agen, pemanasan (menyimpan dan memvektorisasi agen), dan pemanggilan kueri.
-   **`AgentLoader`**: Menangani pemuatan, validasi, dan vektorisasi definisi agen dari URL yang ditentukan ke dalam sistem dan Qdrant.
-   **`Executor`**: Bertanggung jawab untuk memproses kueri pengguna, menemukan alat yang paling relevan melalui pencarian vektor, dan mengeksekusinya.
-   **`QdrantHelper`**: Utilitas singleton untuk mengelola koneksi ke Qdrant, membuat koleksi, memastikan indeks, dan melakukan operasi upsert.
-   **`LLMGemini`**: Implementasi konkret untuk berinteraksi dengan Google Gemini API untuk pembuatan teks dan embeddings.
-   **`InMemoryManager`**: Solusi penyimpanan data sementara dalam memori yang aman untuk thread, bagian dari sistem manajemen memori yang dapat diperluas.

## Cara Kerja
1.  **Pendaftaran Agen:** Agen, yang didefinisikan dalam file JSON terstruktur (sesuai dengan `AgentSchema`), didaftarkan ke orkestrator. Alat-alat mereka kemudian divetorisasi menggunakan LLM dan disimpan di Qdrant.
2.  **Eksekusi Kueri:** Ketika pengguna mengirimkan kueri, orkestrator:
    *   Menghasilkan embedding untuk kueri.
    *   Mencari Qdrant untuk alat yang secara semantik serupa.
    *   Menggunakan LLM untuk memilih alat terbaik dan mengekstrak parameter yang diperlukan dari kueri.
    *   Mengeksekusi alat yang dipilih melalui permintaan HTTP.
    *   Menghasilkan respons yang mudah dipahami pengguna menggunakan LLM berdasarkan output alat.

## Instalasi
Proyek ini menggunakan Poetry untuk manajemen dependensi.
Untuk menginstal dependensi, navigasikan ke root proyek dan jalankan:
```bash
poetry install
```
Pastikan Anda memiliki file `.env` dengan `GEMINI_API_KEY` dan konfigurasi Qdrant Anda (jika tidak menggunakan default).

## Penggunaan
Contoh dasar penggunaan orkestrator disediakan di `main.py`:
```python
from llm_orchestrator import LLMOrchestrator
from llm_orchestrator.types.agents import Agent
async def main():
    llm_orchestrator = LLMOrchestrator()
    
    await llm_orchestrator.register_agents(
        [
            Agent(
                name="AgentTest",
                urlAgentFile="https://raw.githubusercontent.com/Azzarnuji/llm_orchestrator/refs/heads/main/test_agents/agent-test/agent.json"
            )
        ]
    )
    await llm_orchestrator.warm_up()
    
    while True:
        query = input("Enter your query: ")
        if query == "exit":
            break
        
        # STREAM EXAMPLE
        response = await llm_orchestrator.invoke_query(query, stream=True)
        for chunk in response:
            print(chunk.text, end="")
        print("\n")
        
        #NON STREAM EXAMPLE
        # response = await llm_orchestrator.invoke_query(query)
        # print(response.text)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```