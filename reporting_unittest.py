"""Python-style unittests with HTML reporting."""

from dataclasses import dataclass
from datetime import datetime
from itertools import chain
from os import mkdir
from os import path
from os import remove
from typing import Union
from unittest import TestSuite
from unittest import TestCase
from unittest import TestResult

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService


@dataclass
class _TestEvent:
    eventDescription: str
    warning: bool = False   # WARNING = true, DONE = false
    dataString: Union[str, None] = None
    imagePath: Union[str, None] = None
    imageEmbed: bool = False

    def __post_init__(self):
        self.statusColor = "yellow" if self.warning else "antiquewhite"
        self.statusString = "WARNING" if self.warning else "DONE"


@dataclass
class _TestStep:
    stepDescription: str
    expectedBehavior: str
    failureBehavior: str
    testStatus: bool   # PASS = true, FAIL = false
    dataString: Union[str, None] = None
    imagePath: Union[str, None] = None
    imageEmbed: bool = False

    def __post_init__(self):
        self.statusColor = "green" if self.testStatus else "red"
        self.statusString = "PASS" if self.testStatus else "FAIL"
        if self.testStatus:
            self.actualBehavior = self.expectedBehavior
        else:
            self.actualBehavior = self.failureBehavior


class SingletonWebDriver:

    _instance = None

    driverPath = path.join(
        "C:\\"
        "Program Files",
        "Selenium",
        "WebDrivers"
    )

    def __new__(
        cls, 
        driverObj: Union[WebDriver, str, None] = None,
        **kwargs
    ):
        if cls._instance is None:
            if driverObj == 'Chrome':
                cls._instance = webdriver.Chrome(
                    service=ChromeService(
                        executable_path=path.join(
                            cls.driverPath,
                            "chromedriver.exe"
                        )
                    ),
                    **kwargs
                )
            elif driverObj == 'Edge':
                cls._instance = webdriver.Edge(
                    service=EdgeService(
                        executable_path=path.join(
                            cls.driverPath,
                            "msedgedriver.exe"
                        )
                    ),
                    **kwargs
                )
            elif driverObj is None or driverObj == Firefox:
                cls._instance = webdriver.Firefox(
                    service=FirefoxService(
                        executable_path=path.join(
                            cls.driverPath,
                            "geckodriver.exe"
                        )
                    ),
                    **kwargs
                )
            else:
                cls._instance = driverObj
        return cls._instance


