---
title: stimtrial specification
---

stimtrial is a format for recording point processes with some associated metadata, intended for storing the processed spiketimes from a neural recording in which one stimulus was presented in each trial

-   Name: <https://meliza.org/spec:2/stimtrial>
-   Schema: <https://meliza.org/spec:2/stimtrial.json>
-   Extends: [pprox](https://meliza.org/spec:2/pprox) 1.0
-   Editor: Dan Meliza (dan at meliza.org)
-   Version: 1.0
-   Status: draft

## Schema

Stimtrial is a superset of [pprox](https://meliza.org/spec:2/pprox). Each element of the array stored in the `pprox` key MUST have:

- an `interval` field, an array with exactly two numbers: the start and end of the trial (the period in which events were recorded), in seconds, relative to `offset`, if present. pprox leaves this field optional, but a point process needs a defined interval for quantities like the firing rate to be meaningful. The `events` SHOULD fall within the interval.
- a `stimulus` field, a map containing a stimulus identifier (`name`) and the interval in which the stimulus was presented (`interval`, also relative to `offset`, if present).


Here is a minimal example:

~~~ json
{
  "$schema": "https://meliza.org/spec:2/stimtrial.json#",
  "pprox": [ {
    "events": [],
    "interval": [0.0, 10.0],
    "stimulus": {
	    "name": "uuid:40814298-d447-4855-93e3-8aa1e23f06b5",
	    "interval": [2.0, 2.89]
    }
   } ]
}
~~~

Here is an example with example metadata:

~~~ json
{
  "$schema": "https://meliza.org/spec:2/stimtrial.json#",
  "unit": "uuid:9b7d15cb-6529-4f99-889b-d2bfb5126fbd",
  "subject": "uuid:629d1161-9e52-443f-84be-14024405c2c2",
  "source_recording": "uuid:e124679f-0dc0-433a-8b25-a4d8f19d122a",
  "recorded_by": "dmeliza",
  "recorded_date": "2012-10-22",
  "sorted_by": "dmeliza",
  "sorted_date": "2012-11-19",
  "pprox": [
    {
      "offset": 0.0,
      "index": 0,
      "stimulus": {
        "name": "uuid:d2e8e43b-1243-47d7-b102-f4e2833f09bd",
        "interval": [1.0, 4.23]
      },
      "trial": "uuid:a2fdfe1d-a65e-4c12-808e-4de358ad13bb",
      "events": [0.002, 0.3, 1.102, 1.115, 1.271, 4.231],
      "interval": [0, 5.0]
    },
    {
      "offset": 6.23,
      "index": 1,
      "stimulus": {
        "name": "uuid:40814298-d447-4855-93e3-8aa1e23f06b5",
        "interval": [1.0, 6.21]
      },
      "trial": "uuid:5fdb32e8-ff55-44a6-9b03-3a2f59df65eb",
      "events": [0.122, 0.453, 1.298, 2.892, 5.624],
      "interval": [0, 10.0]
    }
  ]
}

~~~

### Auxiliary signals

A trial MAY contain an `aux` field recording pulses on other signals recorded alongside the stimulus, such as an output sent to an optogenetic light source or the TTL output of a sensor. If present, `aux` MUST be an array with one object for each pulse that starts in the trial. Each object MUST have a `name` field identifying the signal, and an `interval` field with the start and end time of the pulse, in seconds, relative to `offset`, if present, like the stimulus interval. A pulse that continues past the end of the trial is not clipped. Each object MAY have additional fields describing the pulse. When `aux` is used, a trial without any pulses SHOULD have an empty array, so that "no pulses" can be distinguished from "not recorded".

A collection that uses `aux` SHOULD include an `aux_tracks` field, a map from the name of each signal to an object describing its source (e.g. the recording channel), so this information is not repeated in every trial.

~~~ json
{
  "$schema": "https://meliza.org/spec:2/stimtrial.json#",
  "aux_tracks": {"led": {"channel": "ADC4"}},
  "pprox": [
    {
      "offset": 3.2698,
      "index": 0,
      "interval": [-0.5, 2.1200],
      "stimulus": {"name": "arc607_CB", "interval": [0.0, 1.52]},
      "aux": [],
      "events": [0.123, 0.524]
    },
    {
      "offset": 13.4878,
      "index": 4,
      "interval": [-0.5, 2.2423],
      "stimulus": {"name": "arc605_G", "interval": [0.0, 1.20]},
      "aux": [{"name": "led", "interval": [0.0, 1.0]}],
      "events": [0.051, 0.712, 1.020]
    }
  ]
}
~~~
