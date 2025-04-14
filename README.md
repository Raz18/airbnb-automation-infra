# Airbnb Test Suite

...existing content...

## Running the Tests on Linux

To run the test suite on a Linux system, follow these steps:

1. **Ensure Prerequisites Are Installed**:
   Make sure Python, Node.js, and Playwright are installed as described in the [Prerequisites](#prerequisites) section.

2. **Set Up the Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install
   mkdir -p temp/test_runs
   ```

3. **Run the Tests**:
   ```bash
   pytest tests/
   ```

4. **View Logs**:
   Logs will be saved in the `temp/test_runs` directory.

## Running the Tests Using Docker

To run the test suite in a Dockerized environment, follow these steps:

1. **Build the Docker Image**:
   ```bash
   ./install.sh
   ```

2. **Run the Tests**:
   Use the provided `run_tests.sh` script to execute the tests inside the Docker container:
   ```bash
   ./run_tests.sh
   ```

3. **Pass Additional Arguments**:
   To pass additional arguments to `pytest`, append them to the `run_tests.sh` command. For example:
   ```bash
   ./run_tests.sh -k "test_second_case"
   ```

4. **View Results**:
   Test results, including logs and reports, will be saved in the `temp` directory on your host machine.

...existing content...
