"""
Generates authorized Video Pipeline and VAL token.

"""

from __future__ import absolute_import
import ast
import logging
import requests
import urllib3

from video_worker.utils import get_config

"""Disable insecure warning for requests lib"""

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


settings = get_config()


logger = logging.getLogger(__name__)


def veda_tokengen():
    """
    Gen and authorize a VEDA API token
    """
    # Generate Token
    payload = {'grant_type': 'client_credentials'}
    veda_token_response = requests.post(
        settings['veda_token_url'] + '/',
        data=payload,
        auth=(
            settings['veda_client_id'],
            settings['veda_secret_key']
        ),
        timeout=settings['global_timeout']
    )

    if veda_token_response.status_code != 200:
        logger.error('VEDA token generation')
        return

    veda_token = ast.literal_eval(veda_token_response.text)['access_token']

    # Authorize token
    """
    This is based around the VEDA "No Auth Server" hack

    NOTE: After much screwing around, I couldn't get nginx to pass
    the auth headers, so I'm moving to token auth

    **it's shit, and needs a rewrite. see api.py in veda-django
    """
    payload = {'data': veda_token}
    veda_auth_response = requests.post(
        settings['veda_auth_url'] + '/',
        data=payload
    )

    if veda_auth_response.status_code != 200:
        logger.error('VEDA token authorization')
        return

    return veda_auth_response.text.strip()
