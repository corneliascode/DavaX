----------------------------------------------------------
-- STEP 1: Create database and schemas
----------------------------------------------------------


CREATE DATABASE TimesheetDB; -- Creates the main database to hold all timesheet-related objects
GO

USE TimesheetDB; -- Switches context to the newly created database
GO

CREATE SCHEMA timesheet; -- Creates a schema to logically separate timesheet-related tables
GO

----------------------------------------------------------
-- STEP 2: Define tables with required constraints
----------------------------------------------------------

CREATE TABLE timesheet.Employees ( -- This table is for employee data
    employee_id INT PRIMARY KEY, -- Every employee has unique ID
    name VARCHAR(100) NOT NULL, -- Name cannot be empty
    email VARCHAR(100) UNIQUE, -- Each email must be different
    hire_date DATE CHECK (hire_date <= GETDATE()), -- We do not allow dates in future
    metadata NVARCHAR(MAX) -- JSON Data
);

CREATE TABLE timesheet.Timesheets ( -- Table for work entries
    timesheet_id INT PRIMARY KEY, -- Unique entry ID
    employee_id INT NOT NULL, -- Link to employee
    work_date DATE NOT NULL, -- Date of work
    hours_worked DECIMAL(4,2) CHECK (hours_worked BETWEEN 0 AND 24), -- Valid hours
    CONSTRAINT fk_employee FOREIGN KEY (employee_id) REFERENCES timesheet.Employees(employee_id), -- Employee must exist
    CONSTRAINT uq_timesheet UNIQUE (employee_id, work_date) -- No duplicate entries per day per employee
);

----------------------------------------------------------
-- STEP 3: Add sample data
----------------------------------------------------------

INSERT INTO timesheet.Employees (employee_id, name, email, hire_date, metadata)
VALUES
(1, 'Alice', 'alice@endava.com', '2022-01-01', N'{"skills": ["SQL"], "hours": {"expected": 40}}'),
(2, 'Bob', 'bob@endava.com', '2022-06-01', N'{"skills": ["Excel"], "hours": {"expected": 38}}');

INSERT INTO timesheet.Timesheets (timesheet_id, employee_id, work_date, hours_worked)
VALUES
(1, 1, '2024-06-03', 8.0),
(2, 1, '2024-06-04', 6.5),
(3, 2, '2024-06-03', 7.0),
(4, 2, '2024-06-04', 7.5),
(5, 1, '2024-06-05', 8.0),
(6, 1, '2024-06-06', 4.0),
(7, 2, '2024-06-05', 6.0),
(8, 1, '2024-06-07', 7.5),
(9, 2, '2024-06-06', 5.5),
(10, 1, '2024-06-08', 8.0);


----------------------------------------------------------
-- STEP 3: Create a View
----------------------------------------------------------
GO
CREATE VIEW timesheet.v_EmployeeHours AS -- This view returns each employee name with the date and hours they worked.
-- It uses a LEFT JOIN to include employees even if they have no timesheet records.
SELECT e.name, t.work_date, t.hours_worked
FROM timesheet.Employees e
LEFT JOIN timesheet.Timesheets t ON e.employee_id = t.employee_id;
GO

----------------------------------------------------------
-- STEP 4: Materialized View
----------------------------------------------------------

CREATE VIEW timesheet.v_TotalHoursPerEmployee
WITH SCHEMABINDING
AS
SELECT t.employee_id, COUNT_BIG(*) AS entries, SUM(ISNULL(t.hours_worked, 0)) AS total_hours
FROM timesheet.Timesheets t
GROUP BY t.employee_id;
GO

-- Create the clustered index to actually materialize the view
CREATE UNIQUE CLUSTERED INDEX ix_TotalHoursPerEmployee
ON timesheet.v_TotalHoursPerEmployee(employee_id)
GO

----------------------------------------------------------
-- STEP 5: Query - group by
----------------------------------------------------------

-- Retrieve the total hours worked per day across all employees.
SELECT 
    work_date,                             -- The date of the work entry
    SUM(hours_worked) AS total_per_day     -- Total hours worked on that date across all employees
FROM 
    timesheet.Timesheets                   -- Source: the timesheet records
GROUP BY 
    work_date;                             -- Grouping by date ensures one row per work_date
GO

----------------------------------------------------------
-- STEP 6: Query - left join
----------------------------------------------------------

-- Get a combined view of employees and their work entries.
-- The LEFT JOIN ensures that employees without timesheet entries are still shown,
-- which helps identify missing logs or inactive employees.

SELECT 
    e.name,                                -- Employee's name from the Employees table
    t.work_date,                           -- Date of the timesheet entry 
    t.hours_worked                         -- Number of hours worked on that day 
FROM 
    timesheet.Employees e                  -- Source: list of all employees
LEFT JOIN 
    timesheet.Timesheets t                 -- Joining with work records
    ON e.employee_id = t.employee_id;      -- Join condition: match employee IDs
GO

----------------------------------------------------------
-- STEP 7: Query - analytic function
----------------------------------------------------------

-- Calculate the average number of hours each employee worked across all their entries.
-- The AVG() OVER(PARTITION BY ...) function computes a running average per employee.


SELECT 
    name,                                  -- Employee's name
    work_date,                             -- Specific date of work
    hours_worked,                          -- Hours worked on that day
    AVG(hours_worked) OVER (PARTITION BY name) AS avg_hours 
                                           -- Calculates average hours for each employee (partitioned by name)
                                           -- The result shows how each day compares to their average
FROM 
    timesheet.v_EmployeeHours;             -- View that includes employee name, work date, and hours
GO
