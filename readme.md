
# AI Image Generator

This is a web-based AI Image Generator application that leverages a deep learning model to generate images from textual descriptions.

## Requirements

Before running the application, make sure you have the necessary Python packages installed. You can install the required dependencies using:

```bash
pip install -r requirements.txt
```

Additionally, you will need to create a `.env` file in the root directory to store environment-specific variables.

## Project Structure

- `app.py`: The main application file where the server is initialized.
- `requirements.txt`: Lists all the Python dependencies required to run the application.
- `static/`: Contains static assets like CSS, images, and JavaScript files.
- `templates/`: Contains HTML templates used by the application.
- `.env`: Environment configuration file (you need to create this).

## Setup

1. Clone the repository or download the files.

    ```bash
    git clone <repository_url>
    cd ai_image_generator-main
    ```

2. Install the required dependencies.

    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory and add the following environment variables:

    ```
    venice=<your_veniceai_apikey>
    SECRET_KEY=<flask_secretkey>
    password=<admin_password>
    ```

4. Run the application.

    ```bash
    python app.py
    ```

5. Access the application by opening your browser and navigating to:

    ```
    http://127.0.0.1:5001
    ```

## Usage

Once the application is running, you can interact with the web interface to provide textual descriptions, and the AI model will generate corresponding images.

## License

This project is open-source, and you can use it under the terms of the MIT License.