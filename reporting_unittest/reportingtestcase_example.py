"""Exemplifies how to use the ReportingTestCase class."""

from selenium.webdriver.remote.webdriver import By

from reporting_unittest import ReportingTestCase

from singleton_web_driver import SingletonWebDriver


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
            eventDescription="login page loaded",
            warning=False,
            element='screen'
        )
        self.reportEvent(
            eventDescription="warning you that nothing has happened!",
            warning=True,
        )
        self.driverObj.find_element(
            By.ID,
            "user-name"
        ).send_keys(
            self.data["login"]
        )
        self.reportEvent(
            eventDescription="username field filled",
            warning=False,
            data=['login'],
            element={"by": By.ID, "value": 'user-name'},
            imageEmbed=True
        )
        passwordElement = self.driverObj.find_element(
            By.ID,
            "password"
        )
        passwordElement.send_keys(
            self.data["password"]
        )
        self.reportEvent(
            "password field filled",
            data=['password'],
            element=passwordElement,
            imageEmbed=True
        )
        loginButton = self.driverObj.find_element(
            By.ID,
            "login-button"
        )
        self.reportEvent(
            "login button identified",
            element=(By.ID, "login-button"),
            imageEmbed=True
        )
        self.reportStep(
            stepDescription="A positive step: login and password fields filled!",
            expectedBehavior="You will see this twice",
            failureBehavior="No one can see me",
            testStatus=True,
            data=['login', 'password']
        )
        self.reportStep(
            "A negative step: nothing bad happened, just saying.",
            "I expect this",
            "I did not expect this",
            False,
        )
        self.assertTrue(
            self.data['password'] == 'secret_sauce',
            f"assertive step report - password == 'secret_sauce' -> {self.data['password'] == 'secret_sauce'}",
            "Values are the same",
            "Values are not the same"
        )
        self.assertFalse(
            self.data['login'] == 'standard_user',
            f"assertive negative assertion - login == 'standard_user' -> {self.data['login'] == 'standard_user'}",
            "Values are the same",
            "Values are not the same"
        )
        self.reportEvent(
            "Unseen report since assertive tests will stop execution"
        )

    def setUp(self):
        """Set up state for test run."""
        self.driverObj.get("https://www.saucedemo.com/")

    def tearDown(self):
        """Reset state after test run."""
        pass

    def runTest(self):
        """Tells which functions to run between setUp + tearDown"""
        self.test_a()


if __name__ == "__main__":
    from selenium import webdriver
    from reporting_unittest import ReportingTestResult
    from reporting_unittest import ReportingTestSuite

    # Declare a singleton with a preferred browser driver
    # (MUST BE DONE BEFORE DECLARING ANY TEST CASES!!)
    driver = SingletonWebDriver()

    # Declare an appropriate test result object
    tempResult = ReportingTestResult()
    testName = "ExampleTest"
    testPath = ".\\"

    # Declare a test suite object to hold all of our cases
    tempSuite = ReportingTestSuite(
        testName,
        "your name here",
        driver,
        testPath
    )

    # Make some test instances from child classes of ReportingTestCase
    testOneArgs = {
        'login': 'standard_user', 
        'password': 'secret_sauce'
    }
    testOne = ReportingTestCaseExample(
        "TC001",
        "Validation hello world",
        **testOneArgs
    )

    testTwo = ReportingTestCaseExample(
        "TC002",
        "Validation two hi world",
        login='problem_user',
        password='secret_sauce'
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
