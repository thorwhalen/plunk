from urllib.parse import urljoin
from extrude import mk_web_app
from http2py import HttpClient

from platform_poc.features import (
    upload_audio_data,
    mk_step,
    # modify_step,
    mk_pipeline,
    # modify_pipeline,
    learn_outlier_model,
    apply_fitted_model,
    visualize_output,
    visualize_session,
)
from platform_poc.apps.web_service import API_URL
from platform_poc.apps.web_client.config import mk_config


def main():
    features = [
        upload_audio_data,
        mk_step,
        # modify_step,
        mk_pipeline,
        # modify_pipeline,
        learn_outlier_model,
        apply_fitted_model,
        visualize_output,
        visualize_session,
    ]
    api = HttpClient(url=urljoin(API_URL, 'openapi'))
    app = mk_web_app(features, api=api, config=mk_config(api),)
    app()


if __name__ == '__main__':
    main()
