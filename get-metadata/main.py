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

    return flask.jsonify(profile)
