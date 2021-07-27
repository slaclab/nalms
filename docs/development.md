# Docs

This project uses [mkdocs](https://www.mkdocs.org/) for generating documentation. This can be installed with Python. Once mkdocs and mkdocs-material have been installed, the documentation may be served locally using the command:

```
$ mkdocs serve
```

A GitHub action workflow has been configured such that the docs are automatically created on merget to the `slaclab/nalms` `main` branch.



## DockerHub deployment

At this current iteration, all Dockerhub images are hosted on my (Jacqueline Garrahan) personal account. 

A Github action has been defined for the automatic build of images on pushes to the main slaclab/master branch. 

