# Locust file to test request limit.
#
# Make sure you have the latest locust & jinja 2 is installed.
# Running `locust` will start the web interface by default at
# http://localhost:8089 where you can spawn users and set your
# wf-marketstats server URL.


from locust import HttpUser, task, between

class User(HttpUser):
    wait_time = between(0.1, 1)

    # Item list are expected to be limited at 3 RPS. More than
    # that will return 429 Too Many Requests.
    @task(10)
    def get_items(self):
        response = self.client.get("/items")
        print("Response status code:", response.status_code)
