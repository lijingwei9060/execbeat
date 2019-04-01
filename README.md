# Execbeat

Welcome to Execbeat.

This beat can exec shell/python and so on ,get result like "k:v" format and send to elasticsearch.
What I wanna do is gathering information(hardware,os,runtime configuratons).

Ensure that this folder is at the following location:
`${GOPATH}/src/github.com/lijingwei9060/execbeat`

## Getting Started with Execbeat

### Requirements

* [Golang](https://golang.org/dl/) 1.7

### Init Project
To get running with Execbeat and also install the
dependencies, run the following command:

```
make setup
```

It will create a clean git history for each major step. Note that you can always rewrite the history if you wish before pushing your changes.

To push Execbeat in the git repository, run the following commands:

```
git remote set-url origin https://github.com/lijingwei9060/execbeat
git push origin master
```

For further development, check out the [beat developer guide](https://www.elastic.co/guide/en/beats/libbeat/current/new-beat.html).

### Build

To build the binary for Execbeat run the command below. This will generate a binary
in the same directory with the name execbeat.

Manually install magefile
$ go get github.com/magefile/mage

Change path in github.com/elastic/beats/libbeat/scripts/Makefile:15

Instead of:
ES_BEATS?=..## @community_beat Must be set to ./vendor/github.com/elastic/beats. It must always be a relative path.

Use:
ES_BEATS?=vendor/github.com/elastic/beats## @community_beat Must be set to ./vendor/github.com/elastic/beats. It must always be a relative path.

Make sure you leave no spaces between beats and ##. This was causing make setup to fail such as below.

Make sure the version of mage is below 1.8 , otherwise mage package will failed .

```
make
```


### Run

To run Execbeat with debugging output enabled, run:

```
./execbeat -c execbeat.yml -e -d "*"
```


### Test

To test Execbeat, run the following command:

```
make testsuite
```

alternatively:
```
make unit-tests
make system-tests
make integration-tests
make coverage-report
```

The test coverage is reported in the folder `./build/coverage/`

### Update

Each beat has a template for the mapping in elasticsearch and a documentation for the fields
which is automatically generated based on `fields.yml` by running the following command.

```
make update
```


### Cleanup

To clean  Execbeat source code, run the following commands:

```
make fmt
make simplify
```

To clean up the build directory and generated artifacts, run:

```
make clean
```


### Clone

To clone Execbeat from the git repository, run the following commands:

```
mkdir -p ${GOPATH}/src/github.com/lijingwei9060/execbeat
git clone https://github.com/lijingwei9060/execbeat ${GOPATH}/src/github.com/lijingwei9060/execbeat
```


For further development, check out the [beat developer guide](https://www.elastic.co/guide/en/beats/libbeat/current/new-beat.html).


## Packaging

The beat frameworks provides tools to crosscompile and package your beat for different platforms. This requires [docker](https://www.docker.com/) and vendoring as described above. To build packages of your beat, run the following command:

```
make release
```

This will fetch and create all images required for the build process. The whole process to finish can take several minutes.
