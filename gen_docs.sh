pdoc --html --html-dir docs chemical/__init__.py --overwrite
mv docs/__init__/index.html docs/index.html
rm -rf docs/__init__
