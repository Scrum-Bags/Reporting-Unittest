"""Exemplifies how to use the ReportingTestCase class."""

from reporting_unittest import ReportingTestCase


class ReportingTestCaseExample(ReportingTestCase):
    """Performs testing logic for one case, reports."""

    def __init__(
        self,
        testCaseID: str,
        testCaseDescription: str,
        methodName: str = 'runTest',
        **kwargs
    ):
        """Initialize the test case."""
        super().__init__(
            testCaseID,
            testCaseDescription,
            methodName,
            **kwargs
        )

    def test_a(self):
        """Perform test logic."""
        self.reportEvent(
            eventDescription="event report",
            warning=False
        )
        self.reportEvent(
            eventDescription="warning report with optional data parameter",
            warning=True,
            data=['a', 'b']
        )
        self.reportStep(
            "positive step report with optional data parameter",
            "expected",
            "failure",
            True,
            data=['a', 'b']
        )
        self.reportStep(
            "negative step report",
            "expected",
            "failure",
            False,
        )
        self.assertTrue(
            self.data['a'] == self.data['b'],
            "assertive step report",
            "expected behavior string",
            "failure behavior string",
            data=['a', 'b']
        )
        self.assertFalse(
            self.data['a'] == self.data['b'],
            "assertive negative assertion",
            "expected behavior string",
            "failure behavior string",
            data=['a', 'b']
        )
        self.reportEvent(
            "unseen report since assertive tests will stop execution"
        )

    def setUp(self):
        """Set up state for test run."""
        pass

    def tearDown(self):
        """Reset state after test run."""
        pass

    def runTest(self):
        """Organize the test run."""
        self.setUp()
        self.test_a()
        self.tearDown()


if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from reporting_unittest import ReportingTestResult
    from reporting_unittest import ReportingTestSuite
    from reporting_unittest import SingletonWebDriver

    # Declare a singleton with a preferred browser driver
    # (MUST BE DONE BEFORE DECLARING ANY TEST CASES!!)
    path_to_firefox_driver = path.join(
        "C:",
        "Program Files",
        "Selenium",
        "Webdrivers",
        "geckdriver.exe"
    )
    driver = SingletonWebDriver(
        webdriver.Firefox(
            service=FirefoxService(executable_path=path_to_firefox_driver)
        )
    )
    # Declare an appropriate test result object
    tempResult = ReportingTestResult()
    testName = "ExampleTest"
    testPath = path.join(
        "C:",
        "Users",
        "matrixrunner",
        "Desktop",
        "Selenium Sprints",
        "9-14"
    )
    # Declare a test suite object to hold all of our cases
    tempSuite = ReportingTestSuite(
        testName,
        "Doug Walter",
        driver,
        testPath
    )
    # Make some test instances from child classes of ReportingTestCase
    testOneArgs = {'a': 1, 'b': 1}
    testOne = ReportingTestCaseExample(
        "TC001",
        "Validation hello world",
        **testOneArgs
    )
    testTwo = ReportingTestCaseExample(
        "TC002",
        "Validation two hi world",
        a=1,
        b=2
    )
    # Add the tests to the test suite
    for test in [testOne, testTwo]:
        tempSuite.addTest(test)
    # Run the suite of tests
    tempSuite.run(tempResult)
    # Optionally, close the driver object
    driver.close()
    del driver

    print(f'\nresults: {tempResult}')
