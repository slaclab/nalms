# Converting from ALH

The ALH -> Phoebus Python (>=3.7) conversion tool is handled by a package currently defined in the `nalms-tools` directory. 

```
$ cd nalms-tools
$ pip install -e .
```

The entry point console script is then available with:

```
$ convert-alh config_name input_filename output_filename
```

Several features of the ALH cannot be translated to Phoebus configurations and are deprecated in NALMS. These are the ALIAS, ACKPV, SEVRCOMMAND, STATCOMMAND, amd BEEPSEVERITY ALH configuration entries. The conversion script will print any failures to STDOUT.

At present, ALH inclusions will parsedd and reserialized into a single Phoebus XML configuration file. Future CS-Studio development with include the ability to accomodate file inclusions within the tree structure such that nested files may be similarly structured.