---
title: pprox specification
redirect_from:
  - /specifications/pproc-json/
  - /spec:2/
---

`pprox` is a simple, extensible, and portable schema for point process (time of event) data.

-   Name: <https://meliza.org/spec:2/pprox> (2/pprox)
-   Schema: <https://meliza.org/spec:2/pprox.json>
-   Editor: Dan Meliza (dan at meliza.org)
-   Version: 1.0
-   Status:  raw
-   MIME types: `application/vnd.meliza-org.pprox+json; version=1.0`, `application/vnd.meliza-org.pprox+edn; version=1.0`

## 1 Goals

Electrophysiological, behavioral, and bioacoustic experiments frequently generate data that consist of a sequence of events taking place at discrete times. This kind of data is known as a point process. The events may be associated with additional attributes like duration, spike width, etc. The goal of this specification is to facilitate open and repeatable handling of point process data. The schema should

- Define a minimalistic representation of temporal point processes and collections of point processes
- Flexibly accommodate additional attributes of processes and collections
- Be trivial to serialize and deserialize as documents and/or data streams
- Be readily manipulated in any modern programming language

The use cases for `pprox` include:

- sequences of spike times, optionally marked with attributes of the spikes
- sequences of event times for stimuli and responses in operant behavioral experiments
- onsets, durations, and labels for components of vocalizations and other bioacoustic signals
- onsets, durations, and labels for manually or automatically coded behavioral states and events (i.e., ethograms)

`pprox` is not intended to handle densely sampled time series data, like microphone recordings, raw voltage traces from extracellular or intracellular recordings, or images. Many formats already exist for these kinds of data. However, the schema can be used in combination with densely sampled data; for example, a `pprox` file containing label data could accompany an acoustic recording stored in WAV format.

## 2 Schema

