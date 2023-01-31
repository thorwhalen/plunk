from py2http.service import run_app

# Define or import functions
def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


class Divider:
    def __init__(self, dividend):
        self.dividend = dividend

    def divide(self, divisor):
        return self.dividend / divisor


divider_from_ten = Divider(10)

# Make a list of functions or instance methods
func_list = [add, multiply, divider_from_ten.divide]

# Create an HTTP server
# run_app(func_list, protocol="https")

run_app(
    func_list,
    publish_openapi=True,
    host="localhost",
    port=3030,
    ssl_certfile="/Users/sylvain/cert.pem",
    ssl_keyfile="/Users/sylvain/key.pem",
    # verify=False,
)
