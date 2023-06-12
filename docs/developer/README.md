# Development
========================

If you're new to Django, see [Getting Started with Django](https://www.djangoproject.com/start/) for an introduction to the framework.

## Local Setup

* Install Docker <https://docs.docker.com/get-docker/>
* Initialize the application:

  ```shell
  cd src
  docker-compose build
  ```
* Run the server: `docker-compose up`

  Press Ctrl-c when you'd like to exit or pass `-d` to run in detached mode.

Visit the running application at [http://localhost:8080](http://localhost:8080).

## Branch Conventions

We use the branch convention of `initials/branch-topic` (ex: `lmm/fix-footer`). This allows for automated deployment to a developer sandbox namespaced to the initials.

## Merging and PRs

History preservation and merge contexts are more important to us than a clean and linear history, so we will merge instead of rebasing. 
To bring your feature branch up-to-date wih main:

```
git checkout main
git pull
git checkout <feature-branch>
git merge orgin/main
git push
```

Resources:
- [https://frontend.turing.edu/lessons/module-3/merge-vs-rebase.html](https://frontend.turing.edu/lessons/module-3/merge-vs-rebase.html)
- [https://www.atlassian.com/git/tutorials/merging-vs-rebasing](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
- [https://www.simplilearn.com/git-rebase-vs-merge-article](https://www.simplilearn.com/git-rebase-vs-merge-article)

## Setting Vars

Non-secret environment variables for local development are set in [src/docker-compose.yml](../../src/docker-compose.yml).

Secrets (for example, if you'd like to have a working Login.gov authentication) go in `.env` in [src/](../../src/) with contents like this:

```
DJANGO_SECRET_LOGIN_KEY="<...>"
```

You'll need to create the `.env` file yourself. Get started by running:

```shell
cd src
cp ./.env-example .env
```

Get the secrets from Cloud.gov by running `cf env getgov-YOURSANDBOX`. More information is available in [rotate_application_secrets.md](../operations/runbooks/rotate_application_secrets.md).

## Adding user to /admin

The endpoint /admin can be used to view and manage site content, including but not limited to user information and the list of current applications in the database. To be able to view and use /admin locally:

1. Login via login.gov
2. Go to the home page and make sure you can see the part where you can submit an application
3. Go to /admin and it will tell you that UUID is not authorized, copy that UUID for use in 4
4. in src/registrar/fixtures.py add to the ADMINS list in that file by adding your UUID as your username along with your first and last name. See below:

```
 ADMINS = [
        {
            "username": "<UUID here>",
            "first_name": "",
            "last_name": "",
        },
        ...
 ]
```

5. In the browser, navigate to /admins. To verify that all is working correctly, under "domain applications" you should see fake domains with various fake statuses.

## Adding to CODEOWNERS (optional)

The CODEOWNERS file sets the tagged individuals as default reviewers on any Pull Request that changes files that they are marked as owners of.

1. Go to [.github\CODEOWNERS](../../.github/CODEOWNERS)
2. Following the [CODEOWNERS documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners), add yourself as owner to files that you wish to be automatically requested as reviewer for.
   
   For example, if you wish to add yourself as a default reviewer for all pull requests, add your GitHub username to the same line as the `*` designator:  

   ```diff
   - * @abroddrick
   + * @abroddrick @YourGitHubUser
   ```

3. Create a pull request to finalize your changes

## Viewing Logs

If you run via `docker-compose up`, you'll see the logs in your terminal.

If you run via `docker-compose up -d`, you can get logs with `docker-compose logs -f`.

You can change the logging verbosity, if needed. Do a web search for "django log level".

## Mock data

There is a `post_migrate` signal in [signals.py](../../src/registrar/signals.py) that will load the fixtures from [fixtures.py](../../src/registrar/fixtures.py), giving you some test data to play with while developing.

See the [database-access README](./database-access.md) for information on how to pull data to update these fixtures.

## Running tests

Crash course on Docker's `run` vs `exec`: in order to run the tests inside of a container, a container must be running. If you already have a container running, you can use `exec`. If you do not, you can use `run`, which will attempt to start one.

To get a container running:

```shell
cd src
docker-compose build
docker-compose up -d
```

Django's test suite:

```shell
docker-compose exec app ./manage.py test
```

OR

```shell
docker-compose exec app python -Wa ./manage.py test  # view deprecation warnings
```

Linters:

```shell
docker-compose exec app ./manage.py lint
```

### Testing behind logged in pages

To test behind logged in pages with external tools, like `pa11y-ci` or `OWASP Zap`, add

```
"registrar.tests.common.MockUserLogin"
```

to MIDDLEWARE in settings.py. **Remove it when you are finished testing.**

### Reducing console noise in tests

Some tests, particularly when using Django's test client, will print errors.

These errors do not indicate test failure, but can make the output hard to read.

To silence them, we have a helper function `less_console_noise`:

```python
from .common import less_console_noise
...
        with less_console_noise():
            # <test code goes here>
```

### Accessibility Scanning

The tool `pa11y-ci` is used to scan pages for compliance with a set of
accessibility rules. The scan runs as part of our CI setup (see
`.github/workflows/test.yaml`) but it can also be run locally. To run locally,
type

```shell
docker-compose run pa11y npm run pa11y-ci
```

The URLs that `pa11y-ci` will scan are configured in `src/.pa11yci`. When new
views and pages are added, their URLs should also be added to that file.

### Security Scanning

The tool OWASP Zap is used for scanning the codebase for compliance with
security rules. The scan runs as part of our CI setup (see
`.github/workflows/test.yaml`) but it can also be run locally. To run locally,
type

```shell
docker-compose run owasp
```

# Images, stylesheets, and JavaScript

We use the U.S. Web Design System (USWDS) for styling our applications.

Static files (images, CSS stylesheets, JavaScripts, etc) are known as "assets".

Assets are stored in `registrar/assets` during development and served from `registrar/public`. During deployment, assets are copied from `registrar/assets` into `registrar/public`. Any assets which need processing, such as USWDS Sass files, are processed before copying.

**Note:** Custom images are added to `/registrar/assets/img/registrar`, keeping them separate from the images copied over by USWDS. However, because the `/img/` directory is listed in `.gitignore`, any files added to `/registrar/assets/img/registrar` will need to be force added (i.e. `git add --force <img-file>`) before they can be deployed. 

We utilize the [uswds-compile tool](https://designsystem.digital.gov/documentation/getting-started/developers/phase-two-compile/) from USWDS to compile and package USWDS assets.

## Making and view style changes

When you run `docker-compose up` the `node` service in the container will begin to watch for changes in the `registrar/assets` folder, and will recompile once any changes are made.

Within the `registrar/assets` folder, the `_theme` folder contains three files initially generated by `uswds-compile`:
1. `_uswds-theme-custom-styles` contains all the custom styles created for this application
2. `_uswds-theme` contains all the custom theme settings (e.g. primary colors, fonts, banner color, etc..)
3. `styles.css` a entry point or index for the styles, forwards all of the other style files used in the project (i.e. the USWDS source code, the settings, and all custom stylesheets).

You can also compile the **Sass** at any time using `npx gulp compile`. Similarly, you can copy over **other static assets** (images and javascript files), using `npx gulp copyAssets`.

## Upgrading USWDS and other JavaScript packages

Version numbers can be manually controlled in `package.json`. Edit that, if desired.

Now run `docker-compose run node npm update`.

Then run `docker-compose up` to recompile and recopy the assets.

Examine the results in the running application (remember to empty your cache!) and commit `package.json` and `package-lock.json` if all is well.

## Finite State Machines

In an effort to keep our domain logic centralized, we are representing the state of 
objects in the application using the [django-fsm](https://github.com/viewflow/django-fsm)
library. See the [ADR number 15](../architecture/decisions/0015-use-django-fs.md) for
more information on the topic.

## Login Time Bug

If you are seeing errors related to openid complaining about issuing a token from the future like this:

```
ERROR [djangooidc.oidc:243] Issued in the future
```

it may help to resync your laptop with time.nist.gov: 

```
sudo sntp -sS time.nist.gov
```
