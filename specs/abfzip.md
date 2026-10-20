---
title: abfzip specification
# the schema for json examples that don't name one in $schema (used by the tests)
example_schema: https://meliza.org/spec:4/abfzip.json#
---

abfzip is a zip archive of Axon Binary Format ([ABF](https://swharden.com/pyabf/abf2-file-format/))
files from one intracellular recording, with a `metadata.json` member that
describes the recording.

-   Name: <https://meliza.org/spec:4/abfzip> (4/abfzip)
-   Schema (for `metadata.json`): <https://meliza.org/spec:4/abfzip.json>
-   Editor: Dan Meliza (dan at meliza.org)
-   Version: 1.0
-   Status: draft
-   MIME type: `application/vnd.meliza-org.abf+zip; version=1.0`

## 1 Goals

Intracellular recordings using Axon's pCLAMP software produce one file per recording epoch in Axon Binary Format. Each recording is defined by a protocol in the Axon software, and the same protocol may be repeated multiple times (e.g., to track physiological properties over time). Analysis workflows usually need to deal with all the recordings as a group, so the ABF files need to be kept together and organized. The goals are to:

-   Keep an experiment made up of several ABF files as one file, so it can be
    identified, hashed, copied, and archived as a unit
-   Keep the ABF files readable in place, without unpacking the archive
-   Carry the metadata that describes the recording (who recorded it, from which
    animal) in the file itself, so it can be checked and registered from the file
    rather than entered by hand
-   Record what each file is (such as the protocol it was recorded with) in the
    archive, so analysis doesn't depend on separate lists

## 2 The archive

An abfzip file is a [zip archive](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT).

-   It MUST contain a member named `metadata.json` at the top level, described in
    section 3.
-   It MUST contain at least one ABF file. A member is an ABF file if its name
    ends in `.abf` (in any case). Each ABF file MUST have a valid ABF header.
-   Members MAY be in subdirectories, with paths relative to the root of the
    archive, as they were in the recording's directory. Paths MUST NOT be
    absolute or contain `..`.
-   It MAY contain other members (such as notes or files written by the
    acquisition software alongside the ABF files). Readers MUST ignore members
    they don't use.
-   Members SHOULD be stored without compression, so that ABF files can be read
    in place (e.g. memory-mapped at the member's offset).

The order of members, their timestamps, and their permissions are not part of
the format. Programs that write abfzip files for an archive that identifies
resources by hash (such as [neurobank](https://github.com/melizalab/neurobank))
SHOULD write them in a fixed form, so that the same files always give the same
archive; neurobank provides a writer for this.

## 3 metadata.json

`metadata.json` is a JSON object with these keys:

-   `$schema` (REQUIRED): the URI of the schema the object follows,
    `https://meliza.org/spec:4/abfzip.json#` for all 1.x versions.
-   `version` (REQUIRED): the version of this specification the file follows, as
    `MAJOR.MINOR` (e.g. `"1.0"`). See section 4.
-   `metadata` (REQUIRED): an object describing the recording as a whole (3.1).
    It MAY be empty.
-   `catalog` (REQUIRED): an array of records describing individual members of
    the archive (3.2). It MAY be empty.

Later versions MAY add other keys at the top level. Readers MUST ignore keys
they don't know.

### 3.1 metadata

`metadata` is the recording's registry metadata: a program that deposits the
file registers it as it is (`experimenter` and `animal` as the registry's fields
for them, everything else as metadata). Its keys are:

-   `experimenter` (OPTIONAL): the person who made the recording, as a username
    in the registry where the recording is deposited.
-   `animal` (OPTIONAL): the animal the recording came from, as its identifier in
    the registry's animal database (in the Meliza lab, the bird's UUID in the
    colony database, in lowercase).
-   Any other keys (OPTIONAL): further metadata about the recording as a whole,
    as JSON values. Names SHOULD follow the lab's conventions for registry
    metadata, e.g. `protocol` for the name of the experimental protocol.

A key with no known value MUST be left out rather than set to `null`.

### 3.2 catalog

Each record in `catalog` describes one member of the archive, typically an ABF
file recorded in one epoch. Records let analysis code find, for example, which
files were recorded with which acquisition protocol without opening them or
keeping a separate list. Its keys are:

-   `path` (REQUIRED): the member's path in the archive, exactly as stored. It
    MUST name a member of the archive other than `metadata.json`, and no two
    records may have the same `path`.
-   `protocol` (OPTIONAL): the acquisition protocol the file was recorded with,
    as the lab names it (e.g. the name of the pCLAMP protocol). This is the
    protocol for this file, not the experimental protocol in `metadata`.
-   `start` (OPTIONAL): when recording of the file started, as an ISO 8601 date
    and time. A time without an offset from UTC is local time where the
    recording was made, as the ABF header records it.
-   Any other keys (OPTIONAL): further metadata about the member, as JSON values.

A key with no known value MUST be left out rather than set to `null`. Not every
member needs a record. Records SHOULD be in the order the files were recorded.
Readers MUST check that each `path` names a member and appears only once, which
the schema can't express.

Here is a minimal example:

~~~ json
{
  "$schema": "https://meliza.org/spec:4/abfzip.json#",
  "version": "1.0",
  "metadata": {},
  "catalog": []
}
~~~

Here is an example with the usual metadata and a representative catalog:

~~~ json
{
  "$schema": "https://meliza.org/spec:4/abfzip.json#",
  "version": "1.0",
  "metadata": {
    "experimenter": "anc4kj",
    "animal": "ca7cb913-0888-4861-8b3b-a954b16f42ce",
    "protocol": "intrinsic-properties",
    "cell": 5
  },
  "catalog": [
    {
      "path": "2016_05_26_0000.abf",
      "protocol": "IV_steps_500ms",
      "start": "2016-05-26T14:02:11"
    },
    {
      "path": "2016_05_26_0001.abf",
      "protocol": "ramp",
      "start": "2016-05-26T14:05:40"
    },
    {
      "path": "2016_05_26_0002.abf",
      "protocol": "IV_steps_500ms",
      "start": "2016-05-26T14:31:02",
      "note": "after bath application"
    }
  ]
}
~~~

## 4 Versions

`version` in `metadata.json` and the `version` parameter of the MIME type give
the version of this specification the file follows. Following the change
process below:

-   Readers MUST refuse a file with a major version they don't know.
-   Readers MAY read a file with a newer minor version than they know, ignoring
    keys they don't know.
-   A new major version gets a new schema URI for `$schema`; minor versions
    share the URI of their major version.

## Licence

Copyright (c) 2026 C Daniel Meliza.

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
