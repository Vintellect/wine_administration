# User Management

This service is responsible for handling user-related operations within our infrastructure. It provides functionality for user registration, authentication, and user profile management.

## Requirements

Before you begin, ensure you have the following installed:
- Google Cloud SDK (gcloud CLI): Follow the [installation guide](https://cloud.google.com/sdk/docs/installing) for step-by-step instructions.

## Initial Setup

Once the gcloud is installed, you'll need to authenticate and set up your project:

1. Initialize gcloud:

   ```sh
   gcloud init
   ```

2. Follow the on-screen instructions to authenticate with your Google account.

3. Select the project you wish to work on from the list provided by the gcloud tool.

## Deployment

To deploy the User Management service to production, use the following command:

```sh
gcloud app deploy ./app.yaml
```

Ensure you are in the correct directory where the `app.yaml` file is located before running this command. This will start the deployment process of your application to Google App Engine.

For an example of a YAML configuration, see [example.app.yml](example.app.yml). You will need to set two lines:
```yml
  SPANNER_INSTANCE: "YOUR_SPANNER_INSTANCE"
  SPANNER_DATABASE: "YOUR_SPANNER_DATABASE"
```

For more detailed information on deployment, visit the [App Engine Deployment Guide](https://cloud.google.com/appengine/docs/standard/python3/deploying).