class ReportingTestCase(TestCase):
    """Stores info for a full test case with logic."""

    def __init__(
        self,
        testCaseID: str,
        testCaseDescription: str,
        methodName: str = 'runTest',
        **kwargs
    ):
        """Set up test case object."""
        super().__init__(methodName=methodName)
        self.data = kwargs
        self.testCaseID = testCaseID
        self.testCaseDescription = testCaseDescription
        self.driverObj = SingletonWebDriver()
        self.status = 1  # 0 = FAIL, 1 = PASS, other = WARNING
        self.steps = []

    def _screenshot(
        self,
        element: Union[dict, str, WebElement],
        description: str
    ):
        outFolder = path.join(
            '.screenshots',
            self.testCaseID
        )
        if not path.exists(outFolder):
            mkdir(outFolder)
        imagePath = path.join(
            outFolder,
            description + ".png"
        )
        if isinstance(element, dict):
            self.driverObj.find_element(**elementIDs).screenshot(imagePath)
        elif isinstance(element, WebElement):
            element.screenshot(imagePath)
        else:
            self.driverObj.save_screenshot(imagePath)
        return imagePath

    def _makeDataString(
        self,
        data: Union[list, str, None]
    ):
        if isinstance(data, list):
            filteredRows = filter(lambda a: a in self.data.keys(), data)
            rows = [f"{k}: '{self.data[k]}'" for k in filteredRows]
            temp = '\n'.join(rows)
            return temp
        elif isinstance(data, str):
            return data
        return ''

    def statusColor(self):
        """Get the case's status color."""
        if self.status == 0:
            return "red"
        elif self.status == 1:
            return "green"
        else:
            return "yellow"

    def statusString(self):
        """Get the case's status string."""
        if self.status == 0:
            return "FAIL"
        elif self.status == 1:
            return "PASS"
        else:
            return "WARNING"

    def reportEvent(
        self,
        eventDescription: str,
        warning: bool = False,
        data: Union[list, str, None] = None,
        imageEmbed: bool = False,
        element: Union[dict, str, None] = None
    ):
        """Log an untested step."""
        imagePath = None
        if element is not None:
            imagePath = self._screenshot(element, eventDescription)
        dataString = self._makeDataString(data)
        self.steps.append(
            _TestEvent(
                eventDescription=eventDescription,
                warning=warning,
                dataString=dataString,
                imagePath=imagePath,
                imageEmbed=imageEmbed
            )
        )
        if warning and self.status == 1:
            self.status = 2

    def reportStep(
        self,
        stepDescription: str,
        expectedBehavior: str,
        failureBehavior: str,
        testStatus: bool,
        data: Union[list, str, None] = None,
        imageEmbed: bool = False,
        element: Union[dict, str, None] = None
    ):
        """Add a new test step to the report."""
        imagePath = None
        if element is not None:
            imagePath = self._screenshot(element, stepDescription)
        dataString = self._makeDataString(data)
        self.steps.append(
            _TestStep(
                stepDescription=stepDescription,
                expectedBehavior=expectedBehavior,
                failureBehavior=failureBehavior,
                testStatus=testStatus,
                dataString=dataString,
                imagePath=imagePath,
                imageEmbed=imageEmbed
            )
        )
        if not testStatus and self.status != 0:
            self.status = 0

    def assertTrue(
        self,
        expr,
        stepDescription: str,
        expectedBehavior: str,
        failureBehavior: str,
        data: Union[list, str, None] = None,
        imageEmbed: bool = False,
        elementIDs: Union[dict, None] = None
    ):
        """Test condition, halt on fail."""
        testStatus = bool(expr)
        self.reportStep(
            stepDescription=stepDescription,
            expectedBehavior=expectedBehavior,
            failureBehavior=failureBehavior,
            testStatus=testStatus,
            data=data,
            imageEmbed=imageEmbed,
            elementIDs=elementIDs
        )
        super().assertTrue(expr)

    def assertEqual(
        self,
        first,
        second,
        stepDescription: str,
        expectedBehavior: str,
        failureBehavior: str,
        data: Union[list, str, None] = None,
        imageEmbed: bool = False,
        elementIDs: Union[dict, None] = None
    ):
        """Test condition, halt on equal fail."""
        testStatus = first == second
        self.reportStep(
            stepDescription=stepDescription,
            expectedBehavior=expectedBehavior,
            failureBehavior=failureBehavior,
            testStatus=testStatus,
            data=data,
            imageEmbed=imageEmbed,
            elementIDs=elementIDs
        )
        super().assertEqual(first, second)

    def assertFalse(
        self,
        expr,
        stepDescription: str,
        expectedBehavior: str,
        failureBehavior: str,
        data: Union[list, str, None] = None,
        imageEmbed: bool = False,
        elementIDs: Union[dict, None] = None
    ):
        """Test condition, halt on negative fail."""
        testStatus = not bool(expr)
        self.reportStep(
            stepDescription=stepDescription,
            expectedBehavior=expectedBehavior,
            failureBehavior=failureBehavior,
            testStatus=testStatus,
            data=data,
            imageEmbed=imageEmbed,
            elementIDs=elementIDs
        )
        super().assertFalse(expr)

    def assertNotEqual(
        self,
        first,
        second,
        stepDescription: str,
        expectedBehavior: str,
        failureBehavior: str,
        data: Union[list, str, None] = None,
        imageEmbed: bool = False,
        elementIDs: Union[dict, None] = None
    ):
        """Test condition, halt on unequal fail."""
        testStatus = not first == second
        self.reportStep(
            stepDescription=stepDescription,
            expectedBehavior=expectedBehavior,
            failureBehavior=failureBehavior,
            testStatus=testStatus,
            data=data,
            imageEmbed=imageEmbed,
            elementIDs=elementIDs
        )
        super().assertNotEqual(first, second)


class ReportingTestResult(TestResult):
    """Contain test suite run results."""

    def __init__(self):
        """Set up results, keep successes too."""
        super().__init__()
        self.successes = []

    def addSuccess(self, test):
        """Append a success record."""
        self.successes.append((test, ""))


