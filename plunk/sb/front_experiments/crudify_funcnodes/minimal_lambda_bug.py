from streamlitfront import mk_app

if __name__ == '__main__':
    app = mk_app([lambda res: res])

    app()
