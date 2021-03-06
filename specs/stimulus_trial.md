---
title: stimtrial specification
---

stimtrial is a format for recording point processes with some associated metadata, intended for storing the processed spiketimes from a neural recording in which one stimulus was presented in each trial

# Schema

Stimtrial is a superset of [pprox](https://meliza.org/spec:2/pprox); it requires a `stimulus` key to each element of the array stored in the `pprox` key, containing a stimulus identifier and the interval in which stimulus was presented.


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
``` json
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

```
