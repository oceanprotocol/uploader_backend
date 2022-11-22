# OCEAN-Decentralized Backend Storage

## Description
Initial repository implementing a solution for the Ocean Decentralized Backend storage management service [explained here](https://github.com/oceanprotocol/decentralized_storage_backend/issues/1)

It is a django-based solution benefitting from django-rest-framework for the class based API Views implementation and drf-spectacular for the Swagger based auto documentation of the API usage. 

## Badges
To Be Added after configuration of the CI on Github

## Installation
This is a server-side API based on Python and Django/DRF so first make sure you have python and pip installed.

Then, use virtualenv to isolate your development environment and setup the virtual env for this project.

The server can be run using the `./manage.py runserver` method.

You can create a superuser with `./manage.py createsuperuser` to be able to access the back-office

## Usage
You can navigate the API using the `http://myserver.com/docs/` Swagger based OpenAPI documentation.

## Support
Please open issues on github if you need support of have any questions.

## Roadmap
More integrations/services to be added.

## Contributing
This project is fully open-source, backed by the $OCEAN community and is obviously open for contributions.

The first version has been implemented following the TDD strategy, so please first familiarize yourself with the test suite, which can be run using the `./manage.py test` command, directly from the root of your server in the context of your virtual environment.

## Authors and acknowledgment
Thanks to the $OCEAN community for the funding and the $OCEAN core team for the technical support and insights.

## License
This project is delivered under a MIT License

## Integrate with your tools

- [ ] [Set up project integrations](https://git.startinblox.com/applications/oceandbs/ocean-dbs/-/settings/integrations)

## Collaborate with your team

- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Automatically merge when pipeline succeeds](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing(SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***