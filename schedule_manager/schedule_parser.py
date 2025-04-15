import pandas as pd
from dataclasses import dataclass
import datetime
from io import BytesIO


@dataclass
class Shift:
    """Represents a single work shift.

    Attributes:
        date (datetime.date): Date of the shift.
        time_start (datetime.time | None): Start time of the shift.
        time_end (datetime.time | None): End time of the shift.
        day_type (str | None): Type of the day (e.g., 'WORK', 'VACATION', 'OFF').
        additional_info (str | None): Any additional info related to the shift.
    """

    date: datetime.date
    time_start: datetime.time | None
    time_end: datetime.time | None
    day_type: str | None
    additional_info: str | None = None


@dataclass
class EmployeeSchedule:
    """Represents an employee's schedule for a given month and year.

    Attributes:
        month (int): Month of the schedule.
        year (int): Year of the schedule.
        shifts (list[Shift]): List of work shifts in that month.
    """

    month: int
    year: int
    shifts: list[Shift]


@dataclass
class Employee:
    """Represents an employee with a monthly schedule.

    Attributes:
        first_name (str): First name of the employee.
        last_name (str): Last name of the employee.
        schedule (EmployeeSchedule): Schedule of the employee.
    """

    first_name: str
    last_name: str
    schedule: EmployeeSchedule

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Employee):
            return NotImplemented
        return self.first_name == other.first_name and self.last_name == other.last_name


class ScheduleParser:
    """Parses employee work schedules from Excel files."""

    def __init__(self) -> None:
        """Initializes the parser with an empty employee schedule list."""

        self.full_schedule: list[Employee] = []

    def _prepare_dataframe(self, file: BytesIO, employee_names_col_index: int = 0) -> None:
        """
        Loads and cleans an Excel sheet into a DataFrame for processing.

        Sets the year and month, renames columns, sets employee names as index,
        and removes unnecessary rows and columns.

        Args:
            file (BytesIO): In-memory Excel file.
            employee_names_col_index (int, optional): Index of the column containing
                employee names to be used as the DataFrame index. Defaults to 0.

        Sets:
            self._df (pd.DataFrame): Processed schedule data.
            self.year (int): Year extracted from the sheet header.
            self.month (int): Month extracted from the sheet header.
        """

        df = pd.read_excel(file)

        # store year and month for later
        self.year: int = df.iloc[:, 0].name.year  # type: ignore
        self.month: int = df.iloc[:, 0].name.month  # type: ignore

        # set the first row as column names
        df = df.rename(
            {
                old_name: new_name
                for old_name, new_name in zip(df.columns.to_list(), df.iloc[0].to_list())
            },
            axis="columns",
        ).iloc[1:]

        # rename first index from "NaN" to "DAY_OF_THE_MONTH"
        df.iloc[0, 0] = "DAY_OF_THE_MONTH"

        # turn the column containing employees' names into the index
        df = df.set_index(df.iloc[:, employee_names_col_index]).drop(
            columns=df.columns[employee_names_col_index]
        )

        # drop emtpy rows and column
        df = df.drop(
            ["FULL TIME", "PART TIME 3/4", "PART TIME 1/2", "PART TIME 1/4", "INSTRUKTORZY"]
        )

        # if the first column name is NaN df.drop won't work,
        # so I fillna with random values to prevent that from happening
        df.columns = df.columns.fillna("peekaboo")
        df = df.drop(df.columns[0], axis=1)

        self._df = df

    def _init_schedule(self, employee_names: list[str]) -> None:
        """Initializes employee objects with empty schedules.

        Args:
            employee_names (list[str]): Full names of employees (e.g., "John Doe").
        """

        self.full_schedule = [
            Employee(
                *employee.split(" "),
                schedule=EmployeeSchedule(month=self.month, year=self.year, shifts=[]),
            )
            for employee in employee_names
        ]

    def _parse_workday_string(
        self, string: str
    ) -> tuple[str | None, str | None, str | None, str | None]:
        """Parses a cell string to extract shift details.

        Args:
            string (str): Cell content from the schedule table.

        Returns:
            tuple:
                time_start (str | None): Start time of the shift.
                time_end (str | None): End time of the shift.
                day_type (str | None): Type of the day (e.g., 'WORK', 'OFF').
                additional_info (str | None): Extra info like 'MC' or unknown content.
        """

        if string.strip() == "OFF":
            return (None, None, "AVAILABILITY_OFF", None)

        if string.strip() == "W":
            return (None, None, "NON_WORKING_DAY", None)

        if "U" in string:
            time_start, time_end = string.split("U")
            return (time_start.strip(), time_end.strip(), "VACATION", None)

        if "-" in string:
            time_start, time_end = string.split("-")
            return (time_start.strip(), time_end.strip(), "WORK", None)

        if "MC" in string:
            time_start, time_end = string.split("MC")
            return (time_start.strip(), time_end.strip(), "WORK", "MC")

        return (None, None, None, string)

    def _parse_time_string(self, time: str | None) -> datetime.time | None:
        """Parses a string into a time object.

        Args:
            time (str | None): Time string in "HH:MM" format, or None.

        Returns:
            datetime.time | None: Parsed time object, or None if input is invalid.
        """

        if not time:
            return None

        return datetime.time(*map(int, time.split(":")))  # type: ignore

    def _extract_data(self) -> None:
        """Extracts shift data from the DataFrame and assigns it to employees.

        Iterates through the DataFrame and fills each employee's schedule
        with Shift objects based on the corresponding day and cell content.
        """

        first_column: int = 0
        days_of_month: list[int] = [int(x) if not pd.isna(x) else -1 for x in self._df.iloc[0]]

        for index in range(len(self._df) - 1):

            for column in range(first_column, len(self._df.columns)):

                cell = self._df.iloc[index + 1, column]
                # if cell is NaN (empty) it skips entire column to do less iterations
                # (cells are only empty for the days that are "outside" the current month)
                if pd.isna(cell):
                    first_column = column + 1
                    continue

                time_start, time_end, day_type, additional_info = self._parse_workday_string(
                    str(cell)
                )

                self.full_schedule[index].schedule.shifts.append(
                    Shift(
                        date=datetime.date(self.year, self.month, days_of_month[column]),
                        time_start=self._parse_time_string(time_start),
                        time_end=self._parse_time_string(time_end),
                        day_type=day_type,
                        additional_info=additional_info,
                    )
                )

    def parse(self, file: BytesIO, employee_names_col_index: int = 0) -> None:
        """Parses an Excel schedule file and returns structured employee data.

        Args:
            file (BytesIO): In-memory Excel file containing the schedule.
            employee_names_col_index (int): Column index containing employee names.
        """

        self._prepare_dataframe(file, employee_names_col_index)

        if not self.full_schedule:
            self._init_schedule(self._df.index.to_list()[1:])

        self._extract_data()
