# EPICS integration

This repository is currently outfitted to integrate directly with SLAC's alarm IOC as used in conjunction with the legacy Alarm Handler. This is critical for a seamless transition between the ALH and NALMS system and will allow for the surfacing of EDM/PyDM alarming indicators (bypass markers) while using the new system. In addition to the bypass indicator, an acknowledgment indicator has also been added to the NALMS alarm IOC, allowing acknowledgment status to be indicated in displays just as bypasses. Postfixes are applied to the end of pv names to create new these new indicator pvs.

The alarm ioc consists of:

* FP postifixed variables for indicating bypass, written to by system
* SV posftixed variables for scanning bypass indicator
* DP postfixed variables for propogating the alarm system's effective PV severity
* ACK postfixed variables indicating acknowledge status (new)
* Group level STATSUMY postfixed variables for the propogating of the alarm system's effective group severity 
* Group level  STATSUMYFP postfixed variablaes for the propogating of the alarm system's effective bypass status


Inside the `nalms-phoebus-alarm-server` Docker image, the script: `phoebus-alarm-server/scripts/update-ioc.py` continually runs and updates the alarm ioc with the pvs' bypass and acknowledgment states. EPICS environment variables may be passed to the image to configure EPICS.

## Generation



Constructed using a template found in `nalms-tools/..`