class ReportingTestSuite(TestSuite):
    """Manages a suite of tests and runs them."""

    def __init__(
        self,
        testName: str,
        testerName: str,
        driverSingleton: SingletonWebDriver,
        outPath: Union[str, None] = None,
        **kwargs
    ):
        """Set up test suite."""
        super().__init__(kwargs)
        self.testName = testName
        self.testerName = testerName
        self.outPath = outPath if outPath is not None else self.testName
        if not path.exists(self.outPath):
            mkdir(self.outPath)
        self.screenshot_path = path.join(self.outPath, '.screenshots')
        if not path.exists(self.screenshot_path):
            mkdir(self.screenshot_path)
        self.testerName = testerName
        self.driver = driverSingleton

    def run(self, result: TestResult = ReportingTestResult()):
        """Run test suite, write report."""
        resultObj = super().run(result=result)
        succs = [s[0] for s in resultObj.successes]
        fails = [f[0] for f in resultObj.failures]
        errors = [e[0] for e in resultObj.errors]

        allTestCases = list(chain(succs, fails, errors))
        allTestCases.sort(key=lambda a: a.testCaseID)

        filePath = path.join(self.outPath, self.testName + '.html')
        if path.exists(filePath):
            remove(filePath)

        with open(filePath, mode='w', encoding='UTF-8') as outfile:
            # open html and body
            outfile.write('<html><body>')

            # write test report header
            outfile.write(
                f'''<h3>{self.testName}
                - run {datetime.now()}
                by {self.testerName}</h3>'''
            )

            # iterate over test cases
            for case in allTestCases:

                # write test case description
                tableStyleString = '''style="width: 1000px;margin: 0;
                    padding: 0;table-layout: fixed;border-collapse: collapse;
                    font: 11px/1.4 Trebuchet MS;"'''
                tableHeaderStyleString = 'style="margin: 0;padding: 0;"'
                outfile.write(
                    f'''<table {tableStyleString}>
                    <thead {tableHeaderStyleString}>
                    <tr {tableHeaderStyleString}>'''
                )
                for text, width in zip(
                    ["TCID", "Description", "Status"],
                    [100, 700, 200]
                ):
                    outfile.write(
                        f'''<th style="width: {width}px;margin: 0;padding: 6px;
                        background: #333;color: white;font-weight: bold;
                        border: 1px solid #ccc;text-align: auto;">
                        {text}</th>'''
                    )
                outfile.write(f'</tr></thead><tbody><tr>')
                for text, width in zip(
                    [case.testCaseID, case.testCaseDescription],
                    [100, 700]
                ):
                    outfile.write(
                        f'''<th style="width: {width}px;margin: 0;padding: 6px;
                        background: white;color: black;font-weight: bold;
                        border: 1px solid #ccc;text-align: auto;">
                        {text}</th>'''
                    )
                outfile.write(
                    f'''<th style="width: 200px;margin: 0;padding: 6px;
                    background: {case.statusColor()};color: black;
                    font-weight: bold;border: 1px solid #ccc;
                    text-align: auto;">{case.statusString()}</th>'''
                )
                outfile.write(f'</tr></tbody></table>')

                # write steps header
                outfile.write(
                    f'''<details><summary>Step Details</summary>
                    <table {tableStyleString}>
                    <thead {tableHeaderStyleString}>
                    <tr {tableHeaderStyleString}>'''
                )
                for text, width in zip(
                    [
                        "Step #",
                        "Description",
                        "Expected Behavior",
                        "Actual Behavior",
                        "Status",
                        "Test Data",
                        "Screenshot"
                    ],
                    [
                        50,
                        200,
                        300,
                        300,
                        50,
                        250,
                        400
                    ]
                ):
                    outfile.write(
                        f'''<th style="width: {width}px;margin: 0;
                        padding: 6px;background: #333;color: white;
                        font-weight: bold;border: 1px solid #ccc;
                        text-align: auto;">{text}</th>'''
                    )
                outfile.write('</tr></thead>')

                # write test steps
                outfile.write(f'<tbody {tableHeaderStyleString}>')
                for i, step in enumerate(case.steps, start=1):
                    outfile.write(
                        f'''<tr><th style="width: 50px;margin: 0;padding: 6px;
                        background: white;color: black;font-weight: bold;
                        border: 1px solid #ccc;text-align: auto;">{i}</th>'''
                    )
                    if isinstance(step, _TestStep):
                        for w, t in zip(
                            [200, 300, 300],
                            [
                                step.stepDescription,
                                step.expectedBehavior,
                                step.actualBehavior
                            ]
                        ):
                            outfile.write(
                                f'''<th style="width: {w}px;margin: 0;
                                padding: 6px;background: white;color: black;
                                font-weight: bold;border: 1px solid #ccc;
                                text-align: auto;">{t}</th>'''
                            )
                    elif isinstance(step, _TestEvent):
                        for w, t in zip(
                            [300, 200, 300],
                            [step.eventDescription, '', '']
                        ):
                            outfile.write(
                                f'''<th style="width: {w}px;margin: 0;
                                padding: 6px;background: white;color: black;
                                font-weight: bold;border: 1px solid #ccc;
                                text-align: auto;">{t}</th>'''
                            )
                    outfile.write(
                        f'''<th style="width: 50px;margin: 0;padding:
                        6px;background: {step.statusColor};color: black;
                        font-weight: bold;border: 1px solid #ccc;
                        text-align: auto;">{step.statusString}</th>'''
                    )
                    outfile.write(
                        f'''<th style="width: 250px;margin: 0;padding: 6px;
                        background: white;color: black;
                        font-weight: bold;border: 1px solid #ccc;
                        text-align: auto;">{step.dataString}</th>'''
                    )
                    if step.imagePath is None:
                        outfile.write(
                            f'''<th style="width: 400px;margin: 0;padding: 6px;
                            background: white;color: black;
                            font-weight: bold;border: 1px solid #ccc;
                            text-align: auto;">N/A</th>'''
                        )
                    else:
                        if step.imageEmbed:
                            outfile.write(
                                f'''<th style="width: 400px;margin: 0;
                                padding: 6px;background: white;
                                color: black;font-weight: bold;
                                border: 1px solid #ccc;text-align: auto;
                                "><image src="{step.imagePath}">
                                </image></th>'''
                            )
                        else:
                            outfile.write(
                                f'''<th style="width: 400px;margin: 0;
                                padding: 6px;background: white;
                                color: black;font-weight: bold;
                                border: 1px solid #ccc;text-align: auto;
                                "><a href="{step.imagePath}
                                " target="_blank">Link</a></th>'''
                            )
                    outfile.write('</tr>')
                outfile.write('</tbody>')

                # close step description
                outfile.write('</table></details><br><br>')

            # close html and body
            outfile.write('</body></html>')

        return resultObj
