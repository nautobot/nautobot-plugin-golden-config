# Golden Configuration 

A navigation overview of the entire plugin.

# Home

The Home view is a portal to understand what the status of the devices are. 

![Home Overview](./img/golden-overview.png)

Some of the information described in this view, may not be immediately obvious.

* The Backup/Intended/Compliance status will always show the last time the job was successfully ran for that device, but there are several conditions it may be in.
  * Green with a date indicates that the ran was successful, which was the last time the job ran. 
  * Red with a data indicates the last time the job ran successfully, with the last time the job was attempted in be shown when you mouse over the date.
  * A red double-dashed icon indicated the job has never been successful
* The icons are provided in the following order, that largely matches the status.
  * Backups
  * Intended
  * Unix Diff
  * SoT aggregation data
  * Run job

The first four bring up a "modal" or "dialogue box" which has a detailed view for a dedicated page. The run job brings the user to a job to run all three 
components against all of the devices.

# Jobs

There are a series of Jobs that are registered via the Plugin. They can be viewed from the standard Jobs view.

![Job Overview](./img/job-overview.png)

Each Job attempts to provide sane error handling, and respects the `debug` flag to provide more information.

![Job Result](./img/job-result.png)

# Application Settings

The golden configuration plugin settings can be found by navigating to `Plugins -> Settings` button. Under the `Golden Configuration` section.

![Navigate to Settings](./img/navigate-compliance-rules.png)

To configure or update the settings click the pencil icon to edit.

|Setting|Explanation|
|:--|:--|
|Backup Repository | This is the Git Repository where your backup configurations will be found. |
|Backup Path|This represents the Jinja path where the backup files will be found.  The variable `obj` is available as the device instance object of a given device, as is the case for all Jinja templates. e.g. `{{obj.site.slug}}/{{obj.name}}.cfg`|
|Intended Repository | This is the Git Repository where your backup configurations will be found. |
|Intended Path|The Jinja path representation of where the generated file will be places. e.g. `{{obj.site.slug}}/{{obj.name}}.cfg`|
|Jinja Repository | This is the Git Repository where your jinja templates will be found. |
|Jinja Path|The Jinja path representation of where the Jinja temaplte can be found. e.g. `{{obj.platform.slug}}.j2`|
|Scope| This is where the scope of devices to be considered within Golden Config is defined. |
|GraphQL Query|A query that is evaluated and used to render the config. The query must start with `query ($device_id: ID!)`.|

> Note: Each of these will be further detailed in their respective sections.

## Scope

The scope, is a JSON blob that describes a filter that will provide the list of devices to be allowed whenever a job is ran. A job can optionally further refine the scope, but the outbound would be based on what is defined here. The options are best described by leveraging the Devices list view, search features (the filtering shown on the side of the Devices.) Building a query there, will provide the exact keys expected.

Filtering to specific platforms, based on their slug.

```json
{
  "platform": [
    "cisco_ios",
    "cisco_nxos",
    "arista_eos",
    "juniper_junos"
  ]
}
```

> Note: The Platform slug is an important value, see the [FAQ](./FAQ.md) for further details.

Adding a "has_primary_ip" check. 

```json
{
  "platform": [
    "cisco_ios",
    "cisco_nxos",
    "arista_eos",
    "juniper_junos"
  ],
  "has_primary_ip": "True"
}
```

When viewing the settings, the scope of devices is actually a link to the query built in the Devices view. Click that link to understand which devices are permitted by the filter.

# Git Settings

The plugin makes heavy use of the Nautobot git data sources feature. There are up to three repositories used in the application. This set of instructions will walk an operator through setting up the backup repository. The steps are the same, except for the "Provides" field name chosen.

In order to setup this repository, go to Nautobot and navigate to the Data Sources Git integration. `Extensibility -> Git Repositories`.

![Backup Git Navigation](./img/git-step1.png)

From the Git Repositories page we can add the **Backup** repository.

Click on `Add`.

You will now be presented with a page to fill in the repository details.

Parameters:
|Field|Explanation|
|:--|:--|
|Name|User friendly name for the backup repo.|
|Slug|Auto-generated based on the `name` provided.|
|Remote URL|The URL pointing to the Git repo that stores the backup configuration files. Current git url usage is limited to `http` or `https`.|
|Branch|The branch in the Git repo to use. Defaults to `main`.|
|Token|The token is a personal access token for the `username` provided.  For more information on generating a personal access token. [Github Personal Access Token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)
|Username|The Git username that corresponds with the personal access token above.|
|Provides|Valid providers for Git Repo.|
<br>

![Example Git Backups](./img/backup-git-step2.png)

Select `backup configs` and click on `Create`.

Once you click `Create` and the repository syncs, the main page will now show the repo along with its status.
![Git Backup Repo Status](./img/backup-git-step3.png)

For their respective features, the "Provides" field could be backup intended configs and jinja templates.

# Plugins Buttons

The plugins buttons provides you with the ability to navigate to Run the script, overview report, and detailed report.

# Run Script

This can be accessed via the Plugins drop-down via `Run Script` button of the `Home` view, the user will be provided a form of the Job (as described 
above), which will allow the user to limit the scope of the request.

# Device Template Content

The plugin makes use of template content `right_page` in order to use display in-line the status of that device in the traditional Nautobot view. From here you can click the link to see the detail compliance view.

# Site Template Content

The plugin makes use of template content `right_page` in order to use display in-line the status of that entire site in the traditional Nautobot view. 

# API

To run the job programmactially, reference the [nautobot documentation](https://nautobot.readthedocs.io/en/stable/additional-features/jobs/#via-the-api) for the proper API call. Pay special attention to the `class_path` defintion.

# Feature Enablement

Enabling features such as backup or compliance, will render those parts of the UI visible. It is worth noting that disabling features does not provide any
garbage collection and it is up to the operator to remove such data.

# Network Operating System Support

The version of OS's supported is documented in the [FAQ](./FAQ.md) and is controlled the platform slug. The platform slug must be exactly as expected for the plugin to work.