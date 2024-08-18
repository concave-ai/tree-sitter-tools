
.phony: install-dependency
install-dependency:
	poetry install --without prod

.phony: package
package:
	docker build --platform=linux/amd64 -t tree-sitter-tools-packager:latest .
	docker run --platform=linux/amd64 --rm -v $(PWD)/dist:/app/dist tree-sitter-tools-packager:latest

.phony: publish
publish:
	poetry publish -u __token__ -p $(PYPI_TOKEN)