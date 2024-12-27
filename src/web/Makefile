.DEFAULT_GOAL=help

tops ?=

help: # Show this help
	@egrep -h '\s#\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

tailwind: # Tailwindcss rebuild (watch) tops="--minify"
	./tailwindcss -i static/css/builder/tailwindcss-in.css -o static/css/tailwindcss.css --watch $(tops)

web-start: # starts web server
	fastapi dev server.py --host 0.0.0.0 --port 8000
