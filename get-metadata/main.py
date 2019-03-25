import logging
import flask
import rasterio


def get_metadata(request):
    """
    Cloud function that get a raster from Google Cloud Storage and returns its `rasterio` profile.

    :param request:
    :return:
    """
    try:
        filename = request.args["filename"]
    except KeyError:
        logging.error("'filename' parameter is missing", exc_info=True)
        flask.abort(400)

    try:
        bucket = request.args["bucket"]
    except KeyError:
        logging.error("'bucket' parameter is missing", exc_info=True)
        flask.abort(400)

    filepath = f"gs://{bucket}/{filename}"
    logging.info(f"Requested file: {filepath}")

    with rasterio.open(filepath) as src:
        profile = src.profile
    logging.info(f"Rasterio profile: {profile}")

    meta = {
        **profile,
        "crs": profile["crs"].to_string(),
        "transform": list(profile["transform"])
    }

    return flask.jsonify(meta)
