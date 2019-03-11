.PHONY: plugin release

VERSION ?= latest

plugin:
	@echo "Building Drone plugin (export VERSION=<version> if needed)"
	docker build . -t gumgum-docker.jfrog.io/drone-spotinst-esg-scaler:$(VERSION)

	@echo "\nDrone plugin successfully built! You can now execute it with:\n"
	@sed -n '/docker run/,/drone-spotinst-esg-scaler/p' README.md

release:
	@echo "Pushing Drone plugin to the registry"
	docker push gumgum-docker.jfrog.io/drone-spotinst-esg-scaler:$(VERSION)
