# Whatsapp server template


## Template features

You can find the following template features in `app/main.py`:

- **Webhook Verification:**
  - Handles GET requests to `/webhook` for WhatsApp webhook verification.
- **Message Handling:**
  - Handles POST requests to `/webhook` for incoming WhatsApp messages (text and images).
  - Sends confirmation replies to users.
- **Send WhatsApp Messages:**
  - Utility to send text messages (and replies) via WhatsApp Cloud API.
- **Download Media:**
  - Downloads images sent to the webhook and saves them locally.
- **Background Task Example:**
  - Demonstrates running long tasks (e.g., on receiving a specific command) using FastAPI background tasks.
- **FastAPI App:**
  - Runs with Uvicorn, ready for production or local development.

---


## Local Development

You can run the WhatsApp App (`app/main.py`) locally using either Docker or Python virtual environment.

### 1. Using Docker

1. Create a `.env` file in the project root (see `.env.example` for required variables).
2. Build the Docker image:
   ```bash
   docker build -f deployment/Dockerfile -t whatsapp-server-template:latest .
   ```
3. Run the container:
   ```bash
   docker run -p 5000:5000 whatsapp-server-template:latest
   ```

### 2. Using Python venv

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip3 install --upgrade pip
   pip3 install -r deployment/requirements.txt
   ```
3. Create a `.env` file in the project root (see `.env.example`).
4. Run the app:
   ```bash
   python3 app/main.py
   ```

---


## GitHub Actions: CI/CD with `whatsapp-server.yml`

The workflow in `.github/workflows/whatsapp-server.yml` automates testing and deployment:

- **Test job:**
  - Builds the Docker image.
  - Runs tests inside the container using pytest.
  - Uploads test results as artifacts.
- **Deploy job:**
  - Runs only if triggered with `deploy: true`.
  - Pushes the Docker image to AWS ECR.
  - Uploads deployment files to S3.
  - Deploys the app to AWS Elastic Beanstalk.


### Setup Required Secrets

Set the following secrets in your GitHub repository for CI/CD and deployment:

- Secrets for AWS credentials:
    - `AWS_ACCESS_KEY_ID` (with console access)
    - `AWS_SECRET_ACCESS_KEY` (with console access)
    - `AWS_REGION`
- Secrets for AWS Elastic Beanstalk deployment
    - `ECR_REPO_URL`
    - `AWS_PUBLIC_S3_BUCKET_NAME`
    - `AWS_PUBLIC_S3_KEY`
    - `AWS_PUBLIC_S3_FOLDER_URI`
- Secrets for setting up the WhatsApp app at [developers.facebook.com](https://developers.facebook.com/)
    - `WHATSAPP_ACCESS_TOKEN`
    - `WHATSAPP_SERVER_NUMBER_ID`
    - `WHATSAPP_VERIFY_TOKEN`

---


## Facebook Setup

- Create a Business Portfolio at [business.facebook.com](https://business.facebook.com/)
- Create an App associated with your Business Portfolio at [developers.facebook.com](https://developers.facebook.com/)

### Setting up the App's webhook

Once the app is running (either locally or on AWS Elastic Beanstalk):
- Go to your App's page at [developers.facebook.com](https://developers.facebook.com/)
- Navigate to `Webhooks` and select `Whatsapp Business Account` in the drop down menu
  - Add a public URL such as `https://<URL>/webhook` (make sure to add /webhook at the end)
  - Add an arbitrary `verification token` that matches your .env file
  - Click on `Verity and save`

**In case you are running locally:**

Expose your local server for webhook testing using ngrok:
   ```bash
   ngrok http 5000
   ```

Your URL will look like: `https://XXXXXXX.ngrok-free.app/webhook`


**In case you are running on AWS Elastic Beanstalk:**

Follow [**THIS POST**](https://patrickmetznermorais.substack.com/p/https-for-your-aws-elastic-beanstalk) for setting up HTTPS for your AWS Elastic Beanstalk application.

Your URL will look like: `your_subdomain.your_domain.com/webhook`
