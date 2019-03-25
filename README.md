# rasterio-cloud-function
Google Cloud Functions using rasterio to get data from rasters stored on Google Cloud Storage.

## Get the raster metadata
```bash
gcloud functions deploy metadata --entry-point get_metadata --trigger-http --runtime python37 \
--region $GCLOUD_REGION --project $GCLOUD_PROJECT_ID \
--set-env-vars GS_ACCESS_KEY_ID=$GS_ACCESS_KEY_ID \
--set-env-vars GS_SECRET_ACCESS_KEY=$GS_SECRET_ACCESS_KEY \ 
--set-env-vars CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
