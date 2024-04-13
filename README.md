# PostalServiceRouting - An Efficient Package Routing Program
A Solution to the Traveling Salesman Problem 
By Jonathan Lane
## Overview
This project is an advanced solution to the Traveling Salesman Problem (TSP), or more closely, the Vehicle Routing Problem (VRP). It aims to optimize the delivery of parcels across a city, ensuring all packages are delivered within a specific timeframe and under a total distance constraint. Utilizing object-oriented programming principles and a genetic algorithm, the program results in efficient static route(s) that help the user manage the logistics of parcel delivery. After utilizing the genetic algorithm when creating routes, the program takes steps to further optimize the routes when they are reused for delivery. The self-adjusting genetic algorithm continually refines the static delivery route(s) based on a variety of metrics including distance, route density, and deviation from theoretically ideal routes.

A pre-generated route is provided in `data/saved_routes.csv` (this was generated using the genetic algorithm using 1 route, 100000 generations, and 10000 population size). The program will automatically load this route, but there is an additional option, as well as a backup of the pre-generated route, in case you want to try generating a different list of routes. A graphic that visualizes the pre-generated routes is provided in the root directory and in `data/routes_backup`.
## Features
- **Genetic Algorithm**: Utilizes mutation and crossover techniques to evolve route solutions generation by generation, aiming to minimize total travel distance while adhering to package constraints.
- **Self-Adjusting Data Structures**: Incorporates `RouteList` and `Location` classes, enabling dynamic route management and address standardization to enhance route optimization.
- **Priority Scheduling Algorithm**: Prioritizes packages based on special delivery requirements and deadlines to ensure timely deliveries.
- **Object-Oriented Data Handling**: Utilizes data from the provided WGUPS distance tables and package files, converting them into structured data classes that facilitate rapid and maintainable access and manipulation.
- ""Pre-Generated Route Loading"": Allows the user to load a pre-generated route from a CSV file, providing a quick and efficient way to test the program without waiting for the genetic algorithm to generate a new route.
  - A backup of the pre-generated route is also provided in `data/routes_backup` case the user wants to revert to the originally provided route.
## Assumptions
- Each truck can carry a maximum of 16 packages, and the ID number of each package is unique.
- The trucks travel at an average speed of 18 miles per hour and have an infinite amount of gas with no need to stop.
- There are no collisions.
- Three trucks and two drivers are available for deliveries. Each driver stays with the same truck as long as that truck is in service.
- Drivers leave the hub no earlier than 8:00 a.m., with the truck loaded, and can return to the hub for packages if needed.
- The delivery and loading times are instantaneous (i.e., no time passes while at a delivery or when moving packages to a truck at the hub). This time is factored into the calculation of the average speed of the trucks.
- There is up to one special note associated with a package. (However, my implementation actually supports multiple notes per package.)
- The delivery address for package #9, Third District Juvenile Court, is wrong and will be corrected at 10:20 a.m. WGUPS is aware that the address is incorrect and will be updated at 10:20 a.m. However, WGUPS does not know the correct address (410 S. State St., Salt Lake City, UT 84111) until 10:20 a.m.
- The distances provided in the “WGUPS Distance Table” are equal regardless of the direction traveled.
- The day ends when all 40 packages have been delivered.
## Installation Guide
### 1. Clone the Repository to Your Machine
Grab the project from GitHub with this command:
```bash
git clone https://github.com/jmsuan/PostalServiceRouting
```
### 2. Go to the Project Folder
Change to the project directory using:
```bash
cd PostalServiceRouting
```
### 3. Setup a Virtual Environment (Optional)
This step is optional. If you want everything neat and isolated, set up a virtual environment (make sure this is in the project's root directory):
```bash
python -m venv venv
```
### 4. Activate the Virtual Environment (Optional)
If you created a virtual environment, activate it with:
- Windows:
  ```bash
  venv\Scripts\activate
  ```
- MacOS or Linux:
  ```bash
  source venv/bin/activate
  ```
### 5. Run the Program
```bash
python src/main.py
```
## Usage
Follow the command-line prompts to interact with the program. You can view the status of all packages at specific times and the total mileage traveled by all trucks at the end of the day. A pre-generated route is provided in data/saved_routes.csv (this was generated using the genetic algorithm using 1 route, 100000 generations, and 10000 population size). The program will automatically load this route, but there is an additional option, as well as a backup of the pre-generated route, in case you want to try generating a different list of routes.
## Implementation Details
- The genetic algorithm's effectiveness is augmented from the standard implementation by utilizing a semantic crossover method that enhances the diversity of route solutions while preventing convergence on sub-optimal routes.
- The program is designed with maintainability in mind, utilizing object-oriented programming principles and detailed documentation to ensure ease of updates and customization.
## Environment
- **Software**: Developed in Python 3.12.2 using JetBrains PyCharm IDE, without external libraries beyond the standard Python toolkit.
- **Hardware**: Tested on an ASUS ROG Zephyrus Duo 16 (2023) laptop, leveraging high-performance components to ensure responsive algorithm execution.
## License
Please contact the author for licensing information.
## Acknowledgments
Western Governors University for providing the project scenario and data files.
