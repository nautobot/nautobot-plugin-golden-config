# nautobot-golden-config

A plugin for [Nautobot](https://github.com/nautobot/nautobot) that intends to provide context around golden configuration.

**This version is currently in Beta and will require a rebuild of the database for a 1.0 release.**

# Overview

You may see the [Navigating Overview](./docs/navigating-golden.md) documentation for an overview of navigating through the different areas of this plugin. You may also see the [FAQ](./docs/FAQ.md) for commonly asked questions.

The golden configuration plugin performs four primary actions, each of which can be toggled on with a respective `enable_*` setting, covered in detail 
later in the readme. 

* Configuration Backup - Is a Nornir process to connect to devices, optionally parse out lines/secrets, backup the configuration, and save to a Git repository.
    * see [Navigating Backup](./docs/navigating-backup.md) for more information
* Configuration Intended - Is a Nornir process to generate configuration based on a Git repo of Jinja files and a Git repo to store the intended configuration.
    * see [Navigating Intended](./docs/navigating-intended.md) for more information
* Source of Truth Aggregation - Is a GraphQL query per device with that creates a data structure used in the generation of configuration.
    * see [Navigating SoTAgg](./docs/navigating-sot-agg.md) for more information
* Configuration Compliance - Is a Nornir process to run comparison of the actual (via backups) and intended (via Jinja file creation) CLI configurations.
    * see [Navigating Compliance](./docs/navigating-compliance.md) for more information

The operator's of their own Nautobot instance are welcome to use any combination of these features. Though the appearance may seem like they are tightly 
coupled, this isn't actually the case. For example, one can obtain backup configurations from their current RANCID/Oxidized process and simply provide a Git Repo
of the location of the backup configurations, and the compliance process would work the same way. Also, another user may only want to generate configurations, but not want to use other features, which is perfectly fine to do so.

## Screenshots

There are many features and capabilities the plugin provides into the Nautobot ecosystem. The following screenshots are intended to provide a quick visual overview of some of these features.

The golden configuration is driven by jobs that run a series of tasks and the result is captured in this overview.

![Compliance Rule](./docs/img/golden-overview.png)

The compliance report provides a high-level overview on the compliance of your network.
![Compliance Report](./docs/img/compliance-report.png)

The compliance overview will provide a per device and feature overview on the compliance of your network devices.
![Compliance Overview](./docs/img/compliance-overview.png)

Drilling into a specific device and feature, you can get an immediate detailed understanding of your device.
![Compliance Device](./docs/img/compliance-device.png)

![Compliance Rule](./docs/img/compliance-rule.png)

## Plugin Settings

There is a setting to determine the inclusion of any of the four given components.

* The `enable_backup`, `enable_compliance`, `enable_intended`, and `enable_sotagg` will toggle inclusion of the entire component.

# Installation

Plugins can be installed manually or use Python's `pip`. See the [nautobot documentation](https://nautobot.readthedocs.io/en/latest/plugins/#install-the-package) for more details. The pip package name for this plugin is [`nautobot-golden-config`](https://pypi.org/project/nautobot-golden-config/)

> The plugin is compatible with Nautobot 1.0.0 and higher

**Prerequisite:** The plugin relies on [`nautobot_plugin_nornir`](https://pypi.org/project/nautobot-plugin-nornir/) to be installed and both plugins to be enabled in your configuration settings.

**Required:** The following block of code below shows the additional configuration required to be added to your `nautobot_config.py` file:
- append `"nautobot_golden_config"` to the `PLUGINS` list
- append the `"nautobot_golden_config"` dictionary to the `PLUGINS_CONFIG` dictionary

```python
PLUGINS = ["nautobot_plugin_nornir", "nautobot_golden_config"]

PLUGINS_CONFIG = {
    "nautobot_plugin_nornir": {
        "nornir_settings": {
            "credentials": "nautobot_plugin_nornir.plugins.credentials.env_vars.CredentialsEnvVars",
            "runner": {
                "plugin": "threaded",
                "options": {
                    "num_workers": 20,
                },
            },
        },
    },
    "nautobot_golden_config": {
        "per_feature_bar_width": 0.15,
        "per_feature_width": 13,
        "per_feature_height": 4,
        "enable_backup": True,
        "enable_compliance": True,
        "enable_intended": True,
        "enable_sotagg": True,
        "sot_agg_transposer": None,
        "default_drivers_mapping": None,
    },
}

```

The plugin behavior can be controlled with the following list of settings. 

| Key     | Example | Default | Description                          |
| ------- | ------ | -------- | ------------------------------------- |
| enable_backup | True | True | A boolean to represent whether or not to run backup configurations within the plugin. |
| enable_compliance | True | True | A boolean to represent whether or not to run the compliance process within the plugin. |
| enable_intended | True | True | A boolean to represent whether or not to generate intended configurations within the plugin. |
| enable_sotagg | True | True | A boolean to represent whether or not to provide a GraphQL query per device to allow the intended configuration to provide data variables to the plugin. |
| default_drivers_mapping | {"newos": "dispatcher.newos"} | None | A dictionary in which the key is a platform slug and the value is the import path of the dispatcher in string format|
| sot_agg_transposer | mypkg.transposer | - | A string representation of a function that can post-process the graphQL data. |
| per_feature_bar_width | 0.15 | 0.15 | The width of the table bar within the overview report | 
| per_feature_width | 13 | 13 | The width in inches that the overview table can be. | 
| per_feature_height | 4 | 4 | The height in inches that the overview table can be. | 

> Note: Over time the intention is to make the compliance report more dynamic, but for now allow users to configure the `per_*` configs in a way that fits best for them.

# Contributing

Pull requests are welcomed and automatically built and tested against multiple versions of Python and Nautobot through TravisCI.

The project is packaged with a light development environment based on `docker-compose` to help with the local development of the project and to run tests within TravisCI.

The project is following Network to Code software development guidelines and are leveraging the following:
- Black, Pylint, Bandit, flake8, and pydocstyle for Python linting and formatting.
- Django unit test to ensure the plugin is working properly.

## CLI Helper Commands

The project features a CLI helper based on [invoke](http://www.pyinvoke.org/) to help setup the development environment. The commands are listed below in 3 categories:
- `dev environment`
- `utility`
- `testing`. 

Each command can be executed with `invoke <command>`. All commands support the arguments `--nautobot-ver` and `--python-ver` if you want to manually define the version of Python and Nautobot to use. Each command also has its own help `invoke <command> --help`

### Local dev environment

```
  build            Build all docker images.
  debug            Start Nautobot and its dependencies in debug mode.
  destroy          Destroy all containers and volumes.
  restart          Restart Nautobot and its dependencies in detached mode.
  start            Start Nautobot and its dependencies in detached mode.
  stop             Stop Nautobot and its dependencies.
```

### Utility 

```
  cli              Launch a bash shell inside the running Nautobot container.
  create-user      Create a new user in django (default: admin), will prompt for password.
  makemigrations   Run Make Migration in Django.
  nbshell          Launch a nbshell session.
```

### Testing 

```
  bandit           Run bandit to validate basic static code security analysis.
  black            Run black to check that Python files adhere to its style standards.
  flake8           Run flake8 to check that Python files adhere to its style standards.
  pylint           Run pylint code analysis.
  pydocstyle       Run pydocstyle to validate docstring formatting adheres to NTC defined standards.
  tests            Run all tests for this plugin.
  unittest         Run Django unit tests for the plugin.
```