`pprox` can be implemented in any data structure that supports nested key-value pairs and arrays. The snippets below are in Javascript Object Notation ([json](https://json.org)), because this is expected to be the predominant form of serialization, but can easily be translated to your favorite structure or notation, such as Python dictionaries, Ruby hashes, [edn](https://github.com/edn-format/edn), or even XML, if you're a masochist. The text uses *map* or *object* to indicate a collection of key-value pairs, *field* to indicate a single key-value pair, and *array* to indicate an ordered, homogeneous sequence.

The schema defines two kinds of objects: **point processes** (`pproc`)and **collections** (`pprox`). A point process is a map that contains an array of event times. A collection is an aggregate of point processes.

### 2.1 Point processes

A minimal point process looks like this:

~~~ json
{
  "events": [1.1, 1.2304, 1.24]
}
~~~

The `events` field is REQUIRED. It MUST be an array of numerical values, in units of seconds. A point process MAY contain two optional fields: `offset` and `marks`. If present, `offset` MUST be a single numerical value that indicates a relative temporal offset, in seconds, for all the events. If present, `marks` MUST be an map containing one or more fields. Each field in `marks` MUST be an array that corresponds one-to-one with the `events` array. Any number of additional fields MAY be used to store metadata. Keys MUST be unique and MUST NOT conflict with any of the required or optional fields described above.

Let's consider some example use cases. First, extracellular spike times recorded in response to a presented stimulus. We code the stimulus identity using a
[UUID](http://tools.ietf.org/html/rfc4122.html) and indicate the start and stop times of the stimulus with the `stimulus_on` and `stimulus_off` fields. We could also code the stimulus using a more human-readable name, but globally unique identifiers help to avoid confusion down the road. Because this is part of a larger experiment in which many stimuli were presented, we've also stored a relative offset time and an index for the trial.

~~~ json
{
  "offset": 5.23,
  "index": 1,
  "stimulus": "uuid:d2e8e43b-1243-47d7-b102-f4e2833f09bd",
  "stimulus_on": 1.0,
  "stimulus_off": 4.23,
  "events": [0.002, 0.3, 1.102, 1.115, 1.271, 4.231]
}
~~~

We might be recording spikes from an animal engaged in an operant task. To accommodate the behavioral data, we've added an array for times when the animal pecked and information about the consequences of its choice. For illustration, we've also added some additional data from a temperature sensor, which is stored as a map with a field for units. We've also added identifiers for the trial and the recording unit, which would allow us to cross-reference this trial with data from the same unit and trial. For example, instead of storing the concurrent peck events in this point process, as we've done here, we could store them in a separate object with the same trial id.

~~~ json
{
  "events": [1.1, 1.2304, 1.24],
  "unit": "uuid:9b7d15cb-6529-4f99-889b-d2bfb5126fbd",
  "trial": "uuid:d2e8e43b-1243-47d7-b102-f4e2833f09bd",
  "stimulus": "uuid:c0c0d6f2-8283-4bd3-b162-2102c7411ee2",
  "stimulus_on": 1.0,
  "stimulus_off": 4.23,
  "peck_t": [2.23, 4.40, 4.601],
  "consequence": "reward",
  "consequence_on": 5.321,
  "consequence_off": 6.321,
  "room_temp": {"value": 25.0, "units": "C"}
}
~~~

Let's consider marked point processes. In an intracellular recording, we might want to include some measurements of the spike waveforms, as these can change in bursts. These measurements are stored as arrays in the `marks` field. Note that the arrays have the same number of elements as `events`. It's presumed that `spike_height[0]` corresponds to `events[0]` and so forth. Here we've also chosen to describe the stimulus using a few parameters rather than making a reference to some external entity.

~~~ json
{
  "index": 2,
  "protocol": "step",
  "amplitude": {"value", 100, "units": "pA"},
  "step_on": 0.2,
  "step_off": 2.2,
  "events": [0.212, 0.224, 0.307]
  "marks": {
    "spike_height": [10.1, 2.23, -0.29],
    "spike_width": [1.12, 1.79, 2.22]
  }
}
~~~

Finally, let's look a set of syllable labels for a zebra finch song recording. The `event` field stores the start times of the syllables, and the marks indicate the duration of the syllables and the assigned label. The metadata fields store information about the (imaginary) program used to generate the labels, the recording file the labels reference, and the bird that produced the song. This example also illustrates using URLs as identifiers, which serves two purposes. The domain acts as a namespace so that the shorter ids are still globally unique, and the URL provides end-users with a link to obtain more information. URL identifiers are especially useful in a public API.

~~~ json
{
  "vocalizer": "https://melizalab.org/birds/38bb8d1f/",
  "recording": "https://melizalab.org/songs/d9c73127/",
  "labeled_by": "autolabeller_v3.0",
  "labeled_on": "2018-01-28T16:16:48Z",
  "events": [0.502, 0.850, 1.211],
  "marks": {
    "duration": [0.32, 0.259, 0.491],
    "label": ["A", "B", "C"],
  }
}
~~~

### 2.2 Collections

Point process data are often part of collections. For example, a single unit may be tested with many different stimuli, and each stimulus may be repeated several times. In `pprox`, a collection is simply a map that contains one or more point processes in an array. Here's a minimal collection that contains one trial with no events:

~~~ json
{
  "$schema": "https://meliza.org/spec:2/pprox.json#",
  "pprox": [ { "events": [], } ]
}
~~~

The `pprox` field is REQUIRED and MUST be an array of `pproc` objects. The `$schema` field SHOULD be used. The value of this field MUST be a [URI](http://tools.ietf.org/html/rfc3986) and SHOULD refer to the most restrictive specification for the contents of the document. That is, if you've extended this schema for a specific application, you should reference the extended schema. Any number of additional fields MAY be included as metadata.

Let's look at how we might collect all the data associated with a single extracellular unit. Metadata for the unit are stored at the collection level, including the experimenter, identifiers for the unit, the experimental subject, and for the file that contains the raw data. Other metadata is trial-specific and is stored in each point process.

~~~ json
{
  "$schema": "https://meliza.org/spec:2/pprox.json#",
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
      "stimulus": "uuid:d2e8e43b-1243-47d7-b102-f4e2833f09bd",
      "trial": "uuid:a2fdfe1d-a65e-4c12-808e-4de358ad13bb",
      "stimulus_on": 1.0,
      "stimulus_off": 4.23,
      "events": [0.002, 0.3, 1.102, 1.115, 1.271, 4.231]
    },
    {
      "offset": 6.23,
      "index": 1,
      "stimulus": "uuid:40814298-d447-4855-93e3-8aa1e23f06b5",
      "trial": "uuid:5fdb32e8-ff55-44a6-9b03-3a2f59df65eb",
      "stimulus_on": 1.0,
      "stimulus_off": 6.21,
      "events": [0.122, 0.453, 1.298, 2.892, 5.624]
    }
  ]
}
~~~

## 3 Notes

### 3.1 Extending the schema

As the examples above illustrate, metadata are important for users to be able to interpret the structure of an experiment. Deciding what metadata to include and how to organize it involves problems akin to those of experimental design, and as such, not trivial. No general-purpose schema or open data standard can make these decisions for you. `pprox` is intended to be general and extensible. You should extend it for specific use cases in your lab, by defining required fields and specifying how they should be interpreted. Do this before you collect data, request comments, and register the spec somewhere. You're doing this already for bench protocols and experimental designs, right?  Revise specs as needed, but under version control, so that if someone wants to use your data, you can point them to the correct version.

### 3.2 Storage and transmission

The `pprox` schema can be serialized in any format that supports nested maps and arrays. Compatible formats include JSON, BSON, YAML, and edn.

Files that contain serialized `pprox` data SHOULD use an extension that indicates the serialization format. Code SHOULD check the `$schema` field to determine which version of the spec to use in parsing the data. When transmitting `pprox` data over a network using HTTP, servers SHOULD use the MIME media type `application/vnd.meliza-org.pprox+json; version=1.0`, replacing `json` with the serialization format being used. Clients requesting `pprox` data SHOULD use this MIME type in the Accepts header to inform servers of the preferred format.

In most cases, data should be serialized as a `pprox` collection rather than as individual `pproc` objects.  Collection contents should reflect the structure of the experiment and minimize the amount of duplicated metadata.

However, in applications where data need to be streamed (e.g., live visualization of ongoing acquisition), serialization protocols that have enclosing delimiters (like JSON) cannot be used. One solution is to use a format like YAML or [ZPL](https://rfc.zeromq.org/spec:4/ZPL). Another solution is to send top-level metadata separately and then stream individual `pproc` objects.

## Licence

Copyright (c) 2016-2018 C Daniel Meliza.

This Specification is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This Specification is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program; if not, see <http://www.gnu.org/licenses>.

## Change Process

This Specification is a free and open Consensus-Oriented Specification System ([COSS](https://rfc.unprotocols.org/spec:2/COSS/)).

Version numbering is [semantic](http://semver.org). Changes that
maintain backwards compatibility (i.e., that do not change or remove any
required fields and attributes) result in increments to the minor version.
Changes that break backwards compatibility must receive new major version
numbers. Changes that significantly alter the goals of the specification must
result in a new identifier, preferably with a reference to the version of this
document at the time of the fork.

## Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](http://tools.ietf.org/html/rfc2119).
