# Flask Application

This is a simple Flask web application that serves an HTML view.

## Project Structure

```
flask-app
├── app.py
├── templates
│   └── index.html
├── static
│   ├── css
│   │   └── styles.css
│   └── js
│       └── scripts.js
└── README.md
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd flask-app
   ```

2. **Create a virtual environment**:
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install the required packages**:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the application, execute the following command:

```
python app.py
```

The application will be accessible at `http://127.0.0.1:5000/`.

## Usage

Once the application is running, you can visit the root URL to see the HTML view rendered from the `index.html` template. You can modify the HTML, CSS, and JavaScript files to customize the application as needed.
