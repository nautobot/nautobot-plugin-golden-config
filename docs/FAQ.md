# Frequently Asked Questions

_Why don't the configurations match like the vendor cli?_

A vendor processes configuration understanding constructs such as knowing that `int g0/0` and `interface GigabitEthernet0/0` are the same. Each one of these 
rules a subject to a given vendor's OS implementation. The ability to track these changes for all vendors/OS/versions is nearly impossible. Additionally, 
this practice would be error prone and not follow the principal of least astonishment. Notwithstanding a major change in the network industry, adjusting 
this strategy is outside the scope of the plugin. 

Instead, it is up to the operator to ensure their configurations match exactly as the configurations show in the running configuration.

_Why doesn't the config overview page reflect the inclusion changes immediately?_

On a technical level, those changes enable the model `GoldenConfiguration` to *not* filter out the newly included devices, but this does not add to the
model. In order to be included, a new job needs to be ran which will create an entry within `GoldenConfiguration`, any of the 3 jobs that successfully run
will create such an entry.

_Why aren't configurations generated or compliance generated real time?_

The plugin make no assumptions about your intention and expects the operator to manage the configurations as they see fit. As as example, in preparation for 
a change, one may update data to reflect these changes, but not want to generate or run compliance against these configurations. Additionally, 
configurations generated would have to either update the Git Repo immediately or generate locally only and not update the Git Repo, both of which may not be 
as the user expected.

The current design allows for the maximum amount of use cases and make little assumptions how the user wants to manage their configurations. That being
said, education about how the process works is important as inevitably any design choice will not be line with another person's pre-conceived notions. There 
are a myriad of technical issues to be considered before any change can be made to this process.

_Why not predefine a list of remove and substitute lines within backup configurations?_

Backup configurations solutions are simple to start with and grow to hundreds or thousands of requests. That added complexity is not something that is in scope for the project.

Many people will have different opinions about what should or should not be filtered or substituted. Providing the flexibility allows the user to have it
operate as they intend it, without burdening the plugins goals.

_Why not predefine the configuration feature map?_

The process is based on an opinion on what defines a feature, for one organization BGP may include the prefix configuration and another it would not.
Understanding that there will never be consensus on what should go into a feature it becomes obvious why the users must maintain such configuration.

_What are the supported platforms? How do I configure a device with a specific OS?_

The current supported platform and the associated *required* platform slug names are the following:

* arista_eos
* cisco_ios
* cisco_nxos
* cisco_aireos
* linux
* bigip_f5
* juniper_junos

In many use cases, this can be extended with a custom dispatcher, which is controlled in the [nornir-nautobot](https://github.com/nautobot/nornir-nautobot) repository.

_Why not provide the corrective configurations?_

Configuration enforcement is a difficult problem to attack. While potentially could integrate with a system to provide the enforcement, this is currently 
out-of-scope for the plugin.

_Why does the compliance section scroll so much?_

The real estate optimizations is not the best for the configuration compliance overview right now. Users are suggested to review the best practices
described in the configuration compliance section. Over time, the hope is to optimize this.