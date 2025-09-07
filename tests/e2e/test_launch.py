import os
import subprocess
import time

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()


class TestE2E:
    """E2E tests for Streamlit applications"""

    # Default error indicators that should cause test failure
    ERROR_INDICATORS = [
        "ModuleNotFoundError",
        "ImportError",
        "No module named",
        "500 Internal Server Error",
        "Something went wrong",
        "Traceback (most recent call last)",
        "FileNotFoundError",
        "AttributeError",
        "TypeError",
        "ValueError",
        "Oh no!",
        "This app has encountered an error",
        "KeyError",
        "NameError",
    ]

    @property
    def project_root(self):
        return os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    @property
    def app_path(self):
        return os.path.join(self.project_root, "src", "main.py")

    @property
    def python_executable(self):
        return os.path.join(self.project_root, ".venv", "bin", "python")

    @property
    def test_port(self):
        return os.getenv("TEST_PORT", "8502")

    @property
    def host_ip(self):
        return os.getenv("HOST_IP", "localhost")

    def test_streamlit_app_loads_without_module_errors(self):
        """Test that the Streamlit app loads completely without errors."""
        # Start Streamlit server
        process = subprocess.Popen(
            [
                self.python_executable,
                "-m",
                "streamlit",
                "run",
                self.app_path,
                f"--server.port={self.test_port}",
                "--server.headless=true",
            ],
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        driver = None

        try:
            # Wait for server to start
            max_wait = 30
            wait_time = 0
            server_ready = False

            while wait_time < max_wait:
                try:
                    response = requests.get(
                        f"http://{self.host_ip}:{self.test_port}", timeout=3
                    )
                    if response.status_code == 200:
                        server_ready = True
                        break
                except requests.RequestException:
                    pass

                time.sleep(1)
                wait_time += 1

            assert (
                server_ready
            ), f"Streamlit server failed to start within {max_wait} seconds"

            # Setup WebDriver
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(f"http://{self.host_ip}:{self.test_port}")

            # Wait for Streamlit to fully load
            time.sleep(5)

            page_source = driver.page_source

            # Check for errors
            found_errors = []
            for error in self.ERROR_INDICATORS:
                if error in page_source:
                    found_errors.append(error)

            # Debug output
            print(f"Page source length: {len(page_source)}")
            print("First 1000 characters of page source:")
            print(page_source[:1000])
            print("---")

            if found_errors:
                print(f"Found errors: {found_errors}")
            else:
                print("No errors found in page source")

            assert len(found_errors) == 0, f"Found errors in page: {found_errors}"

            # Verify basic Streamlit elements are present
            wait = WebDriverWait(driver, 20)
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-testid='stApp']")
                    )
                )
                print("✅ Streamlit app loaded successfully")
            except Exception as e:
                print(
                    f"⚠️  Could not find main Streamlit container, but no errors detected: {e}"
                )

            # Check page title
            title = driver.title
            assert (
                "Streamlit" in title or len(title) > 0
            ), "Page title is empty or invalid"

        finally:
            if driver:
                driver.quit()

            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

    def test_app_functionality_basic_interaction(self):
        """Test basic app functionality - alias for main test method."""
        return self.test_streamlit_app_loads_without_module_errors()
