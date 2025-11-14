if __name__ == '__main__':
    from resources import funcs
    from extrude import mk_api, run_api

    app = mk_api(funcs)
    run_api(app, server='wsgiref')
