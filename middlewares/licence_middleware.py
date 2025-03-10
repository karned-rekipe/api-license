import logging
import time

from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from decorators.log_time import log_time_async
from middlewares.token_middleware import extract_token, get_token_info, refresh_cache_token
from utils.path_util import is_unprotected_path


def extract_entity( request: Request ):
    token_info = get_token_info(extract_token(request))
    logging.info(f"tokeninfo: {token_info}")
    if token_info is not None:
        licenses = token_info.get('licenses', [])
        logging.info(f"licenses: {licenses}")
        license_uuid = extract_licence(request)
        for lic in licenses:
            if str(lic.get('uuid')) == str(license_uuid):
                logging.info(f"license_uuid: {license_uuid}")
                entity_uuid = lic.get('entity_uuid')
                logging.info(f"entity_uuid: {entity_uuid}")
                return entity_uuid
    return None


def extract_licence( request: Request ) -> str:
    return request.headers.get('licence')


def is_headers_licence_present( request: Request ) -> bool:
    licence = extract_licence(request)
    if not licence:
        return False
    return True


def is_licence_found( request: Request, licence: str ):
    token = extract_token(request)
    token_info = get_token_info(token)
    if not token_info.get('licenses'):
        return False
    licenses = token_info.get('licenses')
    if not licenses:
        return False
    if not any(licence_data['uuid'] == licence for licence_data in licenses):
        return False
    return True


def get_licence_info( request: Request, licence: str ) -> dict:
    token = extract_token(request)
    token_info = get_token_info(token)
    licenses = token_info.get('licenses')
    licence_info = next(licence_data for licence_data in licenses if licence_data['uuid'] == licence)
    return licence_info


def check_headers_licence( request: Request ):
    if not is_headers_licence_present(request):
        raise HTTPException(status_code=403, detail="Licence header missing")


def check_licence( request: Request, licence: str ):
    if not is_licence_found(request, licence):
        fresh_limit = int(time.time()) - 60
        if request.state.token_info.get('cached_time') < fresh_limit:
            refresh_cache_token(request)
            if not is_licence_found(request, licence):
                raise HTTPException(status_code=403, detail="Licence not found")


class LicenceVerificationMiddleware(BaseHTTPMiddleware):
    def __init__( self, app ):
        super().__init__(app)

    @log_time_async
    async def dispatch( self, request: Request, call_next ) -> Response:
        logging.info("LicenceVerificationMiddleware")

        if not is_unprotected_path(request.url.path):
            check_headers_licence(request)
            licence = extract_licence(request)
            check_licence(request, licence)
            request.state.licence = licence
            entity_uuid = extract_entity(request)
            request.state.entity_uuid = entity_uuid
        response = await call_next(request)
        return response