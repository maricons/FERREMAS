from flask_app.app import app
import os

if __name__ == "__main__":
    # Lee el puerto de la variable de entorno PORT, o usa 8000 por defecto (para local)
    port = int(os.environ.get("PORT", 8000))

    app.run(debug=True, host="0.0.0.0", port=port)
