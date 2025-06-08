# Mispricing Detective

This project contains a Flask backend and a standalone React frontend for analysing mispriced stocks.

## Backend Setup

1. **Create and activate a Python virtual environment** (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies** using the provided `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download TextBlob corpora** (required for sentiment analysis):
   ```bash
   python -m textblob.download_corpora
   ```

4. **Set the required environment variables** so the application can access the external APIs:
   - `FMP_API_KEY` – your Financial Modeling Prep API key
   - `SEC_API_KEY` – your sec-api.io API key
   
   Example on Linux/macOS:
   ```bash
   export FMP_API_KEY=<your FMP key>
   export SEC_API_KEY=<your SEC key>
   ```

5. **Run the backend** with Flask:
   ```bash
   flask --app main run
   ```
   The API will be available at `http://127.0.0.1:5000`.

## Frontend Setup

The React frontend is provided as a single file named `Mispricing Detective - React Frontend`. Create a new React project and replace the default `App.js` with the contents of this file.

1. **Create a React application** (requires Node.js and npm):
   ```bash
   npx create-react-app mispricing-detective-ui
   cd mispricing-detective-ui
   ```

2. **Install additional dependencies** used by the frontend:
   ```bash
   npm install recharts lucide-react
   ```

3. **Replace `src/App.js`** with the code from `Mispricing Detective - React Frontend`.

4. **Start the React development server**:
   ```bash
   npm start
   ```
   The UI will open in your browser at `http://localhost:3000` and will interact with the backend running on port `5000`.

## Running the Application

Run both the backend and the frontend as described above. Once both servers are running, visit `http://localhost:3000` in your browser. Enter a ticker symbol to fetch and analyse data via the backend API.

