# Docs

This project uses [mkdocs](https://www.mkdocs.org/) for generating documentation. This can be installed with Python. Once mkdocs and mkdocs-material have been installed, the documentation may be served locally using the command:

```
$ mkdocs serve
```

A GitHub action workflow has been configured such that the docs are automatically created on merge to the `slaclab/nalms` `main` branch.

## Docker images
Significant simplifications might be made to these docker images (moving to more modern OS etc.); however, I've tried to replicate the RHEL 7 design requirement as closely as possible to demonstrate the installation outlined in the design document. 

## DockerHub deployment

At this current iteration, all Dockerhub images are hosted on my (Jacqueline Garrahan) personal account (jgarrahan). A Github action has been defined for the automatic build of images on pushes to the main slaclab/master branch. This ought to be changed to use a designated SLAC account and use proper tagged releases.

## Ongoing projects

An attempt has been made to document development needs using Github projects [here](https://github.com/slaclab/nalms/projects).