# Customer Signal Analyzer

AI-powered communication analysis tool designed for Customer Success teams to detect emotional tone, resistance signals, and engagement patterns in customer emails and messages.

## Overview

Customer Success Managers often need to interpret subtle signals from customer communication. This tool analyzes written messages and highlights potential indicators such as:

- Customer frustration
- Passive resistance
- Engagement level
- Adoption risk signals

The goal is to help CSMs respond with better emotional intelligence and more strategic messaging.

## Example

Customer message:

"We've just been really busy and haven't had time to review the platform yet."

Detected signals:

- Low engagement
- Potential adoption stall
- Passive resistance indicator

Recommended response strategy:

- Reinforce value
- Reduce perceived effort
- Offer guided enablement

## Features

- AI-based communication analysis
- Psychological signal detection
- Customer sentiment interpretation
- Clean Gradio web interface
- Lightweight Python implementation

<img width="896" height="1339" alt="image" src="https://github.com/user-attachments/assets/a57443de-63ac-4b3d-9669-cfc5e99da315" />
<img width="1370" height="806" alt="image" src="https://github.com/user-attachments/assets/0292e14f-c071-4eca-9d81-a4701c607c9c" />
<img width="1350" height="811" alt="image" src="https://github.com/user-attachments/assets/8aade7fa-5b6b-4f88-9af3-3314b49e9a69" />
<img width="898" height="978" alt="image" src="https://github.com/user-attachments/assets/a462aee0-fd33-478d-8170-8b445b5cabd9" />




## Technology

- Python
- OpenAI API
- Gradio UI
- dotenv for environment management

## Run Locally

Clone the repository:
git clone https://github.com/YOUR_USERNAME/customer-signal-analyzer.git


Navigate into the folder:


cd customer-signal-analyzer


Create virtual environment:


python3 -m venv venv
source venv/bin/activate


Install dependencies:


pip install -r requirements.txt


Add your API key:


nano .env

OPENAI_API_KEY="your_key_here"


Run the application:


python app_gradio.py


## Author

Josephine Gutierrez  
Customer Success | Technical Account Management | Cybersecurity

Save:

CTRL + O
ENTER
CTRL + X
3️⃣ Initialize Git
git init
4️⃣ Add files
git add .
5️⃣ Commit
git commit -m "Initial commit: Customer Signal Analyzer AI tool"
6️⃣ Create GitHub repo

Go to GitHub and create a repo called:

customer-signal-analyzer

Do NOT add README there (you already made one).

7️⃣ Connect repo and push

Replace YOUR_USERNAME with your GitHub username.

git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/customer-signal-analyzer.git
git push -u origin main
When done

Your GitHub will show:

customer-signal-analyzer
 ├── analyzer.py
 ├── scoring.py
 ├── taxonomy.py
 ├── app_gradio.py
 ├── banner.png
 ├── README.md
 ├── requirements.txt
