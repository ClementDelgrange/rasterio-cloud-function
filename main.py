import logging
import json
import io

import flask
import PIL.Image

import rasterio
import rasterio.mask
import rasterio.plot
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

    try:
        array = rasterio_get_data(filepath, geojson)
    except:
        logging.error("Unable to get data", exc_info=True)
        return flask.abort(404)

    img = PIL.Image.fromarray(rasterio.plot.reshape_as_image(array))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    logging.info("Image built")

    return flask.send_file(buf, mimetype="image/png", as_attachment=False)


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

        array, _ = rasterio.mask.mask(
            img,
            shapes=[geometry],
            crop=True,
            filled=False
        )
        logging.info(f"Array extracted from raster. Shape={array.shape}")

        return array.data
