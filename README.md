# Property-Manager-Django

change the following description:
This is a property title, description and summary generator application using `Ollama` which uses hotel informations from a [property-manager-django](https://github.com/nthalt/property-manager-django) project database and stores newly generated title, description, summary into the same postgres database. The title is generated based on the previous title, the description is generated based on th newly generated title. And the summary is generated using title, description, location, amenities of each property. The summary of each property is stored in a new PropertySummary table. The admin panel provides the property, location, amenity, propertyImage, PropertySummary models for visualizing and managing data.
For anyone interested, the Scrapy project can be found here [https://github.com/nthalt/property-manager-django](https://github.com/nthalt/property-manager-django).

- [Requirements](#requirements)
- [Features](#features)
- [Setup and Installation](#setup-and-installation)
- [Important Notes](#important-notes)
- [Database Schema](#database-schema)
  - [properties_property](#properties_property)
  - [properties_location](#properties_location)
  - [properties_amenity](#properties_amenity)
  - [properties_propertyimage](#properties_propertyimage)
- [Contributing](#contributing)

## Requirements

- [Python 3 or higher](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Django](https://www.djangoproject.com/)
- [Ollama](https://ollama.com/download)
- Run the property-manager-django project from here [https://github.com/nthalt/property-manager-django](https://github.com/nthalt/property-manager-django)

## Features
change this too:
1. Uses Django Model(s) and migrations
2. Uses Django admin with proper authentication
3. Enables CRUD operations for all the models maintaining relationship from
   Django admin panel
4. Provides a Django CLI application to migrate all the data from
   Scrapy project database to Django
5. Uses postgres database
6. Uses Django ORM

## Setup and Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/nthalt/llm-project.git
   cd llm-project
   ```

   Make sure the `property-manager-django` directory and `llm-project` directory are under the same parent directory. Please maintain the following directory structure, otherwise `property-manager-django` project data will not be used properly.

   ```bash
   .
   ├── llm-project/
   └── property-manager-django/
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate # On Windows use: venv\Scripts\activate
   ```

3. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a file named .env in the project root and add your PostgreSQL database connection details. Use .env.example as a reference. Scrapy database name is provided for convenience**

   ```bash
   cp .env.example .env
   ```
   Make sure to provide the database name where the data will be updated i.e. `DB_NAME=django_hotel_db`. Also provide other relevent environment informations.

5. **Make sure Postgresql database engine is installed and running**

6. **You should already have the `django_hotel_db` database created from the property-manager-django project. If you don't have the database, you need to run the property-manager-django project from this link: [https://github.com/nthalt/property-manager-django](https://github.com/nthalt/property-manager-django)**

    - If you have previously run it and have the database, then you can skip this step.

<!-- 7. **Create the migration files**

   ```bash
   python manage.py makemigrations
   ``` -->

7.  **Apply the migrations to the database**

    ```bash
    python manage.py migrate
    ```

8.  **Generate property title, description and summary using the following command. You can use the `--limit` flag to limit the number of properties to operate on.**

    ```bash
    python manage.py summary --limit=5 # this runs the command for 5 properties. Change it to your liking. There should be 77 properties total. Giving 0 will do nothing.
    ```

    ```bash
    python manage.py summary # this runs the command for all properties.
    ```

9.  **Create an admin user**

    ```bash
    python manage.py createsuperuser
    ```

    Set your desired `Username`,`Email address` and`Password`.

10. **Start the django development server**

    ```bash
    python manage.py runserver
    ```

    The application can be viewed here : [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

### Important Notes:

- Please follow the directory structure mentioned in [Setup and Installation](#setup-and-installation). `property-manager-django` directory and `llm-project` directory should be under the same parent directory.
- Ensure that the database is created according to [https://github.com/nthalt/property-manager-django](https://github.com/nthalt/property-manager-django). If you have previously run it and have the database, then you don't need to do anything.
- Ensure that you have activated the virtual environment before running the `pip install -r requirements.txt` command. This ensures that all dependencies are installed within the virtual environment and do not affect the global Python environment.
- Check if the 

## Database Schema

### Properties

The database schema consists of the following main tables:

#### properties_property

| Column      | Type                     | Constraints                 |
| ----------- | ------------------------ | --------------------------- |
| property_id | integer                  | Primary Key, Auto-increment |
| title       | character varying(255)   | Not Null, Unique            |
| description | text                     |                             |
| create_date | timestamp with time zone | Not Null                    |
| update_date | timestamp with time zone | Not Null                    |

#### properties_amenity

| Column | Type                   | Constraints                 |
| ------ | ---------------------- | --------------------------- |
| id     | bigint                 | Primary Key, Auto-increment |
| name   | character varying(255) | Not Null, Unique            |

#### properties_location

| Column    | Type                   | Constraints                 |
| --------- | ---------------------- | --------------------------- |
| id        | bigint                 | Primary Key, Auto-increment |
| name      | character varying(255) | Not Null                    |
| type      | character varying(100) | Not Null                    |
| latitude  | double precision       |                             |
| longitude | double precision       |                             |

#### properties_propertyimage

| Column      | Type                   | Constraints                 |
| ----------- | ---------------------- | --------------------------- |
| id          | bigint                 | Primary Key, Auto-increment |
| image       | character varying(100) | Not Null                    |
| property_id | integer                | Not Null, Foreign Key       |



### Relationships

- A Property can have multiple PropertyImages (One-to-Many)
- Properties and Locations have a Many-to-Many relationship
- Properties and Amenities have a Many-to-Many relationship

#### llm_app_propertysummary

| Column      | Type                   | Constraints                             |
| ----------- | ---------------------- | --------------------------------------- |
| id          | bigint                 | Primary Key, Auto-increment             |
| summary     | text                   | Not Null                                |
| property_id | integer                | Not Null, Foreign Key, Unique Constraint|
| create_date | timestamp with time zone | Not Null, Auto-set on creation          |
| update_date | timestamp with time zone | Not Null, Auto-updated on modification  |

### Relationships

- A Property has a One-to-One relationship with a PropertySummary (One-to-One)


### Indexing

- Unique constraints are in place for property titles and amenity names
- A composite unique index is created on location name, latitude, and longitude
- Foreign key relationships are established between the tables

### Auto-managed Fields

- `create_date` and `update_date` in the `properties_property` table are automatically managed timestamp fields
- `create_date` and `update_date` in the `llm_app_propertysummary` table are automatically managed timestamp fields

<details>
<summary>

## Contributing

</summary>

We welcome contributions to this project. To ensure a smooth collaboration, please follow these guidelines:

1. **Fork the Repository**: Start by forking the repository on GitHub.

2. **Clone the Repository**: Clone your forked repository to your local machine using:

   ```bash
   git clone https://github.com/username/property-manager-django.git
   ```

3. **Create a Branch**: Create a new branch for your feature or bug fix:

   ```bash
   git checkout -b feature-or-bugfix-description
   ```

4. **Make Changes**: Implement your changes in the codebase. Ensure your code adheres to the project's coding standards and includes appropriate tests.

5. **Commit Changes**: Commit your changes with a clear and descriptive commit message:

   ```bash
   git add .
   git commit -m "Description of the feature or bug fix"
   ```

6. **Push to GitHub**: Push your branch to your forked repository on GitHub:

   ```bash
   git push origin feature-or-bugfix-description
   ```

7. **Create a Pull Request**: Go to the original repository on GitHub and create a pull request. Provide a clear and detailed description of your changes.

8. **Review Process**: Wait for the project maintainers to review your pull request. Be prepared to make any necessary changes based on feedback.

Thank you for your contributions! Your help is greatly appreciated.

</details>