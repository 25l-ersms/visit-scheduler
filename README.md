# Visit scheduler

## Development
### Dependencies
The dependency tool used is [Poetry](https://python-poetry.org/). 
It has to be installed and used in order to correctly add dependencies to the project.
### Development
This should be started using fastapi. 
```bash
fastapi dev .\visit_scheduler\app\main.py --port 8080
 ```
### Build
To test the build there is a Dockerfile in this repo and docker-compose.yml in different repo, that enables to test e2e. 
