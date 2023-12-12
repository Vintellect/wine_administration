# Wine Administration

The Wine Administration service is dedicated to ensuring the accurate insertion of wine data within our system. 

## Deployment Instructions

To deploy the wine service, start by copying the example application configuration:

```sh
cp example.app.yml app.yml
```

Next, you need to update the following variables in the `.env` file:

```yml
  USER_MICROSERVICES: "YOUR-URL-USER-MANAGEMENT"
  SPANNER_INSTANCE: "YOUR-SPANNER_INSTANCE"
  SPANNER_DATABASE: "YOUR-WINE-DATABASE"
  BUCKET_IMAGE: "YOUR-BUCKET-NAME"
```

Replace the placeholders (`YOUR-URL-USER-MANAGEMENT`, `YOUR-SPANNER_INSTANCE`, `YOUR-WINE-DATABASE`, and `YOUR-BUCKET-NAME`) with your actual service URL, Spanner instance name, Spanner database name, and the name of your public buckets, respectively.

For a more comprehensive guide on deployment, including detailed steps and additional configurations, please refer to our [App Engine Deployment Guide](https://github.com/Vintellect/deploy_backend_guide/blob/fd5863fb17d5386cdf16eb43cf58b0c6b8cc571f/Microservices_guide.md).