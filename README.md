## AI-Health-Supervisor-Agent

A multi-agent AI system designed to provide personalized health guidance across fitness, diet, and mental wellness, coordinated by a central **Supervisor Agent**.

This AI assistant helps users improve their well-being by generating:
- 🏋️ Customized workout plans  
- 🥗 Healthy meal suggestions  
- 🧘 Mindfulness and stress-reducing tips  


![My Image](https://github.com/Mercytopsy/AI-Health-Supervisor-Agent/blob/main/Architectural_Diagram.png)







### 🛠 Tech Stack
- LangGraph – for building the multi-agent state machine
- LangChain – for Tool orchestration
- Qwen2.5:14b – for agent reasoning and responses
- Streamlit – for frontend
- Python – main programming language


### 📦 Installation & Setup

#### 1. Clone the repository
```bash
git clone https://github.com/Mercytopsy/AI-Health-Supervisor-Agent.git
cd AI-Health-Supervisor-Agent
```
#### 2. Install dependencies
```bash
pip install -r requirements.txt
```
#### 3. Set up Qwen 
```bash
ollama pull qwen2.5:14b
```
#### 4. Add [Fitness](https://api-ninjas.com/profile) & [Dietitian](https://spoonacular.com/food-api/console#Profile)  API Key
```bash
Create a .env file:
```

#### 5. Run the App
```bash
streamlit run main.py
```
