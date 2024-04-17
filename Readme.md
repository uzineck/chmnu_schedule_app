# CHMNU Schedule app
### Stack: Python, Django, Django Ninja, Poetry, Docker, PostgreSQL, Makefile

---

This is the backend part of the schedule app for CHMNU students and teachers.

---

## Requirements:

- [Docker](https://www.docker.com/get-started/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Docker compose](https://docs.docker.com/compose/install/)
- [GNU Make](https://www.gnu.org/software/make/)(on linux), [WSL Ubuntu](https://ubuntu.com/desktop/wsl)(on windows)


---
### How to use(Windows):
1. #### Clone the repo:
    ```bash
   git clone https://github.com/uzineck/chmnu_schedule_app.git
   cd chmnu_schedule_app
   ```
2. #### Install all required packages in `Requirements` section.
3. #### Open Docker Desktop
4. #### Open WSL Ubuntu in your terminal and go to cloned application folder
5. #### Implemented Commands

    - `make app` - up application and database/infrastructure
    - `make app-logs` - follow the logs in app container
    - `make app-down` - down application and all infrastructure
    - `make storages` - up only storages. you should run your application locally for debugging/developing purposes
    - `make storages-logs` - follow the logs in storages containers
    - `make storages-down` - down all infrastructure
6. #### Django Specific Commands

    - `make migrations` - make migrations to models
    - `make migrate` - apply all made migrations
    - `make collectstatic` - collect static
    - `make superuser` - create admin user
    - `make loaddata` - Searches for and loads the contents of the named fixture into the database
    - `make dumpdata` - Outputs to standard output all data in the database associated with the named application



