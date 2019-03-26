# rasterio-cloud-function
Google Cloud Functions using rasterio to get data from rasters stored on Google Cloud Storage.

You must activate the interoperability API for your Google Cloud Storage bucket 
(once a bucket is created, go to the 'Settings' page > 'Interoperability' tab, and create a new key).
 This give you the `GS_ACCESS_KEY_ID` and the `GS_SECRET_ACCESS_KEY`.
 
## Get the raster metadata
```bash
gcloud functions deploy metadata --entry-point get_metadata --trigger-http --runtime python37 \
--region $GCLOUD_REGION --project $GCLOUD_PROJECT_ID \
--set-env-vars GS_ACCESS_KEY_ID=$GS_ACCESS_KEY_ID \
--set-env-vars GS_SECRET_ACCESS_KEY=$GS_SECRET_ACCESS_KEY \ 
--set-env-vars CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

## Get raster data
```bash
gcloud functions deploy get-data --entry-point get_data --trigger-http --runtime python37 --memory 1024MB \
--region $GCLOUD_REGION --project $GCLOUD_PROJECT_ID \
--set-env-vars GS_ACCESS_KEY_ID=$GS_ACCESS_KEY_ID \
--set-env-vars GS_SECRET_ACCESS_KEY=$GS_SECRET_ACCESS_KEY \ 
--set-env-vars CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
