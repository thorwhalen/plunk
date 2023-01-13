from streamlitfront import mk_app


class NoNameCallable:
    def foo(self):
        return "hi"

    def __call__(self):
        return self.foo()


no_name_callable = NoNameCallable()


if __name__ == "__main__":
    app = mk_app([no_name_callable])
    app()
