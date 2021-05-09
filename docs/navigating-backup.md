# Configuration Backup

The backup configuration process relies on the ability for the nautobot worker to connect via Nornir to the device, run the `show run` or equivalent command 
and save the configuration. The high-level process to run backups is:

* Download the latest Git repository, based on `backup config` type Git repo within Nautobot.
* Run a Nornir play to obtain the cli configurations.
* Optionally perform some lightweight processing of the backup.
* Store the backup configurations locally.
* Push configurations to the remote Git repository.

# Configuration Backup Settings

Backup configurations often need some amount of parsing to stay sane. The two obvious use cases are the ability to remove lines such as the "Last 
Configuration" changed date, as this will cause unnecessary changes the second is to strip out secrets from the configuration. In an effort to support these 
uses cases, the following settings are available and further documented below.

* Line Removals - provides the ability to remove a line based on a regex match.
* LIne Replacements - provides the ability to swap out parts of a line based on a regex match.

Backup configurations rely on a Git Repo, and the plugin registers an additional repository for Git source this access. Within the Nautobot Git 
repositories, there will be a `backup config` option, which there must be one and only one configured for the process to work. For further details, refer 
[to](./navigating-golden.md#git-settings).

The `backup_path_template` provides the ability to dynamically state per device where the configurations should end up in the file structure. Every device is a Django ORM object, tied to the model instance of a `Device` model, and that is represented as `obj`. That means that any valid Device model method is available. This is then compiled via Jinja. This may seem complicated, but the equivalent of `obj` by example would be:

```python
obj = Device.objects.get(name="nyc-rt01")
```

An example would be:
```python
backup_path_template = "{{obj.site.slug}}/{{obj.name}}.cfg"
```

The backup process will automatically create folders as required based on the path definition. 

The `backup_path_template` can be set in the UI.  For navigation details [see](./navigating-golden.md#application-settings).

The credentials/secrets management is further described within the [nautbot-plugin-nornir](https://github.com/nautobot/nautobot-plugin-nornir)
repo. For the simplist use case you can set environment variables for `NAPALM_USERNAME`, `NAPALM_PASSWORD`, and `DEVICE_SECRET`. For more
complicated use cases, please refer to the plugin documentation linked above.

# Line Removals

The line removals settings is a series of regex patterns to identify lines that should be removed. This is helpful as there are usually parts of the
configurations that will change each time. A match simply means to remove.

In order to specify line removals. Navigate to **Plugins -> Line Removals**.  Click the **Add** button and fill out the details.

The remove setting is based on `Platform`.  An example is shown below.
![Line Removals View](./img/00-navigating-backup.png)

# Line Replacements

This is a replacement config with a regex pattern with a single capture groups to replace. This is helpful to strip out secrets.

The replace lines setting is based on `Platform`.  An example is shown below.

![Line Replacements View](./img/01-navigating-backup.png)

The line replace uses Python's `re.sub` method. As shown, a common pattern is to obtain the non-confidential data in a capture group e.g. `()`, and return the rest of the string returned in the backrefence, e.g. `\2`.

```python
re.sub(r"(username\s+\S+\spassword\s+5\s+)\S+(\s+role\s+\S+)", r"\1<redacted_config>\2", config, flags=re.MULTILINE))
```