
install-dependency:
    poetry install

package:
    docker build --platform=linux/amd64 -t tree-sitter-tools-packager:latest .
    docker run --platform=linux/amd64 --rm -v $(PWD)/dist:/app/dist tree-sitter-tools-packager:latest