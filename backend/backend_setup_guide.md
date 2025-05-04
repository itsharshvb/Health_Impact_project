

# Health Impact Prediction Backend Setup

This guide will help you set up and run the backend of the Health Impact Prediction project.

## Folder Structure

```
health_impact_project/
├── backend/
│   └── src/
│       └── main.py           # Main FastAPI application
├── requirements.txt          # List of dependencies
└── .gitignore                # Git ignore file (e.g., for virtual environment)
```

## Setup Instructions

Follow these steps to set up the backend:

### 1. **Create a Virtual Environment**

To start, you need to create a virtual environment to isolate your project dependencies. Follow the instructions below depending on your operating system:

#### **For Windows:**

1. Open a command prompt or PowerShell window in the project directory.
2. Run the following command to create a virtual environment named `venv`:

   ```bash
   python -m venv venv
   ```

#### **For macOS/Linux:**

1. Open a terminal window in the project directory.
2. Run the following command to create a virtual environment named `venv`:

   ```bash
   python3 -m venv venv
   ```

### 2. **Activate the Virtual Environment**

Activate the virtual environment based on your operating system:

#### **For Windows:**

```bash
.\venv\Scripts\activate
```

#### **For macOS/Linux:**

```bash
source venv/bin/activate
```

Once activated, your command prompt/terminal should show `(venv)` at the beginning of the line, indicating the virtual environment is active.

### 3. **Install Dependencies from `requirements.txt`**

With the virtual environment activated, install the necessary dependencies for the project by running:

```bash
pip install -r requirements.txt
```

This will install all the libraries listed in the `requirements.txt` file (e.g., FastAPI, Uvicorn, SQLAlchemy, etc.).

### 4. **Run the FastAPI Application**

To start the FastAPI backend, run the following command:

```bash
uvicorn src.main:app --reload
```

- This will start the FastAPI application, with auto-reload enabled, so it will restart the server automatically when you make code changes.

The app should now be accessible at `http://127.0.0.1:8000`.

You can open a browser or use tools like **Postman** or **cURL** to interact with the API.

### 5. **Access API Documentation**

Once the FastAPI application is running, you can visit the interactive API documentation at:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### 6. **Deactivating the Virtual Environment**

After you're done working, you can deactivate the virtual environment by running:

```bash
deactivate
```

This will return you to your global Python environment.

## Notes

- Ensure that you have Python 3.7 or higher installed to run the FastAPI project.
- The virtual environment folder (`venv`) is ignored by Git. If you haven't created it yet, add `venv/` to your `.gitignore` file to ensure it's not tracked by version control.

---

