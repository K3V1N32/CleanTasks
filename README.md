## Version
v1.0.0

# CleanTasks

A full-stack REST API task management web application with AI-powered task summaries and breakdowns.

Built with FastAPI, SQAlchemy, llama3 LLM and vanilla JavaScript, this project demonstrates REST API design, authentication, and AI integration.

---
## Considerations
This project is meant as a local web app to help me build skills with REST API, SQL interaction, AI integration, Authentication and UX Design, it is by no means a production level tool and is more of a fun project than a real task app so far. I have many improvements and ideas for the future of this app so keep an eye out if you enjoy this style of task app!

---

## Features

### Authentication
- User registration and login
- JWT-based authentication
- Persistent sessions (auto-login with token validation)
- Secure logout (clears stored token)

### Task Management
- Create, view, update, and delete tasks
- Inline editing UI
- Collapsible task cards for clean layout

### AI Integration
- Automatically generates:
  - Task summaries
  - Step-by-step breakdowns (subtasks)
- AI results cached in database for performance
- Manual “Regenerate AI” option

### Frontend UX
- Toast notifications (success, error, info)
- Expandable task sections to prevent clutter with many tasks
- Loading spinner with overlay (prevents user spam)
- Dynamic UI updates (no page reloads)
- User context displayed in header and browser tab

---

## Tech Stack

**Backend**
- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT Authentication

**Frontend**
- HTML
- CSS
- Vanilla JavaScript (no frameworks)

**AI**
- ollama running llama3 locally

---

## Screenshots

> *(Add screenshots here later for extra polish)*

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/ai-task-manager.git
cd ai-task-manager
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
Create a .env file:
```env
SECRET_KEY=TOKEN SECRET KEY GOES HERE
DATABASE_URL=URL TO DATABASE GOES HERE
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MINUTES=30
```

### 5. Spin up ollama-llama3
1. Goto https://ollama.com/ and install ollama.
2. Once installed, run the command **ollama run llama3**
3. After a couple of minutes of download,
4. llama3 will be up and running, and ready for the backend to connect!

### 6. Run the backend server
```bash
uvicorn app.main:app --reload
```

### 7. Open index.html in browser
- Host the html page or just directly open the index.html file
- Register a user and begin creating tasks!

## Design Decisions

### AI Generation Strategy
AI summaries and breakdowns are generated:

- On task creation
- On task update
- On manual regeneration

This avoids unnecessary repeated API calls and improves performance.

---
### Authentication Handling
- JWT tokens stored in localStorage
- Token validated on page load via /users/me
- Invalid tokens are cleared automatically

---
### UX Considerations
- Loading spinner with page overlay prevents repeated AI requests
- Toast notifications replace blocking alerts
- Collapsible UI keeps interface clean and scalable

---
## Future Improvements
- Task completion tracking
- Add multiple options for which AI to prompt for response
- Filtering and sorting
- Due dates and priorities
- Deployment (Render / Railway / etc.)
- Improved UI styling (React or component library)

---
## What I Learned
- Designing RESTful APIs with proper separation of concerns
- Handling authentication and session persistence
- Managing async UI state and user feedback
- Integrating AI into a real-world application
- Balancing features vs. performance

---
## Contact
Feel free to reach out or check out more of my work:
- GitHub: https://github.com/K3V1N32