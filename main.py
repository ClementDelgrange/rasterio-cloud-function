import logging
import json
import flask
from PIL import Image

import rasterio
import rasterio.mask as rio_mask
import rasterio.plot as rio_plot
from rasterio.crs import CRS
from fiona.transform import transform_geom


def get_metadata(request):
    """
    Cloud function that returns the metadata of a raster stored on Google Cloud Storage.

    :param request: the request object
    :type request: flask.Request
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


def get_data(request):
    """
    Cloud function that returns a rectangle of data on several channels from a raster
    stored on Google Cloud Storage.

    The request object must contain the following parameters:
    - bucket: the name of the bucket in which the raster is located
    - filename: the name of the raster in the bucket
    - geojson: the GeoJSON feature

    :param request: the request object
    :type request: flask.Request
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

    try:
        geojson = json.loads(request.args["geojson"])
    except KeyError:
        logging.error("'geojson' parameter is missing", exc_info=True)
        flask.abort(400)
    except json.JSONDecodeError:
        logging.error("'geojson' parameter is malformated", exc_info=True)
        flask.abort(400)

    filepath = f"gs://{bucket}/{filename}"
    logging.info(f"Requested file: {filepath}")

    array = rasterio_get_data(filepath, geojson)
    img = Image.fromarray(rio_plot.reshape_as_image(array))
    return flask.send_file(img, mimetype="image/png")


def rasterio_get_data(filepath, geojson):
    """
    Returns the data rectangle surrounding the geometry over several channels from a raster.

    :param filepath: the path to the raster file
    :param geojson: the GeoJSON feature
    :return: the extracted data
    :rtype: np.ndarray
    """
    try:
        crs_obj = geojson["properties"]["crs"]
    except KeyError:
        # Default coordinates reference system is WGS84
        crs = "EPSG:4326"
    else:
        crs = CRS.from_user_input(crs_obj["properties"]["name"]).to_string()
    logging.info(f"GeoJSON CRS: {crs}")

    with rasterio.open(filepath) as img:
        img_crs = img.profile["crs"].to_string()
        logging.info(f"Raster CRS: {img_crs}")

        if crs != img_crs:
            geometry = transform_geom(crs, img_crs, geojson["geometry"])
        else:
            geometry = geojson["geometry"]
        logging.info(f"GeoJSON geometry: {geometry}")

        array, _ = rio_mask.mask(
            img,
            shapes=[geometry],
            crop=True,
            filled=False
        )

        return array.data
